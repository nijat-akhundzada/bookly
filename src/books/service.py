from sqlmodel import Session, select, desc
from src.books.schemas import Book, BookCreateModel, BookUpdateModel
from datetime import datetime


class BookService:

    def get_all_books(self, session: Session):
        statement = select(Book).order_by(desc(Book.created_at))
        books = session.exec(statement).all()
        return books

    def get_user_books(self, user_id, session: Session):
        statement = select(Book).where(
            Book.user_id == user_id).order_by(desc(Book.created_at))
        books = session.exec(statement).all()
        return books

    def get_book(self, id: str,  session: Session):
        statement = select(Book).where(Book.id == id)
        book = session.exec(statement).first()
        return book

    def create_book(self, book_data: BookCreateModel, user_id: str, session: Session):
        book_data_dict = book_data.model_dump()
        new_book = Book(**book_data_dict)
        new_book.published_date = datetime.strptime(
            book_data_dict["published_date"], "%Y-%m-%d"
        )
        new_book.user_id = user_id

        session.add(new_book)
        session.commit()
        session.refresh(new_book)
        return new_book

    def update_book(self, id: str, updated_data: BookUpdateModel, session: Session):
        book = self.get_book(id, session)
        if book is not None:
            updated_data_dict = updated_data.model_dump()
            for k, v in updated_data_dict.items():
                setattr(book, k, v)
            session.commit()
            session.refresh(book)
            return book
        return None

    def delete_book(self, id: str,  session: Session):
        book = self.get_book(id, session)

        if book is not None:
            session.delete(book)
            session.commit()
            return {'msg': 'deleted'}
        return None
