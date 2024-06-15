import time
import logging
from threading import Thread, Lock

import openzwave
from openzwave.network import ZWaveNetwork
from openzwave.option import ZWaveOption
from openzwave.node import ZWaveNode

class Multisense:
    def __init__(self, device_name: str="/dev/ttyACM0", config_fp: str="/home/pi/python-openzwave/openzwave/config") -> None:
        self.device_name = device_name
        self.config_path = config_fp

        self.sensor_data_lock = Lock()
        self.sensor_data = {} # which will be updated on time with thread

    def start_receiving(self):
        options = ZWaveOption(self.device_name, config_path=self.config_path, user_path=".")
        options.set_console_output(False)
        options.lock()

        network = ZWaveNetwork(options)
        network.start()

        while network.state != network.STATE_READY:
            time.sleep(1)
            logging.info("Network not ready...")

        # TODO: receiving data and write into self.sensor_data

        

