from fastapi import APIRouter, Depends, status, HTTPException
from src.books.service import BookService
from sqlmodel import Session
from src.db.main import get_session
from src.db.models import Book
from src.books.schemas import BookUpdateModel, BookCreateModel, BookDetailModel
from src.auth.dependencies import AccessTokenBearer
from src.auth.dependencies import RoleChecker
from src.errors import BookNotFound

book_router = APIRouter()
book_service = BookService()
access_token_bearer = AccessTokenBearer()
role_checker = RoleChecker(['admin', 'user'])


@book_router.get('/')
async def get_all_books(session: Session = Depends(get_session), token_details: dict = Depends(access_token_bearer), _: bool = Depends(role_checker)) -> list[Book]:
    return book_service.get_all_books(session)


@book_router.get('/user/{user_id}')
async def get_user_book_submission(user_id: str, session: Session = Depends(get_session), token_details: dict = Depends(access_token_bearer), _: bool = Depends(role_checker)) -> list[Book]:
    return book_service.get_user_books(user_id, session)


@book_router.post('/', status_code=status.HTTP_201_CREATED)
async def create_book(book_data: BookCreateModel, session: Session = Depends(get_session), token_details: dict = Depends(access_token_bearer), _: bool = Depends(role_checker)):
    user_id = token_details.get('user')['user_id']
    return book_service.create_book(book_data, user_id, session)


@book_router.get('/{id}')
async def get_book(id: str, session: Session = Depends(get_session), token_details: dict = Depends(access_token_bearer), _: bool = Depends(role_checker)) -> BookDetailModel:
    book = book_service.get_book(id, session)
    if book is not None:
        return book
    raise BookNotFound()


@book_router.patch('/{id}')
async def update_book(id: str, updated_data: BookUpdateModel, session: Session = Depends(get_session), token_details: dict = Depends(access_token_bearer), _: bool = Depends(role_checker)):
    book = book_service.update_book(id, updated_data, session)
    if book is not None:
        return book
    raise BookNotFound()


@book_router.delete('/{id}')
async def delete_book(id: str, session: Session = Depends(get_session), token_details: dict = Depends(access_token_bearer), _: bool = Depends(role_checker)):
    response = book_service.delete_book(id, session)
    if response is not None:
        return response
    raise BookNotFound()
