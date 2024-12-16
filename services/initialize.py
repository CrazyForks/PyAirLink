from io import StringIO

import serial
import threading
import time
import logging

from .utils.sms import parse_pdu, encode_pdu
from .utils.commands import ATCommands


# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')
logger = logging.getLogger("PyAirLink")

# 串口配置
SERIAL_PORT = "/dev/ttyACM0"  # 根据实际情况修改
BAUD_RATE = 115200
TIMEOUT = 1
at_commands = ATCommands()


def send_at_command(ser, command, keywords=None, timeout=3):
    """
    发送AT指令并等待响应
    :param ser: 串口对象
    :param command: 要发送的AT指令字符串
    :param keywords: 判断是否成功的关键字
    :param timeout: 等待响应的超时时间(秒)
    :return: 命令响应
    """
    # 发送AT指令
    ser.write(command)
    logger.debug(f"发送指令: {command}")
    # 等待响应
    response = wait_for_response(ser, keywords=keywords, timeout=timeout)
    # 返回响应
    return response


def wait_for_response(ser, keywords, timeout=3):
    """
    从串口等待包含特定关键词的响应
    :param ser: 串口对象
    :param keywords: 字符串或列表，用于匹配返回数据中的特定关键字
    :param timeout: 超时时间(秒)
    :return: 若匹配成功，返回包含该关键词的完整响应；否则返回None
    """
    if not keywords:
        keywords = ['OK', 'ERROR']
    if isinstance(keywords, str):
        keywords = [keywords]

    end_time = time.time() + timeout
    response = ""
    while time.time() < end_time:
        if ser.in_waiting:
            chunk = ser.read(ser.in_waiting).decode(errors='ignore')
            response += chunk
            # 检查是否包含关键字
            for kw in keywords:
                if kw in response:
                    logger.debug(f"匹配到关键词 '{kw}' 于响应中")
                    return response
        time.sleep(0.1)
    # 超时仍未匹配到任何关键词
    logger.debug("等待关键词超时:", keywords)
    return None


def initialize_module(ser):
    """
    初始化模块
    """
    logger.info("正在初始化模块...")

    # 发送基本AT指令
    response = send_at_command(ser, at_commands.at())
    if not response or "OK" not in response:
        logger.error("无法与模块通信")
        return False

    # 检查SIM卡
    response = send_at_command(ser, at_commands.cpin())
    if "READY" not in response:
        logger.error("未检测到 SIM 卡，请检查后重启模块")
        return False
    logger.info("SIM 卡已就绪")

    # 设置短信格式为 PDU
    response = send_at_command(ser, at_commands.cmgf())
    if "OK" not in response:
        logger.error("无法设置短信格式为 PDU")
        return False
    logger.info("短信格式设置为 PDU")

    # 设置字符集为 UCS2
    response = send_at_command(ser, at_commands.cscs())
    if "OK" not in response:
        logger.error("无法设置字符集为 UCS2")
        return False
    logger.info("字符集设置为 UCS2")

    # 配置新短信通知
    response = send_at_command(ser, at_commands.cnmi())
    if "OK" not in response:
        logger.error("无法配置新短信通知")
        return False
    logger.info("新短信通知配置完成")

    # 检查 GPRS 附着状态
    while True:
        response = send_at_command(ser, at_commands.cgatt(), keywords="+CGATT: 1")
        if response:
            logger.info("GPRS 已附着")
            break
        else:
            logger.warning("GPRS 未附着，5秒后重试...")
            time.sleep(5)

    logger.info("模块初始化完成")
    return True


def handle_sms(phone_number, sms_content, receive_time):
    """
    处理接收到的短信（可根据需求进行转发或其他操作）
    """
    logger.info(f"在{receive_time}收到短信来自 {phone_number}，内容: {sms_content}")
    # 在此处添加短信转发逻辑，例如发送到服务器或其他设备
    # 例如: forward_sms(phone_number, sms_content)


def send_sms(ser, to, text):
    """
    使用AT指令在PDU模式下发送SMS。
    ser是已打开的pyserial串口对象。
    to为目标号码字符串（如"+8613800138000"），text为短信内容（UTF-8字符串）。
    """
    logging_tag = "send_sms"
    pdu, length = encode_pdu(to, text)
    if not pdu or not length:
        logger.error("%s: 短信编码失败", logging_tag)
        return False

    # 设置CMGF=0进入PDU模式（如果之前没设置过）
    resp = send_at_command(ser, at_commands.cmgf())
    if not resp:
        logger.error("%s: 无法进入PDU模式", logging_tag)
        return False

    # 发送AT+CMGS指令
    resp = send_at_command(ser, at_commands.cmgs(length), keywords='>', timeout=3)
    if not resp:
        logger.error("%s: 未收到短信发送提示符 '>'，超时", logging_tag)
        return False

    # 发送PDU数据和Ctrl+Z结束符(0x1A)
    resp = send_at_command(ser, pdu.encode('utf-8') + b'\x1A', keywords='+CMGS:', timeout=5)
    logger.debug("%s: 已发送PDU数据，等待发送成功URC", logging_tag)
    if resp:
        logger.info("%s: 短信发送成功", logging_tag)
        return True
    else:
        logger.error("%s: 未收到+CMGS:确认，发送失败", logging_tag)
        return False


def sms_listener(ser):
    """
    监听串口接收短信
    """
    while True:
        try:
            if ser.in_waiting:
                data = ser.read(ser.in_waiting).decode(errors='ignore')
                logger.debug(f"接收到数据: {data}")
                last_line = data.strip().splitlines()[-1]
                f = StringIO(last_line)
                # 解析短信通知
                match = parse_pdu(f)
                if isinstance(match, dict):
                    phone_number = match.get('sender').get('number')
                    receive_time = match.get('scts')
                    sms_content = match.get('user_data').get('data')
                    handle_sms(phone_number, sms_content, receive_time)
        except Exception as e:
            logger.error(f"监听过程中出错: {e}")
            time.sleep(1)


def main():
    # 打开串口
    try:
        ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=TIMEOUT)
        logger.info(f"已打开串口 {SERIAL_PORT}，波特率 {BAUD_RATE}")
    except Exception as e:
        logger.error(f"无法打开串口 {SERIAL_PORT}: {e}")
        return

    # 初始化 Air780E
    if not initialize_module(ser):
        logger.error("模块初始化失败，退出程序")
        ser.close()
        return

    # 启动短信监听线程
    listener_thread = threading.Thread(target=sms_listener, args=(ser,), daemon=True)
    listener_thread.start()
    logger.info("开始监听短信...")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("程序终止")
    finally:
        ser.close()


if __name__ == "__main__":
    main()
