import logging
from src.db.models import Reviews
from src.auth.service import UserService
from src.books.service import BookService
from src.reviews.schemas import ReviewCreateModel
from sqlmodel import Session
from fastapi import HTTPException, status

book_service = BookService()
user_service = UserService()


class ReviewService:

    def add_review_to_book(self, user_email: str, book_id: str, review_data: ReviewCreateModel, session: Session):
        try:
            book = book_service.get_book(
                book_id,
                session
            )
            user = user_service.get_user_by_email(user_email, session)

            if not book:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail='Book not found')

            if not user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail='User not found')

            review_data_dict = review_data.model_dump()
            new_review = Reviews(**review_data_dict)
            new_review.user = user
            new_review.book = book
            session.add(new_review)
            session.commit()
            session.refresh(new_review)
            return new_review
        except Exception as e:
            logging.exception(e)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail='Oops ... Something went wrong')
