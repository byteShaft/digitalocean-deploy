import sys

import apt
import aptsources
from softwareproperties.SoftwareProperties import (
    SoftwareProperties,
    shortcut_handler
)
from softwareproperties.shortcuts import ShortcutException

from helpers import raise_if_not_run_as_root


class APT:
    def __init__(self):
        raise_if_not_run_as_root()
        self.apt_cache = apt.Cache()
        self.apt_cache.open()

    def _get_validated_ppa(self, ppa):
        try:
            return shortcut_handler(ppa)
        except ShortcutException as e:
            print(e)
            sys.exit(1)

    def update(self):
        self.apt_cache.update()
        self.apt_cache.open()

    def upgrade(self, dist_upgrade=False):
        self.apt_cache.upgrade(dist_upgrade)

    def clean(self):
        self.apt_cache.clear()

    def install(self, package_list, update=True):
        if update:
            self.update()
        for package_name in package_list:
            package = self.apt_cache[package_name]
            if not package.is_installed:
                package.mark_install()
        self.apt_cache.commit()

    def add_ppa(self, ppa, update=False):
        ppa = self._get_validated_ppa(ppa)
        software_properties = SoftwareProperties()
        distro = aptsources.distro.get_distro()
        distro.get_sources(software_properties.sourceslist)
        software_properties.add_source_from_shortcut(ppa, True)
        if update:
            self.update()
