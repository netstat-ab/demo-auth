__all__ = ['require']


def require(
        condition: bool,
        *args: str,
        exception_class: type[Exception] = ValueError,
):
    if not condition:
        raise exception_class(*args)
