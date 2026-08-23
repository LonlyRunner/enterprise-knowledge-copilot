import uuid
from pathlib import Path

from sqlalchemy.ext.asyncio import AsyncSession

from app.rag.embedding import EmbeddingClient
from app.rag.loaders.factory import (
    create_document_loader,
)
from app.rag.splitters.recursive import (
    RecursiveTextSplitter,
)
from app.repositories.document import (
    DocumentRepository,
)
from app.repositories.document_chunk import (
    DocumentChunkRepository,
)


class DocumentIndexService:

    def __init__(
        self,
        session: AsyncSession,
    ):
        self.session = session

        self.document_repository = (
            DocumentRepository(
                session
            )
        )

        self.chunk_repository = (
            DocumentChunkRepository(
                session
            )
        )

        self.embedding_client = (
            EmbeddingClient()
        )

        self.splitter = (
            RecursiveTextSplitter(
                chunk_size=400,
                chunk_overlap=100,
            )
        )

    async def index(
            self,
            *,
            document_id: uuid.UUID,
            retry_count: int = 0,
    ) -> int:

        document = (
            await self.document_repository.get_by_id(
                document_id
            )
        )

        if document is None:
            raise ValueError(
                "Document not found"
            )

        if not document.source_path:
            raise ValueError(
                "Document source path is empty"
            )

        path = Path(
            document.source_path
        )

        if not path.exists():
            raise FileNotFoundError(
                f"Document file not found: {path}"
            )

        await self.document_repository.mark_processing(
            document,
            retry_count=retry_count,
        )

        await self.session.commit()

        try:

            loader = (
                create_document_loader(
                    str(path)
                )
            )

            parsed_document = (
                loader.load(
                    str(path)
                )
            )

            chunks = (
                self.splitter.split_document(
                    parsed_document
                )
            )

            if not chunks:
                raise ValueError(
                    "No document chunks generated"
                )

            texts = [
                chunk.content
                for chunk in chunks
            ]

            embeddings = (
                await self.embedding_client.embed_batch(
                    texts
                )
            )

            if (
                    len(embeddings)
                    != len(chunks)
            ):
                raise ValueError(
                    "Embedding count does not match chunk count"
                )

            #
            # 真正修改旧索引，从这里才开始。
            #

            await self.chunk_repository.delete_by_document(
                document.id
            )

            chunk_data = [
                {
                    "chunk_index": index,
                    "content": (
                        chunk.content
                    ),
                    "embedding": embedding,
                }
                for index, (
                    chunk,
                    embedding,
                )
                in enumerate(
                    zip(
                        chunks,
                        embeddings,
                    )
                )
            ]

            await self.chunk_repository.create_many(
                document_id=document.id,
                chunks=chunk_data,
            )

            await self.document_repository.mark_completed(
                document
            )

            await self.session.commit()

            return len(chunks)

        except Exception:

            await self.session.rollback()

            raise

        finally:

            await self.embedding_client.close()