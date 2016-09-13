import os

import host
from commons import run_command

COMMAND_EXECUTE_IN_CONTAINER = 'lxc exec {container_name} -- {command}'
COMMAND_PUSH_IN_CONTAINER = 'lxc file push {source} {container_name}/{target}'

DISTRO = 'ubuntu'
RELEASE = 'xenial'
NAME = 'xenial'


def _push_container_setup_script(name, source, target):
    run_command(
        COMMAND_PUSH_IN_CONTAINER.format(
            container_name=name,
            source=source,
            target=target
        )
    )


def setup_container(name, source, target):
    _push_container_setup_script(name, source, target)
    run_command(
        COMMAND_EXECUTE_IN_CONTAINER.format(
            container_name=name,
            command='{} {}'.format('python3', target)
        )
    )


if __name__ == '__main__':
    # host.setup()
    host.launch_container(NAME, DISTRO, RELEASE)
    setup_container(NAME, os.path.abspath('container.py'), '/tmp/container.py')
