import socket
import json
import os
import threading
from time import sleep
from datetime import datetime
from config import MINER_PATH, MINER_LOG_MASK

class MinerConfig:
    def __init__(self):
        self.cvddc = []
        self.mvddc = []
        self.min_speed = 0

    @staticmethod
    def _str_list_to_int(lst):
        lst_int = []
        for el in lst:
            lst_int.append(int(el))
        return lst_int

    def read_config(self):
        with open(MINER_PATH+'config.txt') as config:
            lines = config.readlines()
            for line in lines:
                line = line.replace('\n', '')
                if line.find('-cvddc ') > -1:
                    line = line.replace('-cvddc ', '')
                    self.cvddc  = MinerConfig._str_list_to_int(line.split(','))
                elif line.find('-mvddc ') > -1:
                    line = line.replace('-mvddc ', '')
                    self.mvddc  = MinerConfig._str_list_to_int(line.split(','))
                elif line.find('-minRigSpeed ') > -1:
                    line = line.replace('-minRigSpeed ', '')
                    self.min_speed = int(line)


class MinerLogs:
    @staticmethod
    def modification_date(filename):
        t = os.path.getmtime(filename)
        return datetime.fromtimestamp(t)

    @staticmethod
    def get_today_logs():
        dirs = os.listdir(MINER_PATH)
        file_list = []
        for file in dirs:
            if file.find(MINER_LOG_MASK) > -1 and (datetime.now()-MinerLogs.modification_date(MINER_PATH+file)).total_seconds() < 3600:
                file_list.append(MINER_PATH+file)
        return file_list

    @staticmethod
    def parse_logs():
        logs = MinerLogs.get_today_logs()
        crushes = []
        for log in logs:
            with open(log) as file:
                lines = file.readlines()
                for line in lines:
                    if line.find('not responding') > -1:
                        pieces = line.split(' ')
                        for piece in pieces:
                            if piece.find('GPU') > -1:
                                gpu = int(piece.replace('GPU',''))
                                crushes.append(gpu)
        return crushes


class Card:
    def __init__(self, cvddc, mvddc):
        self.speed = 0
        self.crushes = 0
        self.cvddc = cvddc
        self.mvddc = mvddc

    def __str__(self):
        return f'speed={self.speed}:crushes={self.crushes} ({self.cvddc}/{self.mvddc})'

class Miner:
    def __init__(self, ip, port):
        self.ip = ip
        self.port = port
        self.config = MinerConfig()
        self.cards = []

        self._thread = threading.Thread(target=self._threaded_get_miner_info, args=(), daemon=True)
        self._thread.start()

    def _threaded_get_miner_info(self):
        while True:
            self.config.read_config()
            self.cards = []
            for cvddc in enumerate(self.config.cvddc):
                self.cards.append(Card(cvddc[1], self.config.mvddc[cvddc[0]]))
            json = self.get_json()
            _speeds = self._get_speed_different(json)

            sleep(5)

    def set_cards_number(self, val):
        if isinstance(val, int):
            self.cards = val
        else:
            raise TypeError('"cards" parametr must be int')

    def get_minspeed(self):
        return self.config.min_speed

    def get_json(self):
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            server_address = (self.ip, self.port)
            sock.settimeout(3)
            sock.connect(server_address)
        except:
            return None

        try:
            request = {"id": 0, "jsonrpc": "2.0", "method": "miner_getstat2"}
            sock.sendall(json.dumps(request).encode())
            sock.sendall(os.linesep.encode())
            sock.shutdown(socket.SHUT_WR)  # no more writing
            with sock.makefile('r', encoding='utf-8') as file:
                response = json.load(file)
            json_answer = response.get('result')
            return json_answer
        except:
            return None
        finally:
            sock.close()

    @staticmethod
    def _get_speed_different(json):
        if json is not None:
            speed_str = json[3].split(';')
            speed_int = []
            for crd in speed_str:
                speed_int.append(int(crd))
            return speed_int
        else:
            return []

    def get_speed(self, card = 0):
        """
        :param card: если 0, то скорость всех карт, если не ноль, то возвращается скорость карты.
        :return: -1, если индекса карты нет
        """
        if card == 0:
            speed = 0
            for card in self.cards:
                speed += card.speed
            return speed
        else:
            try:
                return self.cards[card-1].speed/1000
            except IndexError:
                return -1

    def get_cards_count(self):
        return len(self.cards)

if __name__ == '__main__':
    miner = Miner('127.0.0.1', 3333)
    sleep(1)
    for card in miner.cards:
        print(card)