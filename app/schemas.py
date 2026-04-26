from pydantic import BaseModel


class SearchItemResponseData(BaseModel):
    filename: str
    page_number: int
    content: str


class SearchResponseData(BaseModel):
    search_query: str
    count: int
    rows: list[SearchItemResponseData]
