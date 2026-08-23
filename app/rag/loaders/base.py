from abc import ABC, abstractmethod

from app.rag.models import Document


class BaseDocumentLoader(ABC):

    @abstractmethod
    def load(
        self,
        file_path: str,
    ) -> Document:
        pass