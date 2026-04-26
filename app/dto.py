from typing import NamedTuple


class DocumentChunk(NamedTuple):
    page_number: int
    content: str
    embedding: list[float]


class SearchDocumentChunksResult(NamedTuple):
    chunk_id: int
    document_id: int
    filename: str
    page_number: int
    content: str
    similarity: float
