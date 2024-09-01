import redis.asyncio as redis
from src.config import Config

JTI_EXPIRY = 3600

token_blocklist = redis.from_url(Config.REDIS_URL)


async def add_jti_to_blocklist(jti: str) -> None:
    await token_blocklist.set(
        name=jti,
        value='',
        ex=JTI_EXPIRY
    )


async def token_in_blocklist(jti: str) -> bool:
    jti_value = await token_blocklist.get(jti)
    return jti_value is not None