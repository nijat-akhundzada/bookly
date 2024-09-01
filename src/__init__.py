from fastapi import FastAPI, status
from src.books.routes import book_router
from src.auth.routes import auth_router
from src.reviews.routes import review_router
from src.db.main import lifespan
from src.errors import register_all_errors
from src.middleware import register_middleware

version = 'v1'


app = FastAPI(
    title='Bookly',
    description='A REST API for a book review web service',
    version=version,
    lifespan=lifespan
)

register_all_errors(app)

register_middleware(app)

app.include_router(auth_router, prefix=f'/api/{version}/auth', tags=['auth'])
app.include_router(book_router, prefix=f'/api/{version}/books', tags=['books'])
app.include_router(
    review_router, prefix=f'/api/{version}/reviews', tags=['reviews'])
