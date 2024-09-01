from fastapi import APIRouter, Depends
from src.db.models import User
from src.db.main import get_session
from src.auth.dependencies import get_current_user
from sqlmodel import Session
from src.reviews.schemas import ReviewCreateModel
from src.reviews.service import ReviewService

review_service = ReviewService()
review_router = APIRouter()


@review_router.post('/book/{book_id}')
async def add_review_to_books(book_id: str, review_data: ReviewCreateModel, current_user: User = Depends(get_current_user), session: Session = Depends(get_session)):
    new_review = review_service.add_review_to_book(
        current_user.id, book_id, review_data, session
    )

    return new_review
