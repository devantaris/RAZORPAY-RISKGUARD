import logging
from typing import Optional
import redis.asyncio as aioredis
import redis
from app.core.config import settings

logger = logging.getLogger('riskguard.redis')

_async_redis_client: Optional[aioredis.Redis] = None


async def get_redis() -> aioredis.Redis:
    global _async_redis_client
    if _async_redis_client is None:
        try:
            _async_redis_client = aioredis.from_url(
                settings.REDIS_URL,
                decode_responses=True,
                socket_connect_timeout=2.0
            )
            await _async_redis_client.ping()
        except Exception as e:
            logger.warning(f'Could not connect to Redis at {settings.REDIS_URL}: {e}. Velocity caching will use fallback.')
    return _async_redis_client


def get_sync_redis() -> Optional[redis.Redis]:
    try:
        r = redis.from_url(settings.REDIS_URL, decode_responses=True, socket_connect_timeout=2.0)
        r.ping()
        return r
    except Exception as e:
        logger.warning(f'Could not connect sync Redis at {settings.REDIS_URL}: {e}')
        return None
