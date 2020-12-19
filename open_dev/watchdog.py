from util.check_internet_connection import CheckInternetConnection
from util.com_ports import COM_port
from util.logger_super import LoggerSuper
import threading
from time import sleep
import logging

class CWatchDog(COM_port, LoggerSuper):
    logger = logging.getLogger('watchdog')
    def __init__(self, miner, PID):
        super().__init__('watchdog', PID, 9600, 1)

        self._internet_connection = CheckInternetConnection()
        self.miner = miner

        self._thread = threading.Thread(target=self._threaded_ping, args=(), daemon=True)
        self._thread.start()

    def send_to_serial(self, s):
        if self.initialized:
            try:
                self.serial.write(bytes(s, 'utf-8'))
            except:
                self.initialized = False
                self.logger.critical('Write error to port ' + self.serial)

    def _threaded_ping(self):
        while True:
            if self.initialized:
                speed = self.miner.get_speed()
                self.logger.debug(f'watchdog: speed is {speed} mh/s')
                if speed >= self.miner.get_minspeed() or self.miner.get_minspeed() == 0:
                    self.send_to_serial('~U')  # Отправка команды "я в норме" на вотчдог
                else:
                    self.logger.info(f'Speed is {speed }, but terget speed is {self.miner.get_minspeed()}')
            sleep(5)