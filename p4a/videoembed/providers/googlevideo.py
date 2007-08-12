import urllib2
from xml.dom import minidom
from urlparse import urlunsplit
from p4a.videoembed.utils import break_url, xpath_text, xpath_attr
from p4a.videoembed.interfaces import provider
from p4a.videoembed.interfaces import IEmbedCode
from p4a.videoembed.interfaces import IMediaURL
from p4a.videoembed.interfaces import IURLChecker
from p4a.videoembed.interfaces import IVideoMetadataLookup
from p4a.videoembed.interfaces import VideoMetadata
from zope.interface import implements, implementer
from zope.component import adapts, adapter

# Google video
@provider(IURLChecker)
def google_check(url):
    """Check to see if the given url matches.

      >>> google_check('http://someplace.com')
      False
      >>> google_check('http://video.google.ca/?docid=foo')
      True

    """

    host, path, query, fragment = break_url(url)
    if host.startswith('video.google.') and query.has_key('docid'):
        return True
    return False

google_check.index = 400

def _get_google_rss(url):
    """Retrieve the remote RSS XML for the given video url."""
    host, path, query, fragment = break_url(url)
    video_id = query['docid']
    fin = urllib2.urlopen('http://'+host+'/videofeed?docid='+video_id)
    rss = fin.read()
    fin.close()
    return rss

def _populate_google_data(rss, metadata):
    """Parse google video rss and pull out the metadata information.

      >>> rss = '''<?xml version="1.0" ?>
      ... <rss version="2.0" xmlns:media="http://search.yahoo.com/mrss/" xmlns:openSearch="http://a9.com/-/spec/opensearchrss/1.0/">
      ... <channel>
      ...     <title>
      ...       Google Video - The Big Experiment &amp; Rocky
      ...     </title>
      ...     <link>
      ...       http://video.google.com/videoplay?docid=-274981837129821058
      ...     </link>
      ...     <item>
      ...       <author>
      ...         Jon Doe
      ...       </author>
      ...       <media:group>
      ...         <media:title>
      ...           The Big Experiment &amp; Rocky
      ...         </media:title>
      ...         <media:description>
      ...           hello world
      ...
      ...           Keywords:  eepybird eepy bird
      ...         </media:description>
      ...         <media:thumbnail height="240" url="http://video.google.com/somepath.jpg" width="320"/>
      ...       </media:group>
      ...     </item>
      ...   </channel>
      ... </rss>
      ... '''

      >>> metadata = VideoMetadata()
      >>> _populate_google_data(rss, metadata)

      >>> metadata.title
      u'The Big Experiment & Rocky'
      >>> metadata.description
      u'hello world'
      >>> metadata.tags
      set([u'eepybird', u'bird', u'eepy'])
      >>> metadata.thumbnail_url
      u'http://video.google.com/somepath.jpg'
      >>> metadata.author
      u'Jon Doe'

    """
    doc = minidom.parseString(rss)
    metadata.thumbnail_url = xpath_attr( \
        doc, u'rss/channel/item/media:group/media:thumbnail', 'url')
    metadata.title = xpath_text( \
        doc, u'rss/channel/item/media:group/media:title')
    metadata.author = xpath_text( \
        doc, u'rss/channel/item/author')

    text = xpath_text( \
        doc, u'rss/channel/item/media:group/media:description')
    description = None
    tags = None
    if text:
        description = text
        pos = description.find('Keywords:')
        if pos > -1 and len(description) > pos + 9:
            keywordblurb = description[pos+9:]
            tags = set([x.strip() for x in keywordblurb.split(' ')
                        if x.strip()])
        if pos > -1:
            description = description[:pos]
        description = description.strip()

    metadata.description = description
    metadata.tags = tags

@adapter(str)
@implementer(IVideoMetadataLookup)
def google_metadata_lookup(url):
    """Retrieve metadata information regarding a google video url."""

    data = VideoMetadata()
    rss = _get_google_rss(url)
    _populate_google_data(rss, data)

    return data

@adapter(str, int)
@implementer(IEmbedCode)
def google_generator(url, width):
    """ A quick check for the right url

    >>> print google_generator('http://video.google.com/videoplay?docid=-18281',
    ...                         width=400)
    <embed style="width:400px; height:326px;" id="VideoPlayback" type="application/x-shockwave-flash" src="http://video.google.com/googleplayer.swf?docId=-18281"></embed>

    """
    tag = []
    host, path, query, fragment = break_url(url)
    height = int(round(0.815*width))
    video_id = query['docid']
    tag.append('<embed style="width:%spx; height:%spx;" '
               'id="VideoPlayback" type="application/x-shockwave-flash" '
               'src="http://video.google.com/googleplayer.swf?docId=%s">'%(
        width, height, video_id
        ))
    tag.append('</embed>')
    return u''.join(tag)
