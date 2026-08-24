class AdvancedRetriever:


    async def retrieve(
        self,
        question,
        filters=None,
    ):


        # 1 Query Rewrite

        rewritten = (
            await self.rewriter
            .rewrite(
                question
            )
        )


        # 2 Multi Query

        queries = (
            await self.expander
            .expand(
                rewritten
            )
        )


        # 3 Retrieval

        results=[]


        for q in queries:

            chunks = await (
                self.base_retriever
                .retrieve(q)
            )

            results.extend(
                chunks
            )


        # 4 Filter

        results = (
            self.metadata_filter
            .filter(
                results,
                filters
            )
        )


        return results