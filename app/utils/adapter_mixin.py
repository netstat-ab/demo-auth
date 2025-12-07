__all__ = [
    'AdapterMixin',
    'ImproperlyConfigured',
]

import inspect

from django.conf import settings
from django.utils.module_loading import import_string

from .require import require


class ImproperlyConfigured(Exception):
    ...


def _require(condition):
    require(condition, exception_class=ImproperlyConfigured)


class AdapterMixin:
    adapter_config: str

    @classmethod
    def get_instance(cls):
        config = getattr(settings, cls.adapter_config, None)
        assert isinstance(config, dict)

        path = config.get('path')
        assert isinstance(path, str)

        try:
            adapter_class = import_string(path)
        except ImportError:
            raise ImproperlyConfigured(f'Failed to find adapter {path}')

        assert inspect.isclass(adapter_class)
        assert not inspect.isabstract(adapter_class)
        assert issubclass(adapter_class, cls)

        args = config.get('args', ())
        kwargs = config.get('kwargs', {})
        return adapter_class(*args, **kwargs)
