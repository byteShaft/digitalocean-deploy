from lxd_wrapper import LXD

from commons import raise_if_not_run_as_root, run_command
from wrappers.apt import APT

COMMAND_LXD_INIT = 'lxd init'
COMMAND_LAUNCH_CONTAINER = 'lxc launch images:{distro}/{release} {name}'
PPA_LXD_STABLE = 'ppa:ubuntu-lxc/lxd-stable'


def _update_host_packages():
    apt = APT()
    apt.add_ppa(PPA_LXD_STABLE, update=True)
    apt.upgrade(dist_upgrade=True)
    apt.clean()


def _initialize_lxd():
    run_command(COMMAND_LXD_INIT)


def setup_host():
    _update_host_packages()
    _initialize_lxd()


def _launch_container(name, distro, release):
    run_command(
        COMMAND_LAUNCH_CONTAINER.format(
            name=name, distro=distro, release=release
        )
    )
    lxd = LXD()
    lxd.wait_for_network(name)


def setup_container(name, distro, release):
    _launch_container(name, distro, release)


if __name__ == '__main__':
    raise_if_not_run_as_root()
    setup_host()
    setup_container('x', 'ubuntu', 'xenial')
