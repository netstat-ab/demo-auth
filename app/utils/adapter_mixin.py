__all__ = [
    'AdapterMixin',
    'ImproperlyConfigured',
]

import inspect

from django.utils.module_loading import import_string

from .require import require


class ImproperlyConfigured(Exception):
    ...


def _require(condition):
    require(condition, exception_class=ImproperlyConfigured)


class AdapterMixin:
    adapter_class: str

    @classmethod
    def get_instance(cls):
        adapter_class = getattr(cls, 'adapter_class')
        _require(isinstance(adapter_class, str))

        try:
            adapter_class = import_string(adapter_class)
        except ImportError:
            raise ImproperlyConfigured

        _require(inspect.isclass(adapter_class))
        _require(not inspect.isabstract(adapter_class))
        _require(issubclass(adapter_class, cls))

        return adapter_class()
