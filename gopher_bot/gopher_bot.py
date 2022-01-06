# Gopher server stats bot
import os
import psutil
import socket
import logging.config
from typing import Any
from dotenv import load_dotenv
from wh00t_core.library.client_network import ClientNetwork


class GopherBot:
    def __init__(self, logging_object: Any, socket_host: str, socket_port: int):
        self._logger: logging.Logger = logging_object.getLogger(type(self).__name__)
        self._logger.setLevel(logging.INFO)
        self._chat_key: str = '/gopher'
        self._host_name: str = socket.gethostname()
        self._socket_network: ClientNetwork = ClientNetwork(socket_host, socket_port,
                                                            'gopher_bot', 'app', logging)

    def run_bot(self) -> None:
        self._socket_network.sock_it()
        self._socket_network.receive(self._receive_message_callback)

    def _receive_message_callback(self, package: dict) -> bool:
        if ('id' in package) and (package['id'] not in ['wh00t_server', 'gopher_bot']) and ('message' in package):
            if 'category' in package and package['category'] == 'chat_message' and \
                    isinstance(package['message'], str) and package['message'].replace(self._chat_key, '') == '':
                self._send_server_data()
        return True

    @staticmethod
    def round_stat(data: float) -> float:
        return round(data, 2)

    def _get_server_data(self) -> str:
        cpu_utilization: float = psutil.cpu_percent(4)
        load1, load5, load15 = psutil.getloadavg()
        cpu_usage: float = load1 * 100
        memory_usage: float = psutil.virtual_memory()[2]
        disk_usage = psutil.disk_usage('/').percent
        temp = psutil.sensors_temperatures()['acpitz'][0].current
        screen_summary = (''.join(os.popen('screen -ls').readlines())).rstrip('\n')
        server_stats_report = f'\n\n 🖥️ | {self._host_name}' \
                              f'\n CPU Utilization: {self.round_stat(cpu_utilization)} %' \
                              f'\n CPU Load: {self.round_stat(cpu_usage)}' \
                              f'\n Mem Usage: {self.round_stat(memory_usage)} %' \
                              f'\n Temp: {self.round_stat(temp)} °C' \
                              f'\n Disk Usage: {self.round_stat(disk_usage)} % \n' \
                              f'\n Screen Summary:\n {screen_summary}\n'
        return server_stats_report

    def _send_server_data(self) -> None:
        self._send_chat_data(f'Ok, getting {self._host_name} stats 🤖')
        self._send_chat_data(self._get_server_data())

    def _send_chat_data(self, chat_message: str):
        self._socket_network.send_message('chat_message', chat_message)


if __name__ == '__main__':
    logging.config.fileConfig(fname=os.path.abspath('gopher_bot/bin/logging.conf'), disable_existing_loggers=False)
    logger: logging.Logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)

    try:
        load_dotenv()
        HOST_SERVER_ADDRESS: str = os.getenv('HOST_SERVER_ADDRESS')
        SOCKET_SERVER_PORT: int = int(os.getenv('SOCKET_SERVER_PORT'))

        print(f'\nGopher data sender will now continuously run')
        gopher: GopherBot = GopherBot(logging, HOST_SERVER_ADDRESS, SOCKET_SERVER_PORT)
        gopher.run_bot()
    except TypeError:
        logger.error('Received TypeError: Check that the .env project file is configured correctly')
        exit()
