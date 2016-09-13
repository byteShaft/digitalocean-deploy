import os
import shlex
import subprocess


def has_root_permission():
    return os.getegid() == 0


def raise_if_not_run_as_root():
    if not has_root_permission():
        raise RuntimeError("Script must be run with sudo")


def run_command(command):
    subprocess.check_call(shlex.split(command))


def write_text_to_file(path, content):
    with open(path, 'w') as f:
        f.write(content)
