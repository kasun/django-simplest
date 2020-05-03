from .router import router
from .serializer import Serializer


__version__ = '0.1'
__all__ = [router]


def serialize(query_set, fields=None, include_id=True):
    se = Serializer(query_set, fields, include_id)
    return se.serialize()
