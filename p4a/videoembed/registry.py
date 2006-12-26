from BTrees.IOBTree import IOBTree
from zope.component import getMultiAdapter
from zope.component import queryMultiAdapter
from zope.component import getUtility
from zope.component.exceptions import ComponentLookupError
from zope.interface import implements
from p4a.videoembed.interfaces import IEmbedCode
from p4a.videoembed.interfaces import IEmbedCodeConverterRegistry
from p4a.videoembed.interfaces import ILinkProvider


class EmbedConverterEntry(object):
    """An entry in the EmbedCodeConverterRegistry"""
    def __init__(self, name, match_func):
        self.name = name
        if not callable(match_func):
            raise ValueError, "The matching function must be a callable"
        self.match_func = match_func

    def check(self, url):
        return self.match_func(url)

    def get_code(self, url, width):
        return queryMultiAdapter((url, width), IEmbedCode, name=self.name,
                                     default=None)


class EmbedCodeConverterRegistry(object):
    """A simple registry for converters from urls to embed codes

    Let's make a very simple checker and register it with the CA:

      >>> test_check = lambda url: url.startswith('http://blah.com')
      >>> test_convert = lambda url, width: '<embed url="%s" />'%url
      >>> from zope.component import provideAdapter
      >>> provideAdapter(test_convert, (str, int), IEmbedCode, name='test')

    Now we create our registry and add it there:

      >>> reg = EmbedCodeConverterRegistry()
      >>> reg.register_converter('test', test_check, 100)

    And we try to convert a url:

      >>> print reg.get_code('http://blah.com/foo', 400)
      <embed url="http://blah.com/foo" />
      >>> print reg.get_code('http://bar.com/blah', 300)
      None

    We can register an adapter earlier in the chain and it will win:

      >>> test_check2 = lambda url: url.endswith('.mov')
      >>> test_convert2 = lambda url, width: '<embed url="%s" width="%s" />'%(
      ...                                                         url, width)
      >>> from zope.component import provideAdapter
      >>> provideAdapter(test_convert2, (str, int), IEmbedCode, name='test2')
      >>> reg.register_converter('test2', test_check2, 50)

    Now a url that matches both will be passed to the earlier one:

      >>> print reg.get_code('http://blah.com/foo.mov', 500)
      <embed url="http://blah.com/foo.mov" width="500" />

    A converter registered with the same index gets bumped down to the
    next unoccupied slot (in this case we use the same named adapter
    registered with a different check method):

      >>> test_check3 = lambda url: url.endswith('.avi')
      >>> reg.register_converter('test2', test_check3, 100)
      >>> print reg.get_code('http://blah.com/foo.avi', 500)
      <embed url="http://blah.com/foo.avi" />

    """
    implements(IEmbedCodeConverterRegistry)

    def __init__(self):
        self._registry = IOBTree()

    def register_converter(self, name, match_func, index=0):
        # Registering named adapters instead of direct factories is almost
        # certainly YAGNI, but it's not such a terrible abstraction, IMHO
        reg = self._registry
        check_index = reg.has_key
        # increment the index until we find a suitable one
        while check_index(index):
            index = index + 1
        reg[index] = EmbedConverterEntry(name, match_func)

    def get_code(self, url, width):
        for converter in self._registry.values():
            # Find a converter that likes our url
            if converter.check(url):
                break
        else:
            return None
        return converter.get_code(url, width)

embed_registry = EmbedCodeConverterRegistry()
register_converter = embed_registry.register_converter


def embedCodeAdapter(url, width=425):
    """Queries the registry and returns an embed code"""
    registry = getUtility(IEmbedCodeConverterRegistry)
    return registry.get_code(url, width)


class EmbedCodeView(object):
    """ A simple view that takes optionally takes a url and width and makes them
    into an embed code.  If no url is provided it will attempt to adapt the
    context to ILinkProvider to get the link.  This is mostly for demonstration
    purposes. """

    def get_code(self, width=425, url=None):
        """The method that does 'the work'"""
        if url is None:
            try:
                # Adapt to ILinkProvider to get the link
                url = ILinkProvider(self.context).getLink()
            except (AttributeError, ComponentLookupError):
                return
        return queryMultiAdapter((url, width), IEmbedCode, default=None)

