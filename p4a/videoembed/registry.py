from BTrees.IOBTree import IOBTree
from zope.component import getMultiAdapter
from zope.component import queryMultiAdapter
from zope.component import queryAdapter
from zope.component import getUtility
from zope.component import getUtilitiesFor
from zope.component import adapter
from zope.component import ComponentLookupError
from zope.interface import implements, implementer
from p4a.videoembed.interfaces import provider
from p4a.videoembed.interfaces import IEmbedCode
from p4a.videoembed.interfaces import IEmbedCodeConverterRegistry
from p4a.videoembed.interfaces import ILinkProvider
from p4a.videoembed.interfaces import IURLChecker
from p4a.videoembed.interfaces import IURLType
from p4a.videoembed.interfaces import IMediaURL
from p4a.videoembed.interfaces import IVideoMetadataLookup
from p4a.videoembed.interfaces import IVideoMetadataRetriever

class VideoMetadataRetriever(object):
    """A simple registry that will return video metadata.

    Using a retriever is as simple as instantiating it and asking for
    metadata.  But we have to make sure a IURLType utilility is available
    first.

      >>> from zope.interface import directlyProvides, implements
      >>> from zope.component import provideUtility, provideAdapter
      >>> provideUtility(findURLType, provides=IURLType)

      >>> retriever = VideoMetadataRetriever()
      >>> retriever.get_metadata('http://blah.com') is None
      True

    In orer for the retrieval to really work there must be some initial
    components configured.

      >>> test_check = lambda url: url.startswith('http://blah.com')
      >>> directlyProvides(test_check, IURLChecker)
      >>> provideUtility(test_check, provides=IURLChecker, name='test')

    Of course getting metadata will still return None since there hasn't
    been any lookups registered.

      >>> retriever.get_metadata('http://blah.com') is None
      True

    Now we register a lookup that knows what to do.

      >>> from p4a.videoembed.interfaces import VideoMetadata
      >>> def test_lookup(url):
      ...     return VideoMetadata(thumbnail_url=url+'?thumbnail=boo')
      >>> directlyProvides(test_lookup, IVideoMetadataLookup)
      >>> provideAdapter(test_lookup, adapts=(str,),
      ...                provides=IVideoMetadataLookup, name='test')

      >>> retriever.get_metadata('http://blah.com')
      <VideoMetadata ... thumbnail_url=http://blah.com?thumbnail=boo>

    """
    implements(IVideoMetadataRetriever)

    def get_metadata(self, url):
        name = getUtility(IURLType)(url)
        if name is None:
            return None

        return queryAdapter(url,
                            IVideoMetadataLookup,
                            name=name,
                            default=None)

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

    def get_code(self, url, width):
        url_type = getUtility(IURLType)(url)
        if url_type:
            return queryMultiAdapter((url, width), IEmbedCode, name=url_type,
                                     default=None)


@implementer(IEmbedCode)
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


@adapter(str)
@implementer(IMediaURL)
def mediaURLConverter(url):
    """A simple adapter from a url to a media-file url and mimetype

    Let's make a very simple checker and register it with the CA:

      >>> from zope.interface import directlyProvides
      >>> test_check = lambda url: url.startswith('http://blah.com')
      >>> directlyProvides(test_check, IURLChecker)
      >>> class media_url(object):
      ...     media_url = 'blah.mov'
      ...     mimetype = 'video/quicktime'
      >>> test_convert = lambda url: media_url()
      >>> from zope.component import provideAdapter, provideUtility
      >>> provideAdapter(test_convert, (str,), IMediaURL, name='test')
      >>> provideUtility(test_check, provides=IURLChecker, name='test')

    We need to register the
    URLType utility:

      >>> provideUtility(findURLType, provides=IURLType)

    And we try to convert a url:

      >>> media_url = mediaURLConverter('http://blah.com/foo')
      >>> media_url.media_url
      'blah.mov'
      >>> media_url.mimetype
      'video/quicktime'

    """

    url_type = getUtility(IURLType)(url)
    if url_type:
        return queryAdapter(url, IMediaURL, name=url_type, default=None)
