#!/usr/bin/python3

import os
import subprocess
import shlex
import time

from constants import *


def _run_command(command):
    subprocess.check_call(shlex.split(command))


def setup_host():
    _run_command(COMMAND_LXD_PPA_ADD)
    _run_command(COMMAND_APT_UPDATE)
    _run_command(COMMAND_APT_UPGRADE)
    _run_command(COMMAND_APT_CLEAN)
    _run_command(COMMAND_LXD_INIT)


class Container:
    def __init__(self, container_name):
        self.container_name = container_name

    def _run_command(self, command):
        _run_command(
            COMMAND_EXECUTE_IN_CONTAINER.format(
                container_name=self.container_name,
                command=command
            )
        )

    def initialize(self, distribution, release):
        _run_command(
            COMMAND_LAUNCH_CONTAINER.format(
                distribution=distribution,
                release=release,
                alias=self.container_name
            )
        )
        # FIXME: find a way to wait for internet connectivity in container.
        time.sleep(4)

    def setup(
            self,
            deb_packages,
            pip_packages,
            project_git,
            project_name,
            port_number,
            server_address,
            database_name,
            database_user,
            database_pass,
    ):
        self._run_command(COMMAND_APT_INSTALL.format(packages=deb_packages))
        self._run_command(COMMAND_APT_CLEAN)
        self._run_command(COMMAND_PIP_INSTALL.format(packages=pip_packages))
        self._run_command('mysql_secure_installation')
        self._run_command(
            COMMAND_GIT_CLONE.format(
                source=project_git,
                destination=project_name
            )
        )
        self._run_command(
            COMMAND_ECHO_TO_FILE.format(
                content=GUNICORN_SERVICE_FILE_CONTENT.format(
                    project_root=os.path.join('/root', project_name),
                    project_name=project_name,
                    username='root'
                ),
                output_file=GUNICORN_UNIT_PATH.format(
                    project_name=project_name
                ),
            )
        )
        self._run_command(
            COMMAND_ECHO_TO_FILE.format(
                content=NGINX_CONFIG_FILE_CONTENT.format(
                    project_root=os.path.join('/root', project_name),
                    project_name=project_name,
                    port_number=port_number,
                    server_address=server_address
                ),
                output_file=NGINX_CONFIG_PATH.format(
                    project_name=project_name
                ),
            )
        )
        print("Enter mysql root password below.")
        self._run_command(COMMAND_DATABASE_CREATE_MYSQL.format(
                database_name=database_name,
                database_user=database_user,
                database_password=database_pass
            )
        )


if __name__ == '__main__':
    setup_host()
    container = Container(CONTAINER_NAME)
    container.initialize(
        CONTAINER_DISTRIBUTION,
        CONTAINER_DISTRIBUTION_RELEASE
    )
    DATABASE_NAME = 'mydb'
    DATABASE_PASS = 'secret'
    DATABASE_USER = 'ubuntuone'
    container.setup(
        CONTAINER_DEB_PACKAGES,
        CONTAINER_PIP_PACKAGES,
        PROJECT_GIT,
        PROJECT_NAME,
        SERVER_PORT,
        SERVER_ADDRESS,
        DATABASE_NAME,
        DATABASE_USER,
        DATABASE_PASS
    )
