from zope.interface import Interface, Attribute
from zope.interface import implements, directlyProvides
from zope.schema import Int, List, Text, TextLine
from zope.schema.interfaces import IText

class IVideoMetadataRetriever(Interface):
    """A simple registry that will return video metadata."""

    def get_metadata(self, url):
        """Returns IVideoMetadata for the given url."""

class IVideoMetadataLookup(Interface):
    """A specific lookup that knows how to build an IVideoMetadata
    implementation.
    """

    def __call__(url):
        """Return IVideoMetadata"""

class IVideoMetadata(Interface):
    """Video metadata."""

    title = TextLine(title=u'Title',
                     description=u'Title of the video.',
                     required=False,
                     readonly=True)

    description = Text(title=u'Description',
                       description=u'Description of the video.',
                       required=False,
                       readonly=True)

    author = TextLine(title=u'Author',
                      description=u'Author of the video.',
                      required=False,
                      readonly=True)

    tags = List(title=u'Tags',
                description=u'Tags of the video.',
                required=False,
                value_type=TextLine(),
                readonly=True)

    thumbnail_url = TextLine(title=u'Thumbnail URL',
                             description=u'A URL pointing to the thumbnail for'
                                         u' the given video.',
                             required=False,
                             readonly=True)

class VideoMetadata(object):
    """Video metadata.

    A simple object which can be instantiated with particular keywords.

      >>> VideoMetadata(thumbnail_url='http://mysite.com/whatever')
      <VideoMetadata thumbnail_url=http://mysite.com/whatever>

    """
    implements(IVideoMetadata)

    def __init__(self, title=None, author=None,
                 description=None, tags=None,
                 thumbnail_url=None):
        self.title = title
        self.author = author
        self.description = description
        self.tags = tags
        self.thumbnail_url = thumbnail_url

    def __str__(self):
        tags = self.tags or []
        tags = ','.join(tags)
        return '<VideoMetadata title=%s; author=%s; description=%s; tags=%s; ' \
               'thumbnail_url=%s>' % (self.title or '',
                                      self.author or '',
                                      self.description or '',
                                      tags,
                                      self.thumbnail_url or '')
    __repr__ = __str__

class IEmbedCode(IText):
    """An html video embed code"""


class IEmbedCodeConverterRegistry(Interface):
    """A registry of embed code adapters which can convert a url from
    a video sharing site to an embed code"""

    def get_code(url, width):
        """Converts the given url into an embed code of the desired width"""


class IURLChecker(Interface):
    """Determines whether a given url corresponds to a particular format"""

    def __call__(url):
        """Returns a boolean indicating whether the given url matches the
        desired format"""

    index = Int(title=u'Index',
                description=u'An index indicating the order in which the check '
                            u'should be run')


class IURLType(Interface):
    """A utility which can indicate the converter to which a given url
    corresponds"""

    def __call__(url):
        """Returns the name of the adapter to be used to convert the passed in
        url"""


class ILinkProvider(Interface):
    """A silly adapter declaring that an object provides a getLink method"""

    def getLink():
        """Returns a url which may correspond to a video embed code"""


class IMediaURL(Interface):
    """A simple interface describing a url to a media file"""

    media_url = Attribute("The url to the media file")
    mimetype = Attribute("The mimetype of the media file")

# A simple decorator to indicate that a function provides a particular interface
# useful for marking utility functions
class provider(object):
    def __init__(self, *interfaces):
        self.interfaces = interfaces

    def __call__(self, ob):
        directlyProvides(ob, *self.interfaces)
        return ob
