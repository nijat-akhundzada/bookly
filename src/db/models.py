import uuid
from datetime import date, datetime
from typing import List, Optional

import sqlalchemy.dialects.postgresql as pg
from sqlmodel import Column, Field, Relationship, SQLModel


class User(SQLModel, table=True):
    __tablename__ = "users"
    id: uuid.UUID = Field(
        sa_column=Column(pg.UUID, nullable=False,
                         primary_key=True, default=uuid.uuid4)
    )
    username: str
    email: str
    first_name: str
    last_name: str
    role: str = Field(
        sa_column=Column(pg.VARCHAR, nullable=False, server_default="user")
    )
    is_verified: bool = Field(default=False)
    password_hash: str = Field(
        sa_column=Column(pg.VARCHAR, nullable=False), exclude=True
    )
    created_at: datetime = Field(sa_column=Column(
        pg.TIMESTAMP, default=datetime.now))
    update_at: datetime = Field(sa_column=Column(
        pg.TIMESTAMP, default=datetime.now))
    books: List['Book'] = Relationship(
        back_populates="user", sa_relationship_kwargs={"lazy": "selectin"}
    )
    reviews: List['Reviews'] = Relationship(
        back_populates="user", sa_relationship_kwargs={"lazy": "selectin"}
    )

    def __repr__(self):
        return f"<User {self.username}>"


class Book(SQLModel, table=True):
    __tablename__ = "books"
    id: uuid.UUID = Field(
        sa_column=Column(pg.UUID, nullable=False,
                         primary_key=True, default=uuid.uuid4)
    )
    title: str
    author: str
    publisher: str
    published_date: date
    page_count: int
    language: str
    user_id: Optional[uuid.UUID] = Field(
        default=None, foreign_key="users.id")
    created_at: datetime = Field(sa_column=Column(
        pg.TIMESTAMP, default=datetime.now))
    update_at: datetime = Field(sa_column=Column(
        pg.TIMESTAMP, default=datetime.now))
    user: Optional[User] = Relationship(back_populates="books")
    reviews: List['Reviews'] = Relationship(
        back_populates="book", sa_relationship_kwargs={"lazy": "selectin"}
    )

    def __repr__(self):
        return f"<Book {self.title}>"


class Reviews(SQLModel, table=True):
    __tablename__ = "reviews"
    id: uuid.UUID = Field(
        sa_column=Column(pg.UUID, nullable=False,
                         primary_key=True, default=uuid.uuid4)
    )
    rating: int = Field(lt=5)
    review_text: str
    user_id: Optional[uuid.UUID] = Field(
        default=None, foreign_key="users.id")
    book_id: Optional[uuid.UUID] = Field(
        default=None, foreign_key="books.id")
    created_at: datetime = Field(sa_column=Column(
        pg.TIMESTAMP, default=datetime.now))
    update_at: datetime = Field(sa_column=Column(
        pg.TIMESTAMP, default=datetime.now))
    user: Optional[User] = Relationship(back_populates="reviews")
    book: Optional[Book] = Relationship(back_populates="reviews")

    def __repr__(self):
        return f"<Review for {self.book_id}> by user {self.user_id}"
