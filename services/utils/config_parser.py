from configparser import ConfigParser


class Config:
    def __init__(self):
        self.config = ConfigParser()
        try:
            self.config.read('data/config.ini')
        except FileNotFoundError as e:
            self.config.read('config.ini.template')

    def sqlite_url(self):
        url = self.config.get('DATABASE', 'SQLITE')
        return f'sqlite:///data/{url}'

    def serial(self):
        port = self.config.get('SERIAL', 'PORT')
        rate = int(self.config.get('SERIAL', 'PORT'))
        timeout = float(self.config.get('SERIAL', 'TIMEOUT'))
        return {'port': port, 'rate': rate, 'timeout': timeout}


config = Config()