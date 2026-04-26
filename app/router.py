import uuid
import shutil
from fastapi import APIRouter, UploadFile, File, HTTPException, Query, Response, status
from fastembed import TextEmbedding
from pathlib import Path
import pymupdf

from app.database import create_document_with_chunks, search_document_chunks
from app.dto import DocumentChunk
from app.schemas import SearchResponseData
from app.serializers import serialize_search_result

router = APIRouter()

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

model = TextEmbedding()

@router.post("/upload")
def upload_file(file: UploadFile = File(...)):
    if file.filename is None:
        raise HTTPException(status_code=400, detail="filename missing")

    if file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="only pdf files are allowed")

    ext = Path(file.filename).suffix
    filename = f"{uuid.uuid4()}{ext}"

    file_path = UPLOAD_DIR / filename

    with file_path.open("wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    doc = pymupdf.open(file_path)
    chunks = []
    page_numbers = []
    for idx, page in enumerate(doc):
        page_number = idx + 1
        chunks.append(page.get_text())
        page_numbers.append(page_number)

    vectors = list(model.embed(chunks))

    document_chunks: list[DocumentChunk] = []
    for idx, chunk in enumerate(chunks):
        document_chunks.append(DocumentChunk(
            page_number=page_numbers[idx],
            content=chunk,
            embedding=vectors[idx].tolist(),
        ))

    create_document_with_chunks(filename, document_chunks)

    return Response(status_code=status.HTTP_200_OK)


@router.get("/search")
def search(search_query: str = Query(..., min_length=1)) -> SearchResponseData:
    search_query_embedding = next(model.embed([search_query])).tolist()

    search_result = search_document_chunks(search_query_embedding=search_query_embedding)

    return SearchResponseData(
        search_query=search_query,
        count=len(search_result),
        rows=[serialize_search_result(item) for item in search_result],
    )

