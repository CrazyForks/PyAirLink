from configparser import ConfigParser


class Config:
    def __init__(self, ini_path='data/config.ini', default_ini_path='config.ini.template'):
        self.config = ConfigParser()
        config_read = self.config.read(ini_path)
        if not config_read:
            print(f"Warning: '{ini_path}' not found. Using default settings.")
            self.config.read(default_ini_path)

    def sqlite_url(self):
        url = self.config.get('DATABASE', 'SQLITE')
        return f'sqlite:///data/{url}'

    def serial(self):
        port = self.config.get('SERIAL', 'PORT')
        rate = int(self.config.get('SERIAL', 'BAUD_RATE'))
        timeout = float(self.config.get('SERIAL', 'TIMEOUT'))
        return {'port': port, 'rate': rate, 'timeout': timeout}


config = Config()