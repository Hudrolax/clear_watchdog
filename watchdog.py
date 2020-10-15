import serial
import threading
import socket
import json
import requests
from datetime import datetime
from time import sleep
import os

class CheckInternetConnection:
    CHECKTIME = 300
    SITES_FOR_CHECKING = []
    SITES_FOR_CHECKING.append('https://www.google.com')
    SITES_FOR_CHECKING.append('http://www.ru')

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
            print(f'{site} is ok')
            return True
        except:
            if __name__ == '__main__':
                print(f'{site} is offline')
            return False

    def _threaded_check_func(self):
        while True:
            for _site in self.SITES_FOR_CHECKING:
                if self._check_site(_site):
                    self._last_recieve_time = datetime.now()
                    break
                else:
                    print(f'Error connection. Reboot network things in {round(self.CHECKTIME-(datetime.now() - self._last_recieve_time).total_seconds())} seconds.')
            sleep(20)

class CWatchDog:
    def __init__(self, port: str):
        print('Try connect to WatchDog at port ' + port)
        self.__serial = serial.Serial(port, 9600, timeout=1)
        self.__serial.flushInput()
        self.__serial.flushOutput()
        self.__serial.baudrate = 9600
        self.__serial.timeout = 1
        self.__serial.write_timeout = 1
        self._internet_connection = CheckInternetConnection()
        self._terget_speed = self._read_terget_speed()

        self._thread = threading.Thread(target=self._ping, args=(), daemon=True)
        self._thread.start()

    def _read_terget_speed(self):
        speed = 0
        handle = open("speed.txt")
        try:
            speed = int(handle.readline())
            print(f'loaded speed from "speed.txt is {speed}"')
        except:
            print('Load speed from "speed.txt" failed')
        finally:
            handle.close()
        return speed

    def get_speed(self, ip, port):
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            server_address = (ip, port)
            sock.settimeout(3)
            sock.connect(server_address)
        except:
            return 0

        try:
            request = {"id": 0, "jsonrpc": "2.0", "method": "miner_getstat1"}
            sock.sendall(json.dumps(request).encode())
            sock.sendall(os.linesep.encode())
            sock.shutdown(socket.SHUT_WR)  # no more writing
            with sock.makefile('r', encoding='utf-8') as file:
                response = json.load(file)
            json_answer = response.get('result')
            speed = json_answer[2].split(';')[0]
            return speed
        except:
            return 0
        finally:
            sock.close()

    def send_to_serial(self, _s_port, s):
        speed = self.get_speed('127.0.0.1', 3333)
        if speed >= self._terget_speed or self._terget_speed == 0 or not self._internet_connection.internet_is_available():
            try:
                _s_port.write(bytes(s, 'utf-8'))
            except:
                print('Write error to port ' + _s_port)
        else:
            print(f'Speed is {speed}, but terget speed is {self._terget_speed}')

    def _ping(self):
        while True:
            self.send_to_serial(self.__serial, '~U')  # Отправка команды "я в норме" на вотчдог
            sleep(5)