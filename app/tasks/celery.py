from celery import Celery


celery=Celery(
    "worker"
)


@celery.task
def index_document(
    document_id
):

    print(
        "embedding..."
    )
