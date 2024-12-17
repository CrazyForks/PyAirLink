import time
import logging

import serial

from services import serial_lock
from .config_parser import config

logger = logging.getLogger("PyAirLink")


class SerialManager:
    def __init__(self):
        self.port = config.serial().get('port')
        self.rate = config.serial().get('rate')
        self.timeout = config.serial().get('timeout')
        self._ser = None

    def open(self):
        """
        打开串口连接。
        """
        if self._ser is None or not self._ser.is_open:
            try:
                self._ser = serial.Serial(self.port, self.rate, timeout=self.timeout)
                logger.info(f"串口已打开：{self.port}，波特率：{self.rate}")
            except Exception as e:
                logger.error(f"无法打开串口：{e}")
                self._ser = None
                raise e
        return self

    def __enter__(self):
        self.open()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()

    def close(self):
        """
        关闭串口连接。
        """
        if self._ser and self._ser.is_open:
            try:
                self._ser.close()
                logger.info("串口已关闭")
            except Exception as e:
                logger.error(f"关闭串口时出错：{e}")
            finally:
                self._ser = None

    def send_at_command(self, command, keywords=None, timeout=3, retries=120):
        """
        发送AT指令并等待响应，支持自动重连机制。

        :param command: 要发送的AT指令字符串
        :param keywords: 判断响应成功的关键字列表
        :param timeout: 等待响应的超时时间(秒)
        :param retries: 最大重试次数
        :return: 命令响应字符串，或None表示失败
        """
        if not keywords:
            keywords = ['OK', 'ERROR']
        if isinstance(keywords, str):
            keywords = [keywords]

        attempt = 0  # 当前重试次数

        while attempt < retries:
            with serial_lock:
                try:
                    # 检查串口是否已打开
                    if self._ser is None or not self._ser.is_open:
                        logger.warning("串口未打开，正在尝试打开...")
                        self.open()

                    logger.debug(f"发送指令: {command}")
                    self._ser.write(command)
                    self._ser.flush()
                    response = ''
                    start_time = time.time()
                    while time.time() - start_time < timeout:
                        if self._ser.in_waiting:
                            data = self._ser.read(self._ser.in_waiting).decode(errors='ignore')
                            response += data
                            for kw in keywords:
                                if kw in response:
                                    logger.debug(f"匹配到关键词 '{kw}' 于响应中: {response}")
                                    return response
                        time.sleep(0.1)
                    logger.debug(f"等待关键词 {keywords} 超时: {response}")
                    return response if response else None
                except (serial.SerialException, serial.SerialTimeoutException, OSError) as e:
                    logger.error(f"串口通信出错：{e}")
                    # 尝试重连
                    attempt += 1
                    logger.info(f"正在尝试重新连接串口（第 {attempt} 次重试）")
                    self.close()  # 关闭串口，准备重新打开
                    time.sleep(1)  # 等待一段时间再尝试
                    continue  # 继续下一次重试
                except Exception as e:
                    logger.error(f"send_at_command 出错：{e}")
                    return None

        logger.error(f"在尝试 {retries} 次后，无法完成命令发送：{command}")
        return None