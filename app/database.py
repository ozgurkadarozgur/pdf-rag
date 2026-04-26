import time
from pathlib import Path

import psycopg

from app.dto import DocumentChunk, SearchDocumentChunksResult

DB_DSN = "host=db port=5432 dbname=search user=app password=app"

DB_CONNECTION_RETRY_COUNT = 5

def init_db() -> None:
    sql = Path("app/init.sql").read_text(encoding="utf-8")

    for _ in range(DB_CONNECTION_RETRY_COUNT):
        try:
            with psycopg.connect(DB_DSN, autocommit=True) as conn:
                with conn.cursor() as cur:
                    cur.execute(sql)
        except Exception as exc:
            print("database connection failed. exc:", exc)
            time.sleep(1)
        else:
            break

    print("database initialized successfully.")

def create_document_with_chunks(filename: str, chunks: list[DocumentChunk]) -> int:
    with psycopg.connect(DB_DSN) as conn:
        with conn.transaction():
            document_id = _create_document(
                filename=filename,
                conn=conn,
            )

            for chunk in chunks:
                _create_document_chunk(
                    document_id=document_id,
                    chunk=chunk,
                    conn=conn,
                )

            return document_id

def _create_document(
    filename: str,
    conn: psycopg.Connection,
) -> int:
    with conn.cursor() as cur:
        cur.execute(
            """
            INSERT INTO documents (filename)
            VALUES (%s)
            RETURNING id
            """,
            (filename,),
        )
        return cur.fetchone()[0]

def _create_document_chunk(
    document_id: int,
    chunk: DocumentChunk,
    conn: psycopg.Connection,
) -> int:
    with conn.cursor() as cur:
        cur.execute(
            """
            INSERT INTO document_chunks (
                document_id,
                page_number,
                content,
                embedding
            )
            VALUES (%s, %s, %s, %s)
            RETURNING id
            """,
            (
                document_id,
                chunk.page_number,
                chunk.content,
                chunk.embedding,
            ),
        )
        return cur.fetchone()[0]

def search_document_chunks(search_query_embedding: list[float], limit: int = 5, min_similarity: float = 0.65) -> list[SearchDocumentChunksResult]:
    with psycopg.connect(DB_DSN) as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT
                    dc.id,
                    dc.document_id,
                    d.filename,
                    dc.page_number,
                    dc.content,
                    1 - (dc.embedding <=> %s::vector) AS similarity
                FROM document_chunks dc
                INNER JOIN documents d
                    ON d.id = dc.document_id
                WHERE 1 - (dc.embedding <=> %s::vector) >= %s
                ORDER BY similarity DESC
                LIMIT %s
                """,
                (
                    search_query_embedding,
                    search_query_embedding,
                    min_similarity,
                    limit,
                ),
            )

            rows = cur.fetchall()

            results: list[SearchDocumentChunksResult] = []
            for row in rows:
                results.append(
                    SearchDocumentChunksResult(
                        chunk_id=row[0],
                        document_id=row[1],
                        filename=row[2],
                        page_number=row[3],
                        content=row[4],
                        similarity=round(float(row[5]), 4),
                    )
                )

            return results