from datetime import datetime
from typing import List, Union, Optional, Any, Dict

from pydantic import BaseModel, Field, field_validator


class ErrorDetail(BaseModel):
    loc: List[Union[str, int]]
    msg: str
    type: str


class ErrorModel(BaseModel):
    detail: tuple[ErrorDetail]


class ResponseDetail(BaseModel):
    status: str
    data: List[Any]
    message: str


class Command(BaseModel):
    keyword: Optional[str] = Field(default=None, description="AT命令返回的关键字, 一般是'OK'或者 'ERROR'，不传则两个都检测")
    timeout: int = Field(default=3, description="等待AT命令回应的超时时间")

    @field_validator('keyword', mode='after', check_fields=False)
    @classmethod
    def check_message(cls, v: str) -> list[str]:
        if v is None:
            return ['OK', 'ERROR']
        return [v]


class CommandRequest(Command):
    command: str


class CommandBaseRequest(CommandRequest):
    command: str


class CommandResponse(BaseModel):
    status: str
    content: str

class SendSMSRequest(BaseModel):
    country: int
    number: int
    message: str

    @field_validator('message')
    @classmethod
    def check_message(cls, v: str) -> str:
        if len(v) > 70:
            raise ValueError(f"Do not support long sms yet, makesure less than 71 characters.")
        return v


class ListScheduleJob(BaseModel):
    id: str
    next_run_time: datetime
    trigger: str
    func: str


class ScheduleSendSMSRequest(SendSMSRequest):
    id: str
    seconds: int
    next_run_time: datetime = Field(default=datetime.now(), description="下次执行的时间")