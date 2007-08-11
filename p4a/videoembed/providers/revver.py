from xml.dom import minidom
import re
from urlparse import urlunsplit
import urllib2
from urllib import quote, quote_plus
from zope.interface import implements, implementer
from zope.component import adapts, adapter
from p4a.videoembed.utils import break_url
from p4a.videoembed.interfaces import provider
from p4a.videoembed.interfaces import IEmbedCode
from p4a.videoembed.interfaces import IURLChecker
from p4a.videoembed.interfaces import IMediaURL
from p4a.videoembed.interfaces import IVideoMetadataLookup
from p4a.videoembed.interfaces import VideoMetadata

# one.revver.com
@provider(IURLChecker)
def onerevver_check(url):
    host, path, query, fragment = break_url(url)
    if host == 'one.revver.com':
        return True
    return False

onerevver_check.index = 200

FINALDIGITS = re.compile(r'.*?(\d+)$')
WATCHDIGITS = re.compile(r'.*?/(\d+)(?:/\D+?)?(?:/(\d+))?$')

def _onerevver_getids(url):
    host, path, query, fragment = break_url(url)
    video_id = None
    affiliate_id = 0

    # First look for /watch/######
    match = WATCHDIGITS.search(path)
    if not match:
        # Otherwise take the last digits in the url
        # this seems to be going away
        path_elems = path.split('/')
        last_elem = path_elems.pop(-1)
        if not last_elem:
            # in case the url ends with a '/'
            last_elem = path_elems.pop(-1)
        match = FINALDIGITS.match(last_elem)
    if not match and fragment:
        # Sometimes the video_id is the url fragment (strange)
        # fortunately this seems to be going away
        match = FINALDIGITS.match(fragment)
    if match:
        # Take the first matching value
        groups =  match.groups()
        video_id = groups[0]
        if len(groups) > 1:
            affiliate_id = groups[-1] or 0
    return video_id, affiliate_id

@adapter(str, int)
@implementer(IEmbedCode)
def onerevver_generator(url, width):
    """ A quick check for the right url

    >>> print onerevver_generator('http://one.revver.com/something/139266',
    ...                         width=480)
    <script src="http://flash.revver.com/player/1.0/player.js?mediaId:139266;affiliateId:0;height:392;width:480;" type="text/javascript"></script>

    >>> print onerevver_generator('http://one.revver.com/watch/139266',
    ...                         width=480)
    <script src="http://flash.revver.com/player/1.0/player.js?mediaId:139266;affiliateId:0;height:392;width:480;" type="text/javascript"></script>

    >>> print onerevver_generator('http://one.revver.com/other/139266/12234',
    ...                         width=480)
    <script src="http://flash.revver.com/player/1.0/player.js?mediaId:139266;affiliateId:12234;height:392;width:480;" type="text/javascript"></script>

    >>> print onerevver_generator('http://one.revver.com/watch/139266/flv/affiliate/12234',
    ...                         width=480)
    <script src="http://flash.revver.com/player/1.0/player.js?mediaId:139266;affiliateId:12234;height:392;width:480;" type="text/javascript"></script>

    >>> print onerevver_generator('http://one.revver.com/specialpage#139266',
    ...                         width=480)
    <script src="http://flash.revver.com/player/1.0/player.js?mediaId:139266;affiliateId:0;height:392;width:480;" type="text/javascript"></script>

    >>> print  onerevver_generator('http://one.revver.com/watch/66469/flv',
    ...                         width=480)
    <script src="http://flash.revver.com/player/1.0/player.js?mediaId:66469;affiliateId:0;height:392;width:480;" type="text/javascript"></script>
    """

    tag = []
    height = int(round(0.817*width))
    video_id, affiliate_id = _onerevver_getids(url)

    if video_id is None:
        return

    tag.append('<script src="http://flash.revver.com/player/1.0/player.js?'
               'mediaId:%s;affiliateId:%s;height:%s;width:%s;"'
               ' type="text/javascript">'%(video_id, affiliate_id,
                                           height, width))
    tag.append('</script>')
    return u''.join(tag)

