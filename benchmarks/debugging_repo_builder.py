import os
from pathlib import Path

def setup_buggy_repository(workspace: Path):
    """Constructs an unfamiliar Python Book Management REST API codebase with an intentional defect in pagination."""
    workspace = Path(workspace).resolve()
    
    files = {
        "app/__init__.py": "# App package initialization\n",
        
        "app/config.py": """import os

class Config:
    DB_NAME = os.getenv("DATABASE_NAME", "books.db")
    DEBUG = os.getenv("DEBUG", "False").lower() in ("true", "1")
    PAGE_SIZE_DEFAULT = 10
""",

        "app/database/__init__.py": "# Database package\n",
        
        "app/database/connection.py": """import sqlite3
from app.config import Config

def get_db_connection():
    conn = sqlite3.connect(Config.DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn
""",

        "app/database/init_db.py": """from app.database.connection import get_db_connection

def initialize_database():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(\"\"\"
        CREATE TABLE IF NOT EXISTS books (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            author TEXT NOT NULL,
            genre TEXT NOT NULL,
            price REAL NOT NULL CHECK(price >= 0),
            published_year INTEGER NOT NULL
        )
    \"\"\")
    conn.commit()
    conn.close()
""",

        "app/models/__init__.py": "# Models package\n",

        "app/models/book_model.py": """class BookModel:
    def __init__(self, book_id: int, title: str, author: str, genre: str, price: float, published_year: int):
        self.id = book_id
        self.title = title
        self.author = author
        self.genre = genre
        self.price = price
        self.published_year = published_year

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "author": self.author,
            "genre": self.genre,
            "price": self.price,
            "published_year": self.published_year
        }
""",

        "app/schemas/__init__.py": "# Schemas package\n",

        "app/schemas/book_schema.py": """from pydantic import BaseModel, Field
from typing import Optional

class BookCreateSchema(BaseModel):
    title: str = Field(..., min_length=1)
    author: str = Field(..., min_length=1)
    genre: str = Field(..., min_length=1)
    price: float = Field(..., ge=0.0)
    published_year: int = Field(..., ge=1000, le=2100)

class BookUpdateSchema(BaseModel):
    title: Optional[str] = Field(None, min_length=1)
    author: Optional[str] = Field(None, min_length=1)
    genre: Optional[str] = Field(None, min_length=1)
    price: Optional[float] = Field(None, ge=0.0)
    published_year: Optional[int] = Field(None, ge=1000, le=2100)

class BookResponseSchema(BaseModel):
    id: int
    title: str
    author: str
    genre: str
    price: float
    published_year: int
""",

        "app/services/__init__.py": "# Services package\n",

        "app/services/book_service.py": """from app.database.connection import get_db_connection
from app.models.book_model import BookModel
from typing import List, Optional

class BookService:
    @staticmethod
    def create_book(title: str, author: str, genre: str, price: float, published_year: int) -> BookModel:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO books (title, author, genre, price, published_year) VALUES (?, ?, ?, ?, ?)",
            (title, author, genre, price, published_year)
        )
        conn.commit()
        book_id = cursor.lastrowid
        conn.close()
        return BookModel(book_id, title, author, genre, price, published_year)

    @staticmethod
    def get_all_books(page: int = 1, page_size: int = 10) -> List[BookModel]:
        # DEFECT: Incorrect offset calculation (page * page_size skips page 1 items)
        offset = page * page_size
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, title, author, genre, price, published_year FROM books LIMIT ? OFFSET ?", (page_size, offset))
        rows = cursor.fetchall()
        conn.close()
        return [BookModel(r["id"], r["title"], r["author"], r["genre"], r["price"], r["published_year"]) for r in rows]

    @staticmethod
    def get_book_by_id(book_id: int) -> Optional[BookModel]:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, title, author, genre, price, published_year FROM books WHERE id = ?", (book_id,))
        row = cursor.fetchone()
        conn.close()
        if row:
            return BookModel(row["id"], row["title"], row["author"], row["genre"], row["price"], row["published_year"])
        return None

    @staticmethod
    def update_book(book_id: int, title: Optional[str] = None, author: Optional[str] = None, genre: Optional[str] = None, price: Optional[float] = None, published_year: Optional[int] = None) -> Optional[BookModel]:
        book = BookService.get_book_by_id(book_id)
        if not book:
            return None
        new_title = title if title is not None else book.title
        new_author = author if author is not None else book.author
        new_genre = genre if genre is not None else book.genre
        new_price = price if price is not None else book.price
        new_year = published_year if published_year is not None else book.published_year

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE books SET title = ?, author = ?, genre = ?, price = ?, published_year = ? WHERE id = ?",
            (new_title, new_author, new_genre, new_price, new_year, book_id)
        )
        conn.commit()
        conn.close()
        return BookModel(book_id, new_title, new_author, new_genre, new_price, new_year)

    @staticmethod
    def delete_book(book_id: int) -> bool:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM books WHERE id = ?", (book_id,))
        if not cursor.fetchone():
            conn.close()
            return False
        cursor.execute("DELETE FROM books WHERE id = ?", (book_id,))
        conn.commit()
        conn.close()
        return True
""",

        "app/api/__init__.py": "# API package\n",

        "app/api/book_router.py": """from fastapi import APIRouter, HTTPException, status, Query
from typing import List
from app.schemas.book_schema import BookCreateSchema, BookUpdateSchema, BookResponseSchema
from app.services.book_service import BookService

router = APIRouter(prefix="/api/v1/books", tags=["Books"])

@router.post("", response_model=BookResponseSchema, status_code=status.HTTP_201_CREATED)
def create_book_endpoint(book_in: BookCreateSchema):
    book = BookService.create_book(
        title=book_in.title,
        author=book_in.author,
        genre=book_in.genre,
        price=book_in.price,
        published_year=book_in.published_year
    )
    return book.to_dict()

@router.get("", response_model=List[BookResponseSchema])
def list_books_endpoint(page: int = Query(1, ge=1), page_size: int = Query(10, ge=1, le=100)):
    books = BookService.get_all_books(page=page, page_size=page_size)
    return [b.to_dict() for b in books]

@router.get("/{book_id}", response_model=BookResponseSchema)
def get_book_endpoint(book_id: int):
    book = BookService.get_book_by_id(book_id)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    return book.to_dict()

@router.put("/{book_id}", response_model=BookResponseSchema)
def update_book_endpoint(book_id: int, book_in: BookUpdateSchema):
    book = BookService.update_book(
        book_id=book_id,
        title=book_in.title,
        author=book_in.author,
        genre=book_in.genre,
        price=book_in.price,
        published_year=book_in.published_year
    )
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    return book.to_dict()

@router.delete("/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_book_endpoint(book_id: int):
    success = BookService.delete_book(book_id)
    if not success:
        raise HTTPException(status_code=404, detail="Book not found")
    return None
""",

        "app/main.py": """from fastapi import FastAPI
from app.database.init_db import initialize_database
from app.api.book_router import router as book_router

app = FastAPI(title="Book Management REST API")
initialize_database()

app.include_router(book_router)

@app.get("/health")
def health_check():
    return {"status": "healthy"}
""",

        "tests/__init__.py": "# Tests package\n",

        "tests/test_api.py": """import unittest
from fastapi.testclient import TestClient
from app.main import app
from app.database.init_db import initialize_database

class TestBookAPIEndpoints(unittest.TestCase):
    def setUp(self):
        initialize_database()
        self.client = TestClient(app)

    def test_crud_flow(self):
        payload = {"title": "Dune", "author": "Frank Herbert", "genre": "Sci-Fi", "price": 15.99, "published_year": 1965}
        res1 = self.client.post("/api/v1/books", json=payload)
        self.assertEqual(res1.status_code, 201)
        data1 = res1.json()
        book_id = data1["id"]
        self.assertEqual(data1["title"], "Dune")

        res2 = self.client.get(f"/api/v1/books/{book_id}")
        self.assertEqual(res2.status_code, 200)

        res3 = self.client.get("/api/v1/books")
        self.assertEqual(res3.status_code, 200)

        res4 = self.client.put(f"/api/v1/books/{book_id}", json={"price": 18.99})
        self.assertEqual(res4.status_code, 200)

        res5 = self.client.delete(f"/api/v1/books/{book_id}")
        self.assertEqual(res5.status_code, 204)
""",

        "tests/test_pagination.py": """import unittest
from fastapi.testclient import TestClient
from app.main import app
from app.database.init_db import initialize_database
from app.services.book_service import BookService

class TestBookPagination(unittest.TestCase):
    def setUp(self):
        initialize_database()
        self.client = TestClient(app)
        for i in range(15):
            BookService.create_book(f"Book {i}", "Author", "Genre", 10.0 + i, 2000 + i)

    def test_page_one_returns_first_item(self):
        res = self.client.get("/api/v1/books?page=1&page_size=5")
        self.assertEqual(res.status_code, 200)
        items = res.json()
        # Page 1 must return 5 items starting with Book 0
        self.assertEqual(len(items), 5)
        self.assertEqual(items[0]["title"], "Book 0")
"""
    }

    for path_str, content in files.items():
        file_path = workspace / path_str
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_text(content, encoding="utf-8")

    return workspace
