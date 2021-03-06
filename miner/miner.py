import socket
import json
import os
import threading
from time import sleep
from prettytable import PrettyTable
from miner.miner_config import MinerConfig
from miner.miner_card import Card
from miner.miner_logs import MinerLogs
from util.logger_super import LoggerSuper
from util.base_class import BaseClass
from config import MINER_PATH, CHANGE_CONFIG, REBOOT_IF_CARD_SPEED_ZERO_5MIN
from util.reboot import reboot
import requests
import logging

class Miner(LoggerSuper):
    logger = logging.getLogger('Miner')
    def __init__(self, ip, port, miner):
        self.miner = miner
        self.ip = ip
        self.port = port
        self.config = MinerConfig()
        self.cards = []
        self._crash_got = False
        self._crash_got_reaction = False

        self._thread = threading.Thread(target=self._threaded_get_miner_info, args=(), daemon=False)
        self._thread.start()

    def _parse_config(self):
        self.config.read_config()
        self.cards = []
        for cvddc in enumerate(self.config.cvddc):
            _cvddc = cvddc[1]
            _mvddc = self.config.mvddc[cvddc[0]]
            _cclock = 0
            for clock in self.config.cclock:
                if clock[0] == '*' or int(clock[0]) == cvddc[0]+1:
                    _cclock = int(clock[1])
            _mclock = 0
            for mclock in self.config.mclock:
                if mclock[0] == '*' or int(mclock[0]) == cvddc[0]+1:
                    _mclock = int(mclock[1])

            _card = Card(_cvddc, _mvddc, _cclock, _mclock)
            self.cards.append(_card)

    def _pase_miner_data(self):
        json = self.get_json()
        _speeds = self._get_speed_different(json)
        for speed in enumerate(_speeds):
            try:
                self.cards[speed[0]].speed = speed[1] / 1000
            except IndexError:
                continue
        for card in self.cards:
            card.check_speed()

    def _parse_logs_24h(self):
        parsed_log_24h = MinerLogs.parse_logs(86400)
        for card in enumerate(self.cards):
            card[1].crashes24h = parsed_log_24h[0].count(card[0] + 1)
            for parse_type in parsed_log_24h[1]:
                if parse_type[0] == card[0] + 1:
                    card[1].type = parse_type[1]

    def _parse_logs_1m(self):
        parsed_log_1min = MinerLogs.parse_logs(60)
        for card in enumerate(self.cards):
            card[1].crashes1m = parsed_log_1min[0].count(card[0] + 1)

    def _get_crash_last_minute(self):
        if not self._crash_got:
            for card in enumerate(self.cards):
                if card[1].crashes1m > 0:
                    self.logger.critical(f'Crash GPU{card[0]+1} got!')
                    card[1].increase_voltage()
                    card[1].decrease_clocks()
                    if card[1].set_cclock > 0:
                        self.logger.info(f'Set cclock {card[1].set_cclock} for GPU{card[0]+1}')
                    if card[1].set_mclock > 0:
                        self.logger.info(f'Set mclock {card[1].set_mclock} for GPU{card[0]+1}')
                    if card[1].set_cvddc > 0:
                        self.logger.info(f'Set cvddc {card[1].set_cvddc} for GPU{card[0]+1}')
                    if card[1].set_mvddc > 0:
                        self.logger.info(f'Set mvddc {card[1].set_mvddc} for GPU{card[0]+1}')
                    self._crash_got = True

        if self._crash_got and not self._crash_got_reaction:
            self.config.update_config(self.cards)
            self.logger.info('Config updated.')
            self._crash_got_reaction = True
            if MINER_PATH.find('test') == -1:
                self.logger.info('Rebooting...')
                reboot()
            else:
                self.logger.info("Not rebooting because it's' Test")
            BaseClass.exit()

    def _check_card_speed_and_reboot(self):
        for card in enumerate(self.cards):
            if card[1].speed_zero_douring_5min():
                self.logger.critical(f'GPU{card[0]} speed is 0 douring five minutes.')
                if REBOOT_IF_CARD_SPEED_ZERO_5MIN:
                    if MINER_PATH.find('test') == -1:
                        self.logger.info('Rebooting...')
                        reboot()
                    else:
                        self.logger.info("Not rebooting because it's' Test")

    def _lolminer_add_cards(self):
        json = self.get_json()
        if json is None:
            self.cards.append(Card(0, 0, 0, 0, 'RX 580'))
            return
        gpus = json.get('GPUs')
        for gpu in gpus:
            card_type = gpu.get('Name')
            if card_type.find('RX 470') > -1:
                card_type = 'RX 470'
            elif card_type.find('RX 480') > -1:
                card_type = 'RX 480'
            elif card_type.find('RX 570') > -1:
                card_type = 'RX 570'
            elif card_type.find('RX 580') > -1:
                card_type = 'RX 580'
            self.cards.append(Card(0, 0, 0, 0, card_type))

    def _threaded_get_miner_info(self):
        # Разбор конфига
        if self.miner == 'phoenix':
            self._parse_config()
        elif self.miner == 'lolminer':
            self._lolminer_add_cards()
        print('Наберите cards для просмотра состояния рига.')
        while BaseClass.working():
            # разбор данные от майнера
            self._pase_miner_data()
            if self.miner == 'phoenix':
                # парсинг логов 24 часа
                self._parse_logs_24h()
                # парсинг логов 1 минуту
                self._parse_logs_1m()
                # проверяем как долго на карте скорость 0 и перезагружаем, если дольше 5 минут
            self._check_card_speed_and_reboot()
            # Действия, при обнаружении краша за последнюю минуту
            if CHANGE_CONFIG:
                self._get_crash_last_minute()

            sleep(5)

    def set_cards_number(self, val):
        if isinstance(val, int):
            self.cards = val
        else:
            raise TypeError('"cards" parametr must be int')

    def get_minspeed(self):
        return self.config.min_speed

    def get_json(self):
        if self.miner == 'phoenix':
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
        elif self.miner == 'lolminer':
            try:
                return json.loads(requests.get(f"http://{self.ip }:{self.port}", timeout=3).content.decode())
            except:
                return None

    def _get_speed_different(self, json):
        if json is not None:
            speed_int = []
            if self.miner == 'phoenix':
                speed_str = json[3].split(';')
                for crd in speed_str:
                    speed_int.append(int(crd))
            elif self.miner == 'lolminer':
                gpus = json.get("GPUs")
                for gpu in gpus:
                    speed_int.append(gpu.get('Performance')*1000)
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

    def print_cards_list(self):
        table = PrettyTable()
        table.field_names = ["#", "speed", "crashes 24h", "cvddc", "mvddc", 'cclock', 'mclock', 'type']
        for card in enumerate(self.cards):
            _addon = ''
            if card[1].speed < card[1].normal_speed:
                _addon = '!!!'
            if card[1].speed == 0:
                _addon = f'{card[1].time_speed_belov_zero_min()} min'
            table.add_row([card[0]+1, f'{card[1].speed} {_addon}', card[1].crashes24h, card[1].cvddc, card[1].mvddc, card[1].cclock, card[1].mclock, card[1].type])
        print('-----------------------------------------------------------------------')
        print(f'Total speed: {self.get_speed()}')
        print(table)

    def print_crashes(self):
        print('-----------------------------------------------------------------------')
        print('Crashes:')
        table = PrettyTable()
        table.field_names = ["#", "crashes 24h", "crashes 1m"]
        for card in enumerate(self.cards):
            table.add_row([card[0]+1, card[1].crashes24h, card[1].crashes1m])
        print(table)


if __name__ == '__main__':
    crashes = MinerLogs.parse_logs()
    print(crashes)