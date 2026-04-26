from app.dto import SearchDocumentChunksResult
from app.schemas import SearchItemResponseData


def serialize_search_result(result: SearchDocumentChunksResult) -> SearchItemResponseData:
    return SearchItemResponseData(
        filename=result.filename,
        page_number=result.page_number,
        content=result.content,
    )
