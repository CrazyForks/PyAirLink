import serial

from .config_parser import config


class SerialManager:
    def __init__(self):
        self.port = config.serial().get('port')
        self.rate = config.serial().get('rate')
        self.timeout = config.serial().get('timeout')
        self.ser = None

    def open(self):
        self.ser = serial.Serial(self.port, self.rate, timeout=self.timeout)
        return self.ser

    def __enter__(self):
        self.open()
        return self.ser

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()

    def close(self):
        if self.ser:
            self.ser.close()
            print("串口已关闭")
