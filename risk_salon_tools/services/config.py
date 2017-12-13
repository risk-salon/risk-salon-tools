import os
import yaml

from six import iteritems


class Settings(object):
    _config_path = os.path.expanduser('~/.risk_salon_tools/config.yaml')

    def __init__(self):
        self._settings = {}
        with open(self._config_path, "r") as f:
            settings = yaml.load(f)
            assert type(settings) is dict

            for k, v in iteritems(settings):
                self._settings[k] = v

    def get(self, key):
        return self._settings[key]
