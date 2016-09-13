import os

from commons import run_command, raise_if_not_run_as_root, write_text_to_file
from wrappers import APT, GIT


COMMAND_PIP_INSTALL = 'pip3 install {packages}'
COMMAND_DATABASE_CREATE_MYSQL = """\
mysql -u root -p -e \
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


def setup(deb_packages, pip_packages, project_git, project_name, port_number,
          server_address):
    apt = APT()
    apt.install(deb_packages)
    apt.clean()
    run_command(COMMAND_PIP_INSTALL.format(packages=pip_packages))
    run_command('mysql_secure_installation')
    project_root = os.path.join(os.getcwd(), project_name)
    GIT.clone(url=project_git, path=project_root)
    write_text_to_file(
        GUNICORN_UNIT_PATH.format(project_name=project_name),
        GUNICORN_SERVICE_FILE_CONTENT.format(
            project_root=project_root,
            project_name=project_name,
            username='root'
        )
    )
    write_text_to_file(
        NGINX_CONFIG_PATH.format(project_name=project_name),
        NGINX_CONFIG_FILE_CONTENT.format(
            project_root=project_root,
            project_name=project_name,
            port_number=port_number,
            server_address=server_address
        )
    )


if __name__ == '__main__':
    raise_if_not_run_as_root()
    setup(
        CONTAINER_DEB_PACKAGES,
        CONTAINER_PIP_PACKAGES,
        PROJECT_GIT,
        PROJECT_NAME,
        SERVER_PORT,
        SERVER_ADDRESS
    )
