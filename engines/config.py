import os
import yaml


class Config:
    def __init__(self, config_path='data/config.yaml'):
        self._path = config_path
        self._data = {}
        if os.path.exists(config_path):
            with open(config_path, 'r', encoding='utf-8') as f:
                self._data = yaml.safe_load(f) or {}

    def get(self, key, default=None):
        keys = key.split('.')
        value = self._data
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
                if value is None:
                    return default
            else:
                return default
        return value

    def reload(self):
        self.__init__(self._path)
