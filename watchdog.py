import serial
from time import sleep
import threading

class CWatchDog:
    def __init__(self, port: str):
        print('Try connect to WatchDog at port ' + port)
        self.__serial = serial.Serial(port, 9600, timeout=1)
        self.__serial.flushInput()
        self.__serial.flushOutput()
        self.__serial.baudrate = 9600
        self.__serial.timeout = 1
        self.__serial.write_timeout = 1
        self._thread = threading.Thread(target=self._ping, args=(), daemon=True)
        self._thread.start()

    @staticmethod
    def send_to_serial(_s_port, s):
        try:
            _s_port.write(bytes(s, 'utf-8'))
        except:
            print('Write error to port ' + _s_port)

    def _ping(self):
        while True:
            CWatchDog.send_to_serial(self.__serial, '~U')  # Отправка команды "я в норме" на вотчдог
            sleep(5)