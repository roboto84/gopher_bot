# Gopher server stats bot
import os
import time
import platform
import uuid
import re
import psutil
import socket
import logging.config
from datetime import datetime
from typing import Any
from dotenv import load_dotenv
from wh00t_core.library.client_network import ClientNetwork
from wh00t_core.library.network_commons import NetworkCommons
from wh00t_core.library.network_utils import NetworkUtils
from bin.utils import get_external_ip


class GopherBot:
    def __init__(self, logging_object: Any, socket_host: str, socket_port: int):
        self._logger: logging.Logger = logging_object.getLogger(type(self).__name__)
        self._logger.setLevel(logging.INFO)
        self._chat_key: str = '/gopher'
        self._host_name: str = socket.gethostname()
        self._host_ip_address: str = socket.gethostbyname(self._host_name)
        self._mac_address: str = GopherBot._get_mac_address()
        self._network_commons: NetworkCommons = NetworkCommons()
        self._network_utils: NetworkUtils = NetworkUtils()
        self._socket_network: ClientNetwork = ClientNetwork(socket_host, socket_port,
                                                            'gopher_bot', 'app', logging)

    def run_bot(self) -> None:
        self._socket_network.sock_it()
        self._socket_network.receive(self._receive_message_callback)

    def _receive_message_callback(self, package: dict) -> bool:
        if ('id' in package) and (package['id'] not in ['wh00t_server', 'gopher_bot']) and ('message' in package):
            if 'category' in package and package['category'] == self._network_commons.get_chat_message_category() and \
                    isinstance(package['message'], str):
                if package['message'].rstrip().replace(self._chat_key, '') == '':
                    self._send_chat_data(f'{self._host_name} is UP 🤖')
                elif package['message'].replace(self._chat_key, '').strip() == self._host_name:
                    self._send_server_data()
        return True

    @staticmethod
    def _get_mac_address():
        mac_address: int = uuid.getnode()
        if (mac_address >> 40) % 2:
            mac_address_string = 'MAC address not found'
        else:
            mac_address_string = ':'.join(re.findall('..', '%012x' % mac_address))
        return mac_address_string

    @staticmethod
    def round_stat(data: float) -> float:
        return round(data, 2)

    def _get_server_data(self) -> str:
        # TODO: Consider using "hostnamectl" data and differentitate between computer platforms
        platform_summary: str = platform.platform()
        cpu_utilization: float = psutil.cpu_percent(4)
        load1, load5, load15 = psutil.getloadavg()
        cpu_usage: float = load1 * 100
        memory_usage: float = psutil.virtual_memory()[2]
        disk_usage: float = psutil.disk_usage('/').percent
        temp_sensor_data: dict = psutil.sensors_temperatures()
        logger.info(temp_sensor_data)
        temp = f'{self.round_stat(temp_sensor_data["acpitz"][0].current)} °C' \
            if 'acpitz' in temp_sensor_data else 'unknown'
        external_ip_address: str = get_external_ip()
        local_time: str = datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')
        local_timezone = datetime.utcnow().astimezone().tzinfo
        screen_summary = (''.join(os.popen('screen -ls').readlines())).rstrip('\n')
        server_stats_report = f' 🖥️ | {self._host_name}' \
                              f'\n\n Platform: {platform_summary}' \
                              f'\n DateTime: {local_time} {local_timezone}' \
                              f'\n CPU Utilization: {self.round_stat(cpu_utilization)} %' \
                              f'\n CPU Load: {self.round_stat(cpu_usage)}' \
                              f'\n Mem Usage: {self.round_stat(memory_usage)} %' \
                              f'\n Temp: {temp}' \
                              f'\n Disk Usage: {self.round_stat(disk_usage)} %' \
                              f'\n Internal IP address: {self._host_ip_address}' \
                              f'\n External IP address: {external_ip_address}' \
                              f'\n MAC address: {self._mac_address} \n' \
                              f'\n Screen Summary:\n {screen_summary}\n'
        return server_stats_report

    def _send_server_data(self) -> None:
        self._send_chat_data(f'Ok, getting {self._host_name} stats 🤖')
        self._send_chat_data(self._get_server_data())

    def _send_chat_data(self, chat_message: str):
        self._socket_network.send_message(self._network_commons.get_chat_message_category(), chat_message)


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
