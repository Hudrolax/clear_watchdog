import serial
from time import sleep
import threading
import socket
import json

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
        self._terget_speed = self._read_terget_speed()

    def _read_terget_speed(self):
        speed = 0
        handle = open("speed.txt")
        try:
            speed = handle.readlines()
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
            sock.settimeout(1)
            sock.connect(server_address)
        except:
            return 0

        try:
            request = '{"id":0,"jsonrpc":"2.0","method":"miner_getstat1"}'
            request = request.encode()
            sock.sendall(request)
            data = sock.recv(512)
            message = json.loads(data)
            json_answer = message.get('result')
            speed = json_answer[2].split(';')[0]
            print(type(speed))
            return speed
        except:
            return 0
        finally:
            sock.close()

    def send_to_serial(self, _s_port, s):
        speed = self.get_speed('127.0.0.1', 3333)
        if speed >= self._terget_speed or self._terget_speed == 0:
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