import urllib
import urllib2
from xml.dom import minidom
from urlparse import urlunsplit
from p4a.videoembed.utils import break_url, xpath_text, xpath_attr, squeeze_xml
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
