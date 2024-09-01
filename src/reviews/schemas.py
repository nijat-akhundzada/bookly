import uuid
from pydantic import BaseModel, Field
from datetime import datetime


class ReviewModel(BaseModel):
    id: uuid.UUID
    rating: int = Field(lt=5)
    review_text: str
    user_id: uuid.UUID | None
    book_id: uuid.UUID | None
    created_at: datetime
    updated_at: datetime


class ReviewCreateModel(BaseModel):
    rating: int = Field(lt=5)
    review_text: str
