from xml.dom import minidom
import re
from urlparse import urlunsplit
import urllib2
from urllib import quote, quote_plus
from zope.interface import implements, implementer
from zope.component import adapts, adapter
from p4a.videoembed.interfaces import provider
from p4a.videoembed.interfaces import IEmbedCode
from p4a.videoembed.interfaces import IURLChecker
from p4a.videoembed.interfaces import IMediaURL
from p4a.videoembed.interfaces import IVideoMetadataLookup
from p4a.videoembed.interfaces import VideoMetadata

# Any flv (only accepts direct urls to flv videos!) uses blip's player
@provider(IURLChecker)
def flv_check(url):
    host, path, query, fragment = break_url(url)
    if path.endswith('.flv'):
        return True
    return False

flv_check.index = 10100

# FLV player url (requires the flv player from http://www.jeroenwijering.com/)
# indicate the url to your copy of that player here

FLV_PLAYER_URL = "http://location/path/to/flvplayer.swf"

@adapter(str, int)
@implementer(IEmbedCode)
def flv_generator(url, width):
    """ A quick check for the right url, this one requires a direct
    flv link:

    >>> print flv_generator('http://blip.tv/file/get/SomeVideo.flv', width=400)
    <embed src="http://location/path/to/flvplayer.swf" width="400" height="320" bgcolor="#FFFFFF" type="application/x-shockwave-flash" pluginspage="http://www.macromedia.com/go/getflashplayer" flashvars="file=http://blip.tv/file/get/SomeVideo.flv&autostart=true"></embed>

    """
    tag = []
    height = int(round(0.8*width))

    video_url = url
    tag.append('<embed src="%s" width="%s" height="%s" bgcolor="#FFFFFF" '
        'type="application/x-shockwave-flash" '
        'pluginspage="http://www.macromedia.com/go/getflashplayer" '
        'flashvars="file=%s&autostart=true">'%(FLV_PLAYER_URL, width, height,
                                                video_url))
    tag.append('</embed>')
    return u''.join(tag)
