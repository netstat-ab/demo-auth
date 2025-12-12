__all__ = ['Injectable']

import inspect
import typing

from django.conf import settings
from django.utils.module_loading import import_string


class ImproperlyConfigured(Exception):
    ...


T = typing.TypeVar('T')


class Injectable:
    config_key: str

    @classmethod
    def get_instance(cls: type[T]) -> T:
        import_path = cls._get_import_path()
        try:
            adapter = import_string(import_path)
        except ImportError:
            raise ImproperlyConfigured(f'Failed to import {cls.import_path}')

        assert inspect.isclass(adapter)
        assert not inspect.isabstract(adapter)
        assert issubclass(adapter, cls)
        return adapter()

    @classmethod
    def _get_import_path(cls) -> str:
        config = cls._get_config()
        path = config.get('path')
        assert isinstance(path, str)
        return path

    @classmethod
    def _get_config(cls) -> dict:
        config = getattr(settings, cls.config_key, None)
        assert isinstance(config, dict)
        return config
