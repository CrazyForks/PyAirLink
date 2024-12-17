import logging
import threading
from contextlib import asynccontextmanager

from fastapi import FastAPI, status
from fastapi.responses import ORJSONResponse
from pydantic import ValidationError

from router.route import module_router, sms_router, schedule_router
from services import scheduler
from schemas.schemas import ErrorModel, ErrorDetail
from services.initialize import sms_listener, initialize_module

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')
logger = logging.getLogger("PyAirLink")


@asynccontextmanager
async def lifespan(app: FastAPI):
    scheduler.start()
    initialize_module()
    stop_event = threading.Event()
    sms_thread = threading.Thread(target=sms_listener, args=(stop_event,), daemon=True)
    sms_thread.start()
    logger.info("sms_listener 已启动")
    try:
        yield
    finally:
        if scheduler.running:
            scheduler.shutdown()
        stop_event.set()
        sms_thread.join()
        logger.info("sms_listener 已停止")


app = FastAPI(lifespan=lifespan, title='PyAirLink API', version='0.0.1')
app.include_router(module_router)
app.include_router(sms_router)
app.include_router(schedule_router)


@app.exception_handler(ValidationError)
async def validation_exception_handler(exc: ValidationError):
    error_response = ErrorModel(detail=[ErrorDetail(loc=err.get('loc'), msg=err.get('msg'), type=err.get('type')) for err in exc.errors()])
    return ORJSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=error_response.model_dump()
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=10103, reload=False)