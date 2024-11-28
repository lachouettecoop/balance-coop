import logging
import socket
from threading import Thread
from time import sleep

from api import config
from api.scale.message import Message
from api.scale.screen import Screen


class Scale(Thread):
    def __init__(self, socket_io):
        super(Scale, self).__init__()
        self._socket_io = socket_io
        self._keep_running = True
        self._sock = None
        self._healthy = False
        self._weight = 0.0
        self._tare = 0.0
        self._last_status = {}

    def __exit__(self, exc_type, exc_value, traceback):
        self.stop()

    def run(self):
        s = Screen()
        while self._keep_running:
            if config.core.mock_scale:
                import random

                self._healthy = True
                #self._weight = 1.2
                #self._tare = 0
                self._weight = random.random()
                self._tare = random.random()
                self._notify()
            else:
                try:
                    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as self._sock:
                        ip = config.scale.ip.split(":")[0]
                        port = int(config.scale.ip.split(":")[1])
                        self._sock.connect((ip, port))
                        while self._keep_running:
                            m = Message(self._sock)
                            m.read()
                            self._healthy = True
                            if m.is_rle:
                                if m.header == 41:
                                    s.rle_shorts_to_grid(m.coord, m.data, m.data_length)
                                else:
                                    s.rle_bytes_to_grid(m.coord, m.data, m.data_length)
                            elif m.is_bin:
                                s.bin_to_grid(m.coord, m.data, m.data_length)

                            self._weight = s.weight
                            self._tare = s.tare
                            self._notify()
                            logging.debug(f"Weight: {self._weight:.3f} - Tare: {self._tare:.3f}")
                except Exception as e:
                    self._notify()
                    self.clear()
                    if self._healthy:
                        logging.error(e)
                        self._healthy = False
            sleep(2)

    @property
    def status(self):
        return {
            "healthy": self._healthy,
            "weight": self._weight if self._healthy else 0.0,
            "tare": self._tare if self._healthy else 0.0,
        }

    def _notify(self):
        if self._last_status != self.status:
            self._socket_io.emit(
                "scale_status",
                self.status,
            )
            self._last_status = self.status

    def clear(self):
        if self._sock:
            self._sock.close()
            self._sock = None

    def stop(self):
        self._keep_running = False
        self.clear()
