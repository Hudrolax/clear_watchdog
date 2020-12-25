import threading
import requests
from datetime import datetime
from time import sleep
from util.logger_super import LoggerSuper
import logging

class CheckInternetConnection(LoggerSuper):
    CHECKTIME = 300
    SITES_FOR_CHECKING = []
    SITES_FOR_CHECKING.append('https://www.google.com')
    SITES_FOR_CHECKING.append('http://www.ru')

    logger = logging.getLogger('CheckInternetConnection')
    def __init__(self):
        self._last_recieve_time = datetime.now()
        self._check_thread = threading.Thread(target=self._threaded_check_func, args=(), daemon=True)
        self._check_thread.start()

    def internet_is_available(self):
        if (datetime.now() - self._last_recieve_time).total_seconds() > self.CHECKTIME:
            return False
        else:
            return True

    def _check_site(self, site):
        try:
            content = requests.get(site, timeout=5).content.decode()
            self.logger.debug(f'{site} is ok')
            return True
        except:
            if __name__ == '__main__':
                self.logger.info(f'{site} is offline')
            return False

    def _threaded_check_func(self):
        while True:
            for _site in self.SITES_FOR_CHECKING:
                if self._check_site(_site):
                    self._last_recieve_time = datetime.now()
                    break
                else:
                    self.logger.info(f'Connection error to {_site}.')
            sleep(20)