from BTrees.IOBTree import IOBTree
from zope.component import getMultiAdapter
from zope.component import queryMultiAdapter
from zope.component import getUtility
from zope.component import getUtilitiesFor
from zope.component.exceptions import ComponentLookupError
from zope.interface import implements
from p4a.videoembed.interfaces import provider
from p4a.videoembed.interfaces import IEmbedCode
from p4a.videoembed.interfaces import IEmbedCodeConverterRegistry
from p4a.videoembed.interfaces import IURLType
from p4a.videoembed.interfaces import IURLChecker

@provider(IURLType)
def findURLType(url):
    """A means of finding the name of the adapter to use to convert a given
    URL"""
    checkers = [u for u in getUtilitiesFor(IURLChecker)]
    # sort on explicit index
    checkers.sort(key=lambda u: getattr(u[1], 'index', 100000))
    for name, check in checkers:
        if check(url):
            return name
    return None

class EmbedCodeConverterUtility(object):
    """A simple registry for converters from urls to embed codes

    Let's make a very simple checker and register it with the CA:

      >>> from zope.interface import directlyProvides
      >>> test_check = lambda url: url.startswith('http://blah.com')
      >>> directlyProvides(test_check, IURLChecker)
      >>> test_convert = lambda url, width: '<embed url="%s" />'%url
      >>> from zope.component import provideAdapter, provideUtility
      >>> provideAdapter(test_convert, (str, int), IEmbedCode, name='test')
      >>> provideUtility(test_check, provides=IURLChecker, name='test')

    We need an instance of this utility and also to register the
    URLType utility:

      >>> provideUtility(findURLType, provides=IURLType)
      >>> util = EmbedCodeConverterUtility()

    And we try to convert a url:

      >>> print util.get_code('http://blah.com/foo', 400)
      <embed url="http://blah.com/foo" />
      >>> print util.get_code('http://bar.com/blah', 300)
      None

    We can register an adapter earlier in the chain and it will win:

      >>> test_check2 = lambda url: url.endswith('.mov')
      >>> test_check2.index = 100
      >>> directlyProvides(test_check2, IURLChecker)
      >>> test_convert2 = lambda url, width: '<embed url="%s" width="%s" />'%(
      ...                                                         url, width)
      >>> from zope.component import provideAdapter
      >>> provideAdapter(test_convert2, (str, int), IEmbedCode, name='test2')
      >>> provideUtility(test_check2, provides=IURLChecker, name='test2')

    Now a url that matches both will be passed to the earlier one:

      >>> print util.get_code('http://blah.com/foo.mov', 500)
      <embed url="http://blah.com/foo.mov" width="500" />

    """
    implements(IEmbedCodeConverterRegistry)

    def __init__(self):
        self._registry = IOBTree()

    def get_code(self, url, width):
        url_type = getUtility(IURLType)(url)
        if url_type:
            return queryMultiAdapter((url, width), IEmbedCode, name=url_type,
                                     default=None)


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

