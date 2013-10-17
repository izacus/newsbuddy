import inspect
import settings
from dogpile.cache import make_region


def get_cache():

    if settings.MEMCACHED_URL:
        region = make_region(
            function_key_generator=fn_key_generator
        ).configure(
            'dogpile.cache.pylibmc',
            expiration_time=7200,
            arguments={
                'url': [settings.MEMCACHED_URL],
                'binary': True,
                'behaviors': {"tcp_nodelay": True, "ketama": True}
            }
        )
    else:
        region = make_region(
            function_key_generator=fn_key_generator
        ).configure(
            'dogpile.cache.memory',
            expiration_time=7200
        )

    return region


# Default key generator doesn't handle unicode at all so use this to convert it beforehand
def fn_key_generator(namespace, fn):
    if namespace is None:
        namespace = '%s:%s' % (fn.__module__, fn.__name__)
    else:
        namespace = '%s:%s|%s' % (fn.__module__, fn.__name__, namespace)

    args = inspect.getargspec(fn)
    has_self = args[0] and args[0][0] in ('self', 'cls')
    def generate_key(*args, **kw):
        if kw:
            raise ValueError("Keyword arguments are not supported.")
        if has_self:
            args = args[1:]

        return namespace + "|" + " ".join(map(to_str, args))
    return generate_key


def to_str(x):
    if isinstance(x, unicode):
        return x.encode("utf-8")
    else:
        return str(x)