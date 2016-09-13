import time

from pylxd.client import Client as LXDClient


class LXD(LXDClient):
    def __init__(self, name):
        self.container = self.containers.get(name)

    def _get_ip_from_state(self, state):
        return state.network['eth0']['addresses'][0]['address']

    def wait_for_network(self, timeout=10):
        for i in range(timeout):
            ip = self._get_ip_from_state(self.container.state())
            if not ip:
                time.sleep(1)
        raise RuntimeError(
            "Network interface not up after {} seconds".format(timeout)
        )
