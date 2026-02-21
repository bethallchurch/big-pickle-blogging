from fastapi import APIRouter, HTTPException, Header
from jose import jwt, JWTError
from slugify import slugify
from database import get_conn, release_conn
import os

router = APIRouter(prefix="/api/articles")
SECRET = os.environ.get("JWT_SECRET")

def get_user_id(authorization: str):
    try:
        token = authorization.split(" ")[1]
        payload = jwt.decode(token, SECRET, algorithms=["HS256"])
        return int(payload["sub"])
    except (JWTError, IndexError):
        raise HTTPException(401, "Invalid token")

@router.get("")
def list_articles(page: int = 1):
    conn = get_conn()
    try:
        offset = (page - 1) * 20
        with conn.cursor() as cur:
            cur.execute(
                "SELECT id, title, created_at, user_id FROM articles "
                "ORDER BY created_at DESC LIMIT 20 OFFSET %s", (offset,)
            )
            rows = cur.fetchall()
            return [{"id": r[0], "title": r[1], "created_at": str(r[2]), "user_id": r[3]} for r in rows]
    finally:
        release_conn(conn)

@router.get("/{article_id}")
def get_article(article_id: int):
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT id, title, body, user_id, created_at FROM articles WHERE id = %s",
                (article_id,)
            )
            row = cur.fetchone()
            if not row:
                raise HTTPException(404, "Not found")
            return {"id": row[0], "title": row[1], "body": row[2], "user_id": row[3], "created_at": str(row[4])}
    finally:
        release_conn(conn)

@router.post("")
def create_article(title: str, body: str, authorization: str = Header(None)):
    user_id = get_user_id(authorization)
    slug = slugify(title)
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO articles (title, slug, body, user_id) VALUES (%s, %s, %s, %s) RETURNING id",
                (title, slug, body, user_id)
            )
            article_id = cur.fetchone()[0]
            conn.commit()
            return {"article_id": article_id}
    except Exception as e:
        conn.rollback()
        raise HTTPException(400, str(e))
    finally:
        release_conn(conn)

@router.put("/{article_id}")
def update_article(article_id: int, title: str, body: str, authorization: str = Header(None)):
    user_id = get_user_id(authorization)
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "UPDATE articles SET title=%s, body=%s WHERE id=%s AND user_id=%s RETURNING id",
                (title, body, article_id, user_id)
            )
            if not cur.fetchone():
                raise HTTPException(403, "Not authorized or not found")
            conn.commit()
            return {"updated": True}
    except HTTPException:
        raise
    except Exception as e:
        conn.rollback()
        raise HTTPException(400, str(e))
    finally:
        release_conn(conn)

@router.delete("/{article_id}")
def delete_article(article_id: int, title: str, authorization: str = Header(None)):
    user_id = get_user_id(authorization)
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "DELETE FROM articles WHERE id=%s AND user_id=%s RETURNING id",
                (article_id, user_id)
            )
            if not cur.fetchone():
                raise HTTPException(403, "Not authorized or not found")
            conn.commit()
            return {"deleted": True}
    except HTTPException:
        raise
    except Exception as e:
        conn.rollback()
        raise HTTPException(400, str(e))
    finally:
        release_conn(conn)

        