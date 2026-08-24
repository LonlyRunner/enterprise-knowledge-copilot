from abc import ABC, abstractmethod

from app.rag.models import Document


class BaseDocumentLoader(ABC):

    @abstractmethod
    def load(
        self,
        file_path: str,
        *,
        document_id: str | None = None,
        tenant_id: str = "default",
    ) -> Document:
        pass
