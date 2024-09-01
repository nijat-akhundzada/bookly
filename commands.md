alembic init migrations
alembic revision --autogenerate -m 'message'
alembic upgrade head
python -c 'from secrets import token_hex; print(token_hex(16))'
