from typing import List

from fastapi import APIRouter, Depends, Query
from fastapi.responses import ORJSONResponse

from services import scheduler
from schemas import schemas
from services.initialize import send_at_command, send_sms
from services.utils.commands import at_commands

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


@module_router.post("/command/base", response_model=schemas.CommandResponse, summary='执行任意AT命令',
                   description=
"""
需要自己拼接所有参数
"""
                   )
async def command_base(params: schemas.CommandBaseRequest = Depends()):
    response = send_at_command(at_commands.base(params.command), keywords=params.keyword, timeout=params.timeout)
    return {'status': 'success' if response else 'failure', 'content': response}


@module_router.post("/command/restart", response_model=schemas.CommandResponse, summary='重启模块',
                   description=
"""
"""
                   )
async def command_reset(params: schemas.Command = Depends()):
    response = send_at_command(at_commands.reset(), keywords=params.keyword, timeout=params.timeout)
    return {'status': 'success' if response else 'failure', 'content': response}


@sms_router.post("/sms/send", response_model=schemas.CommandResponse, summary='发送短信',
                   description=
"""
尚未支持长短信，不要大于70个字符
"""
                   )
async def immediately_send_sms(params: schemas.SendSMSRequest = Depends()):
    response = send_sms(f'+{params.country}{params.number}', text=params.message)
    return {'status': 'success' if response else 'failure', 'content': response}


@schedule_router.get("/schedule/list", response_model=List[schemas.ListScheduleJob], summary='查看定时任务',
                   description=
"""
查看所有执行中的定时任务
"""
                   )
async def list_schedule():
    jobs = scheduler.get_jobs()
    if jobs:
        return [{'id': job.id, 'next_run_time': job.next_run_time, 'trigger': job.trigger, 'func': job.func} for job in jobs]
    return ORJSONResponse(status_code=404, content={"status": "fail", "message": f"no jobs in schedule"})


@schedule_router.delete("/schedule/del", response_model=schemas.CommandResponse, summary='删除定时任务',
                   description=
"""
删除定时任务
"""
                   )
async def del_schedule(job_id: str = Query()):
    job = scheduler.get_job(job_id=job_id)
    if job:
        scheduler.remove_job(job_id=job_id)
        return {'status': 'success', 'content': job_id}
    return 404


@schedule_router.post("/schedule/add/sms", response_model=schemas.CommandResponse, summary='添加定时发短信任务',
                   description=
"""
"""
                   )
async def add_sms_schedule(params: schemas.ScheduleSendSMSRequest = Depends()):
    try:
        job = scheduler.add_job(func=send_sms, args=(f'+{params.country}{params.number}', params.message,),
                                trigger='interval', seconds=params.seconds, jobstore='default')
        return {'status': 'success', 'content': job.id}
    except Exception as e:
        return ORJSONResponse(status_code=400, content={"status": "error", "message": f"An error occurred: {str(e)}"})


@schedule_router.post("/schedule/add/restart", response_model=schemas.CommandResponse, summary='添加定时重启任务',
                   description=
"""
"""
                   )
async def add_restart_schedule(params: schemas.ScheduleSendSMSRequest = Depends()):
    try:
        job = scheduler.add_job(func=send_at_command, args=(at_commands.reset(),),
                                trigger='interval', seconds=params.seconds, jobstore='default')
        return {'status': 'success', 'content': job.id}
    except Exception as e:
        return ORJSONResponse(status_code=400, content={"status": "error", "message": f"An error occurred: {str(e)}"})
