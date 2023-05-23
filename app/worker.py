import asyncio

from arq import create_pool, run_worker
from arq.connections import RedisSettings

from .database.mongodb import close_db, get_db
from .search_engine.elasticsearch import close_es, get_es
from .settings import get_settings
from .tasks.elasticsearch import es_create_index, es_delete_document, es_index_document, es_update_document

settings = get_settings()

redis_settings = RedisSettings(host=settings.redis_host, port=settings.redis_port)
redis_pool = None
redis_lock = asyncio.Lock()


async def get_redis():
    global redis_pool
    if redis_pool is None:
        async with redis_lock:  # to avoid a race condition when creating a connection pool
            if redis_pool is None:
                redis_pool = await create_pool(redis_settings)
    return redis_pool


async def close_redis():
    global redis_pool
    if redis_pool is not None:
        await redis_pool.close()
        redis_pool = None


async def startup(ctx):
    ctx["db"] = await get_db()
    ctx["es"] = await get_es()
    ctx["redis"] = await get_redis()


async def shutdown(ctx):
    await close_db()
    await close_es()
    await close_redis()


class WorkerSettings:
    functions = [es_create_index, es_index_document, es_update_document, es_delete_document]
    redis_settings = redis_settings
    on_startup = startup
    on_shutdown = shutdown


if __name__ == "__main__":
    run_worker(WorkerSettings)
