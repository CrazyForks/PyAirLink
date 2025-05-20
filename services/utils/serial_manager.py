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
                logger.info(f"Serial port is open：{self.port}, baud rate：{self.rate}")
            except Exception as e:
                logger.error(f"Unable to open serial port：{e}")
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
                logger.info("Serial port closed")
            except Exception as e:
                logger.error(f"Error closing serial port: {e}")
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
                        logger.warning("The serial port is not open, trying to open...")
                        self.open()

                    logger.debug(f"Sending command: {command}")
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
                                    logger.debug(f"Matched keyword '{kw}' in response: {response}")
                                    return response
                        time.sleep(0.1)
                    logger.debug(f"Waiting for keywords {keywords} Timed out: {response}")
                    return response if response else None
                except (serial.SerialException, serial.SerialTimeoutException, OSError) as e:
                    logger.error(f"Serial communication error: {e}")
                    # 尝试重连
                    attempt += 1
                    logger.info(f"Trying to reconnect to the serial port ({attempt} times)")
                    self.close()  # 关闭串口，准备重新打开
                    time.sleep(1)  # 等待一段时间再尝试
                    continue  # 继续下一次重试
                except Exception as e:
                    logger.error(f"send_at_command error: {e}")
                    return None

        logger.error(f"Unable to complete command send after {retries} attempts: {command}")
        return None