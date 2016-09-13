import shlex
import time

from pylxd.client import Client as LXDClient


class LXD(LXDClient):
    def __init__(self):
        super().__init__()

    def wait_for_network(self, name, timeout=10):
        container = ContainerX(self.containers.get(name))
        for i in range(timeout):
            if container.get_ip():
                return
            else:
                time.sleep(1)
        raise RuntimeError(
            'Network interface not up after {} seconds'.format(timeout)
        )

    def exec(self, name, command):
        container = self.containers.get(name)
        container.execute(shlex.split(command))


class ContainerX:
    def __init__(self, container):
        self.container = container

    def get_ip(self):
        container_state = self.container.state()
        return container_state.network['eth0']['addresses'][0]['address']
