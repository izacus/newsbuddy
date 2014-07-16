import inspect
from sqlalchemy.orm.interfaces import MapperOption
import settings
from dogpile.cache import make_region


def get_cache():
    if settings.REDIS_CONFIG and settings.REDIS_CONFIG.get("host"):
        region = make_region(
            function_key_generator=fn_key_generator
        ).configure(
            'dogpile.cache.redis',
            expiration_time=7200,
            arguments={
                'host': settings.REDIS_CONFIG["host"],
                'port': settings.REDIS_CONFIG["port"],
                'db': settings.REDIS_CONFIG["db"],
                'distributed_lock': True
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

class FromCache(MapperOption):
    """Specifies that a Query should load results from a cache."""

    propagate_to_loaders = False

    def __init__(self, region="default", cache_key=None):
        """Construct a new FromCache.

        :param region: the cache region.  Should be a
        region configured in the dictionary of dogpile
        regions.

        :param cache_key: optional.  A string cache key
        that will serve as the key to the query.   Use this
        if your query has a huge amount of parameters (such
        as when using in_()) which correspond more simply to
        some other identifier.

        """
        self.region = region
        self.cache_key = cache_key

    def process_query(self, query):
        """Process a Query during normal loading operation."""
        query._cache_region = self
