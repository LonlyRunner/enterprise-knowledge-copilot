class ParentRetriever:


    def __init__(
        self,
        document_repository,
    ):

        self.document_repository = (
            document_repository
        )


    async def expand(
        self,
        chunks,
    ):


        documents=[]


        for chunk in chunks:

            doc = await (
                self.document_repository
                .get(
                    chunk.parent_id
                )
            )


            documents.append(
                doc
            )


        return documents