from fastapi import APIRouter
from fastapi.responses import ORJSONResponse


module_router = APIRouter(
    prefix="/api/v1/module",
    tags=["module"],
    responses={404: {"description": "Not found"}},
)

sms_router = APIRouter(
    prefix="/api/v1/sms",
    tags=["sms"],
    responses={404: {"description": "Not found"}},
)

schedule_router = APIRouter(
    prefix="/api/v1/schedule",
    tags=["schedule"],
    responses={404: {"description": "Not found"}},
)