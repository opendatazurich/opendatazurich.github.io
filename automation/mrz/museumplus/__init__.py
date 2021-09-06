__version__ = '0.1.2'
__all__ = ['client', 'errors', 'response', 'xmlparse']

from .errors import MuseumPlusError
from .client import MuseumPlusClient

def fulltext_search(base_url, query, **kwargs):  # noqa
    search_params = ['query', 'module', 'limit', 'offset']
    search_kwargs = {k: v for k, v in kwargs.items() if k in search_params}
    search_kwargs['query'] = query

    # assume all others kwargs are for the client
    client_kwargs = {k: v for k, v in kwargs.items() if k not in search_params}
    client_kwargs['base_url'] = base_url

    c = MuseumPlusClient(**client_kwargs)
    return c.search(**search_kwargs)

def search(base_url, field, value, **kwargs):  # noqa
    search_params = ['field', 'value', 'module', 'limit', 'offset']
    search_kwargs = {k: v for k, v in kwargs.items() if k in search_params}
    search_kwargs['field'] = field
    search_kwargs['value'] = value

    # assume all others kwargs are for the client
    client_kwargs = {k: v for k, v in kwargs.items() if k not in search_params}
    client_kwargs['base_url'] = base_url

    c = MuseumPlusClient(**client_kwargs)
    return c.search(**search_kwargs)

