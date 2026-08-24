class MetadataFilter:


    def filter(
        self,
        chunks,
        filters:dict,
    ):


        if not filters:
            return chunks


        result=[]


        for chunk in chunks:

            matched=True


            for key,value in filters.items():

                if (
                    chunk.metadata
                    .get(key)
                    != value
                ):
                    matched=False


            if matched:
                result.append(chunk)


        return result