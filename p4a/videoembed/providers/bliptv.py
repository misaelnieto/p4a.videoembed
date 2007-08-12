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
      >>> bliptv_check('http://blip.tv/somefile.flv')
      True

    """

    host, path, query, fragment = break_url(url)
    if host.endswith('blip.tv') and path.endswith('.flv'):
        return True
    return False

bliptv_check.index = 1000

EMBED_TEMPLATE = u'''
<embed wmode="transparent"
       src="http://blip.tv/scripts/flash/blipplayer.swf?autoStart=false&file=%(file_url)s&source=3"
       quality="high" width="%(width)s" height="%(height)s" name="movie"
       type="application/x-shockwave-flash"
       pluginspage="http://www.macromedia.com/go/getflashplayer"></embed>
'''

@adapter(str, int)
@implementer(IEmbedCode)
def bliptv_generator(url, width):
    """ A quick check for the right url

    >>> print bliptv_generator('http://blip.tv/file/get/random.flv',
    ...                         width=400)
    <embed wmode="transparent" src="http://blip.tv/scripts/flash/blipplayer.swf?autoStart=false&file=http%3A//blip.tv/file/get/random.flv&source=3" quality="high" width="400" height="326" name="movie" type="application/x-shockwave-flash" pluginspage="http://www.macromedia.com/go/getflashplayer"></embed>

    """
    tag = []
    host, path, query, fragment = break_url(url)
    height = int(round(0.815*width))
    file_id = path.split('/')[-1]

    kwargs = dict(width=width,
                  height=height,
                  file_url=urllib.quote(url))

    return squeeze_xml(EMBED_TEMPLATE % kwargs)
