#!/usr/bin/python3

import os
import subprocess
import shlex
import time

COMMAND_APT_CLEAN = 'apt clean'
COMMAND_APT_INSTALL = 'apt -y install {packages}'
COMMAND_APT_UPDATE = 'apt update'
COMMAND_APT_UPGRADE = 'apt -y dist-upgrade'
COMMAND_ECHO_TO_FILE = 'sh -c \"echo \'{content}\' >> {output_file}\"'
COMMAND_GIT_CLONE = 'git clone {source} {destination}'
COMMAND_PIP_INSTALL = 'pip3 install {packages}'
COMMAND_LXD_PPA_ADD = 'add-apt-repository -y ppa:ubuntu-lxc/lxd-stable'
COMMAND_LXD_INIT = 'lxd init'
COMMAND_LAUNCH_CONTAINER = 'lxc launch images:{distribution}/{release} {alias}'
COMMAND_EXECUTE_IN_CONTAINER = 'lxc exec {container_name} -- {command}'
COMMAND_DATABASE_CREATE_MYSQL = """\
mysql -u root -p{mysql_password} -e \
"CREATE DATABASE {database_name} CHARACTER SET UTF8; \
CREATE USER {database_user}@localhost IDENTIFIED BY '{database_password}'; \
GRANT ALL PRIVILEGES ON {database_name}.* TO {database_user}@localhost; \
FLUSH PRIVILEGES;"\
"""

GUNICORN_UNIT_PATH = '/etc/systemd/system/{project_name}-gunicorn.service'
NGINX_CONFIG_PATH = '/etc/nginx/sites-available/{project_name}.conf'

CONTAINER_DEB_PACKAGES = 'python3-pip mysql-server nginx libmysqlclient-dev ' \
                         'git'
CONTAINER_PIP_PACKAGES = 'django djangorestframework mysqlclient gunicorn'
CONTAINER_DISTRIBUTION = 'ubuntu'
CONTAINER_DISTRIBUTION_RELEASE = 'xenial'
CONTAINER_NAME = CONTAINER_DISTRIBUTION_RELEASE

PROJECT_GIT = 'https://github.com/byteShaft/brochure-service.git'
PROJECT_NAME = 'brochure_service'
APP_NAME = 'brochure_app'

SERVER_PORT = 80
SERVER_ADDRESS = '0.0.0.0'

GUNICORN_SERVICE_FILE_CONTENT = """
[Unit]
Description={project_name} gunicorn daemon
After=network.target

[Service]
User={username}
Group=nginx
WorkingDirectory={project_root}
ExecStart=/usr/local/bin/gunicorn --workers 3 --bind unix:{project_root}/\
{project_name}.sock {project_name}.wsgi:application

[Install]
WantedBy=multi-user.target
"""
NGINX_CONFIG_FILE_CONTENT = """
server {{
    listen {port_number};
    server_name {server_address};

    location = /favicon.ico {{ access_log off; log_not_found off; }}
    location /static/ {{
        root {project_root};
    }}
    location /media/ {{
        root {project_root};
    }}
    location / {{
        proxy_pass http://unix:{project_root}/{project_name}.sock;
    }}
}}
"""


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
            server_address
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


if __name__ == '__main__':
    setup_host()
    container = Container(CONTAINER_NAME)
    container.initialize(
        CONTAINER_DISTRIBUTION,
        CONTAINER_DISTRIBUTION_RELEASE
    )
    container.setup(
        CONTAINER_DEB_PACKAGES,
        CONTAINER_PIP_PACKAGES,
        PROJECT_GIT,
        PROJECT_NAME,
        SERVER_PORT,
        SERVER_ADDRESS
    )
