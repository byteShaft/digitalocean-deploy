COMMAND_APT_CLEAN = 'apt clean'
COMMAND_APT_INSTALL = 'apt -y install {packages}'
COMMAND_APT_UPDATE = 'apt update'
COMMAND_APT_UPGRADE = 'apt -y dist-upgrade'
COMMAND_ECHO_TO_FILE = 'sh -c \"echo \'{content}\' >> {output_file}\"'
COMMAND_GIT_CLONE = 'git clone {source} {destination}'
COMMAND_PIP_INSTALL = 'pip3 install {packages}'
COMMAND_LXD_INSTALL = 'snap install lxd'
COMMAND_LXD_INIT = 'lxd init'
COMMAND_LAUNCH_CONTAINER = 'lxc launch {distribution}:{release} {alias}'
COMMAND_EXECUTE_IN_CONTAINER = 'lxc exec {container_name} -- {command}'
COMMAND_DATABASE_CREATE_MYSQL = """\
mysql -u root -p -e \
"CREATE DATABASE {database_name} CHARACTER SET UTF8;\
CREATE USER {database_user}@localhost IDENTIFIED BY '{database_password}';\
GRANT ALL PRIVILEGES ON {database_name}.* TO {database_user}@localhost;\
FLUSH PRIVILEGES;"\
"""

GUNICORN_UNIT_PATH = '/etc/systemd/system/{project_name}-gunicorn.service'
NGINX_CONFIG_PATH = '/etc/nginx/sites-available/{project_name}.conf'

CONTAINER_DEB_PACKAGES = 'python3-pip mysql-server nginx libmysqlclient-dev git'
CONTAINER_PIP_PACKAGES = 'django djangorestframework mysqlclient gunicorn'
CONTAINER_DISTRIBUTION = 'ubuntu'
CONTAINER_DISTRIBUTION_RELEASE = '16.04'
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
