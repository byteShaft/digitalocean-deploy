from wrappers import APT, LXD
from commons import run_command

COMMAND_LXD_INIT = 'lxd init'
COMMAND_LAUNCH_CONTAINER = 'lxc launch images:{distro}/{release} {name}'
PPA_LXD_STABLE = 'ppa:ubuntu-lxc/lxd-stable'


def _update_lxd(ppa=PPA_LXD_STABLE):
    apt = APT()
    apt.add_ppa(ppa, update=True)
    apt.upgrade(dist_upgrade=True)
    apt.clean()


def _initialize_lxd():
    run_command(COMMAND_LXD_INIT)


def setup():
    _update_lxd()
    _initialize_lxd()


def launch_container(name, distro, release):
    """Launch the container with given parameters."""
    run_command(
        COMMAND_LAUNCH_CONTAINER.format(
            name=name, distro=distro, release=release
        )
    )
    lxd = LXD()
    lxd.wait_for_network(name)
