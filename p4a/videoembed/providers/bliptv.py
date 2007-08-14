import urllib
import urllib2
from xml.dom import minidom
from urlparse import urlunsplit
from p4a.videoembed.utils import (break_url, xpath_text,
                                  xpath_attr, squeeze_xml,
                                  remote_content)
from p4a.videoembed.interfaces import provider
from p4a.videoembed.interfaces import IEmbedCode
from p4a.videoembed.interfaces import IMediaURL
from p4a.videoembed.interfaces import IURLChecker
from p4a.videoembed.interfaces import IVideoMetadataLookup
from p4a.videoembed.interfaces import VideoMetadata
from zope.interface import implements, implementer
from zope.component import adapts, adapter

@provider(IURLChecker)
def bliptv_check(url):
    """Check to see if the given url is blip.tv style.

      >>> bliptv_check('http://someplace.com')
      False
      >>> bliptv_check('http://blip.tv/file/somefile.flv')
      False
      >>> bliptv_check('http://blip.tv/file/1234')
      True

    """

    host, path, query, fragment = break_url(url)
    if host.endswith('blip.tv'):
        pieces = path.split('/')
        if len(pieces) == 3 \
               and pieces[0] == '' \
               and pieces[1] == 'file' \
               and pieces[2].isdigit():
            return True
    return False

bliptv_check.index = 1000

EMBED_HTML = u'''
<object
    type="application/x-shockwave-flash"
    classid="clsid:d27cdb6e-ae6d-11cf-96b8-444553540000"
    codebase="http://fpdownload.macromedia.com/pub/shockwave/cabs/flash/swflash.cab#version=8,0,0,0"
    width="%(width)s"
    height="%(height)s"
    id="showplayer"
    allowfullscreen="true"
    allowscriptaccess="always">
    <param name="movie"
        value="http://blip.tv/scripts/flash/showplayer.swf?file=%(file_url)s" />
     <param name="allowscriptaccess" value="always" />
     <param name="allowfullscreen" value="true" />
     <param name="quality" value="best" />
     <param name="wmode" value="window" />
     <embed
        type="application/x-shockwave-flash"
        width="%(width)s"
        height="%(height)s"
        id="shoplayerembed"
        src="http://blip.tv/scripts/flash/showplayer.swf?file=%(file_url)s"
        pluginspage="http://www.macromedia.com/go/getflashplayer"
        wmode="window"
        allowfullscreen="true"
        allowscriptaccess="always"
     />
</object>
'''
EMBED_HTML = squeeze_xml(EMBED_HTML)

def _rss_url(url):
    """Return RSS url for the video url.

      >>> _rss_url('http://someplace.com')
      'http://someplace.com?skin=rss'

      >>> _rss_url('http://someplace.com?arg1=foo')
      'http://someplace.com?arg1=foo&skin=rss'
    """

    host, path, query, fragment = break_url(url)
    file_url = url
    if len(query.keys()) == 0:
        file_url += '?skin=rss'
    else:
        file_url += '&skin=rss'
    return file_url

@adapter(str, int)
@implementer(IEmbedCode)
def bliptv_generator(url, width):
    """ A quick check for the right url

    >>> html = bliptv_generator('http://blip.tv/file/get/random.flv',
    ...                         width=400)
    >>> 'showplayer.swf?file=http%3A//blip.tv/file/get/random.flv' in html
    True

    """
    tag = []
    host, path, query, fragment = break_url(url)
    height = int(round(0.815*width))

    file_url = _rss_url(url)

    kwargs = dict(width=width,
                  height=height,
                  file_url=urllib.quote(file_url))

    return EMBED_HTML % kwargs

def _populate_bliptv_data(rss, metadata):
    """Parse bliptv video rss and pull out the metadata information.

      >>> rss = '''<?xml version="1.0" ?>
      ... <rss version="2.0"
      ...      xmlns:media="http://search.yahoo.com/mrss/"
      ...      xmlns:blip="http://blip.tv/dtd/blip/1.0">
      ... <channel>
      ...     <item>
      ...       <title>
      ...         Random Video
      ...       </title>
      ...       <blip:user>someuser</blip:user>
      ...       <blip:puredescription>
      ...         This is a random description.
      ...       </blip:puredescription>
      ...       <media:keywords>abc, def</media:keywords>
      ...       <media:thumbnail url="http://someurl.com/somefile.jpg" />
      ...     </item>
      ...   </channel>
      ... </rss>
      ... '''

      >>> metadata = VideoMetadata()
      >>> _populate_bliptv_data(rss, metadata)

      >>> metadata.title
      u'Random Video'
      >>> metadata.description
      u'This is a random description.'
      >>> metadata.tags
      set([u'abc', u'def'])
      >>> metadata.thumbnail_url
      u'http://someurl.com/somefile.jpg'
      >>> metadata.author
      u'someuser'

    """
    doc = minidom.parseString(rss)
    metadata.thumbnail_url = xpath_attr( \
        doc, u'rss/channel/item/media:thumbnail', 'url')
    metadata.title = xpath_text( \
        doc, u'rss/channel/item/title')
    metadata.author = xpath_text( \
        doc, u'rss/channel/item/blip:user')
    metadata.description = xpath_text( \
        doc, u'rss/channel/item/blip:puredescription')

    keywordtext = xpath_text( \
        doc, u'rss/channel/item/media:keywords') or ''
    metadata.tags = set([x.strip()
                         for x in keywordtext.split(',') if x.strip()])

@adapter(str)
@implementer(IVideoMetadataLookup)
def bliptv_metadata_lookup(url):
    """Retrieve metadata information regarding a bliptv video url."""

    data = VideoMetadata()
    rss = remote_content(_rss_url(url))
    _populate_bliptv_data(rss, data)

    return data
