from zope.interface import Interface
from zope.schema.interfaces import IText

class IEmbedCode(IText):
    """An html video embed code"""


class IEmbedCodeConverterRegistry(Interface):
    """A registry of embed code adapters which can convert a url from
    a video sharing site to an embed code"""

    def register_converter(name, match_func, index):
        """Register a named adapter for converting urls to embed codes,
        requres the name of an existing adapter, a function that checks
        urls for correspondence to the particular named adapter"""

    def get_code(url, width):
        """Converts the given url into an embed code of the desired width"""

class ILinkProvider(Interface):
    """A silly adapter declaring that an object provides a getLink method"""

    def getLink():
        """Returns a url which may correspond to a video embed code"""