class onerevver_mediaurl(object):
    """Returns the quicktime media url for a piece of revver content:

           >>> url = onerevver_mediaurl('http://one.revver.com/other/139266/12234')
           >>> url.media_url
           'http://media.revver.com/qt;sharer=12234/139266.mov'
           >>> url.mimetype
           'video/quicktime'
    """
    implements(IMediaURL)
    adapts(str)
    def __init__(self, url):
        host, path, query, fragment = break_url(url)
        video_id, affiliate_id = _onerevver_getids(url)
        self.mimetype = 'video/quicktime'
        self.media_url = 'http://media.revver.com/qt;sharer=%s/%s.mov'%(
                                                         affiliate_id, video_id)

# The original revver QT embed
@provider(IURLChecker)
def revver_check(url):
    host, path, query, fragment = break_url(url)
    if host.endswith('revver.com'):
        return True
    return False

revver_check.index = 300

@adapter(str, int)
@implementer(IEmbedCode)
def revver_generator(url, width):
    """ A quick check for the right url

    >>> print revver_generator('http://www.revver.com/view.php?id=1111',
    ...                         width=400)
    <object codebase="http://www.apple.com/qtactivex/qtplugin.cab" width="400" classid="clsid:02BF25D5-8C17-4B23-BC80-D3488ABDDC6B" height="340"><param name="src" value="http://media.revver.com/broadcast/1111/video.mov" /><param name="controller" value="True" /><param name="cache" value="False" /><param name="autoplay" value="False" /><param name="kioskmode" value="False" /><param name="scale" value="tofit" /><embed src="http://media.revver.com/broadcast/1111/video.mov" pluginspage="http://www.apple.com/quicktime/download/" scale="tofit" kioskmode="False" qtsrc="http://media.revver.com/broadcast/1111/video.mov" cache="False" width="400" height="340" controller="True" type="video/quicktime" autoplay="False"></embed></object>

    >>> print revver_generator('http://www.revver.com/videos/1111/5544',
    ...                         width=400)
    <object codebase="http://www.apple.com/qtactivex/qtplugin.cab" width="400" classid="clsid:02BF25D5-8C17-4B23-BC80-D3488ABDDC6B" height="340"><param name="src" value="http://media.revver.com/broadcast/1111/video.mov/5544" /><param name="controller" value="True" /><param name="cache" value="False" /><param name="autoplay" value="False" /><param name="kioskmode" value="False" /><param name="scale" value="tofit" /><embed src="http://media.revver.com/broadcast/1111/video.mov/5544" pluginspage="http://www.apple.com/quicktime/download/" scale="tofit" kioskmode="False" qtsrc="http://media.revver.com/broadcast/1111/video.mov/5544" cache="False" width="400" height="340" controller="True" type="video/quicktime" autoplay="False"></embed></object>

    """
    tag = []
    host, path, query, fragment = break_url(url)
    video_ids = []
    video_id = ''
    height = int(round(0.85*width))
    if 'view.php' in path and query.has_key('id'):
        video_id = query['id']
    else:
        path_elems = path.split('/')
        while path_elems:
            # Find all integer elements
            entry = path_elems.pop(-1)
            try:
                video_ids.append(str(int(entry)))
            except ValueError:
                pass
        if video_ids:
            # the first integer in the path is the video id
            video_id = video_ids.pop(-1)
    if not video_id:
        return
    # Handle extra path id information (we don't want to short change any
    # referrers)
    extra = ''
    if video_ids:
        extra = '/' + video_ids[0]
    embed_url=urlunsplit(('http', 'media.revver.com',
                          'broadcast/%s/video.mov%s'%(video_id, extra), '', ''))
    tag.append('<object '
          'codebase="http://www.apple.com/qtactivex/qtplugin.cab" width="%s" '
          'classid="clsid:02BF25D5-8C17-4B23-BC80-D3488ABDDC6B" height="%s">'%(
                      width, height))
    tag.append('<param name="src" value="%s" />'%embed_url)
    tag.append('<param name="controller" value="True" />')
    tag.append('<param name="cache" value="False" />')
    tag.append('<param name="autoplay" value="False" />')
    tag.append('<param name="kioskmode" value="False" />')
    tag.append('<param name="scale" value="tofit" />')
    tag.append('<embed src="%s" '
               'pluginspage="http://www.apple.com/quicktime/download/" '
               'scale="tofit" kioskmode="False" '
               'qtsrc="%s" cache="False" width="%s" height="%s" '
               'controller="True" type="video/quicktime" '
               'autoplay="False"></embed>'%(embed_url, embed_url,
                                            width, height))
    tag.append('</object>')
    return u''.join(tag)

