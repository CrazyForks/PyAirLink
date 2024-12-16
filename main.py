import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, status, Request
from pydantic import ValidationError
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore

from router.route import module_router, sms_router
from services.utils.config_parser import config

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')
logger = logging.getLogger("PyAirLink")

jobstores = {
    'default': SQLAlchemyJobStore(url=config.sqlite_url())
}

scheduler = AsyncIOScheduler(jobstores=jobstores)


@asynccontextmanager
async def lifespan(app: FastAPI):
    scheduler.start()
    try:
        yield
    finally:
        if scheduler.running:
            scheduler.shutdown()


app = FastAPI(lifespan=lifespan, title='PyAirLink API', version='0.0.1')
app.include_router(module_router)
app.include_router(sms_router)


if __name__ == '__main__':
    pass