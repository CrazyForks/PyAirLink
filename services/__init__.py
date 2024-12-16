from zoneinfo import ZoneInfo

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from services.utils.config_parser import config

jobstores = {
    'default': SQLAlchemyJobStore(url=config.sqlite_url())
}

scheduler = AsyncIOScheduler(timezone=ZoneInfo("Asia/Shanghai"), jobstores=jobstores)
