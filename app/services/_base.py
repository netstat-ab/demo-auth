__all__ = ['Injectable']

import inspect
import typing

from django.conf import settings
from django.utils.module_loading import import_string


class ImproperlyConfigured(Exception):
    ...


T = typing.TypeVar('T')


class Injectable:
    settings_key: str
    default_config = {}

    def __init__(self, config: dict):
        self.config = self.default_config | config

    @classmethod
    def get_instance(cls: type[T]) -> T:
        configuration = getattr(settings, cls.settings_key, None)
        assert isinstance(configuration, dict)

        import_path = configuration.get('path')
        assert isinstance(import_path, str)

        try:
            adapter = import_string(import_path)
        except ImportError:
            raise ImproperlyConfigured(f'Failed to import {cls.import_path}')
        assert inspect.isclass(adapter)
        assert not inspect.isabstract(adapter)
        assert issubclass(adapter, cls)

        config = configuration.get('config')
        assert isinstance(config, dict)
        return adapter(config)
