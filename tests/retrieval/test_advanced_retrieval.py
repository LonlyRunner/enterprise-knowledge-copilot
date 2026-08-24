from types import SimpleNamespace

from app.rag.retrieval.metadata_filter import MetadataFilter


def test_metadata_filter():


    filter = MetadataFilter()


    result = filter.filter(
        [
            SimpleNamespace(
                metadata={
                    "department":
                    "finance"
                }
            )
        ],
        {
            "department":
            "finance"
        }
    )


    assert len(result)==1
