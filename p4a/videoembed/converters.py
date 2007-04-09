import re
from urlparse import urlsplit, urlunsplit
from urllib import quote, quote_plus
from zope.interface import implements, implementer
from zope.component import adapts, adapter
from p4a.videoembed._cache import BufferCache
from p4a.videoembed.interfaces import provider
from p4a.videoembed.interfaces import IEmbedCode
from p4a.videoembed.interfaces import IURLChecker
from p4a.videoembed.interfaces import IMediaURL

def _break_url(url):
    """A helper method for extracting url parts and parsing the query string

    >>> _break_url('http://www.blah.com/foo/bar?blah=2&blee=bix#1234')
    ('www.blah.com', '/foo/bar', {'blee': 'bix', 'blah': '2'}, '1234')

    Needs to do url quoting:

    >>> _break_url('http://www.blah.com/foo / bar?blah=2>&blee=bix#1234')
    ('www.blah.com', '/foo%20/%20bar', {'blee': 'bix', 'blah': '2%3E'}, '1234')

    """
    # Splits and encodes the url, and breaks the query string into a dict
    proto, host, path, query, fragment = urlsplit(url)
    path = quote(path)
    query = quote(query, safe='&=')
    fragment = quote(fragment, safe='')
    query_elems = {}
    # Put the query elems in a dict
    for pair in query.split('&'):
        pair = pair.split('=')
        if pair:
            query_elems[pair[0]] = pair[-1]
    return host, path, query_elems, fragment

# We make this method cache its results because it will be called
# once for most url checks and also when generating the embed code
# no need to reparse the url n times
break_url = BufferCache(_break_url)

# YouTube!
@provider(IURLChecker)
def youtube_check(url):
    host, path, query, fragment = _break_url(url)
    if host.endswith('youtube.com') and query.has_key('v'):
        return True
    return False

youtube_check.index = 100

def youtube_generator(url, width):
    """ A quick check for the right url

    >>> print youtube_generator('http://www.youtube.com/watch?v=1111',
    ...                         width=400)
    <object width="400" height="330"><param name="movie" value="http://www.youtube.com/v/1111"></param><param name="wmode" value="transparent"></param><embed src="http://www.youtube.com/v/1111" type="application/x-shockwave-flash" wmode="transparent" width="400" height="330"></embed></object>

    """
    tag = []
    host, path, query, fragment = _break_url(url)
    height = int(round(0.824*width))
    tag.append('<object width="%s" height="%s">'%(width, height))
    video_id = query['v']
    embed_url = urlunsplit(('http', host, 'v/'+video_id, '', ''))
    tag.append('<param name="movie" value="%s"></param>'%embed_url)
    tag.append('<param name="wmode" value="transparent"></param>')
    tag.append('<embed src="%s" type="application/x-shockwave-flash" '
               'wmode="transparent" '
               'width="%s" height="%s"></embed>'%(embed_url,
                                                  width, height))
    tag.append('</object>')
    return u''.join(tag)

class youtube_mediaurl(object):
    """Returns the quicktime media url for a piece of youtube content:

           >>> url = youtube_mediaurl('http://www.youtube.com/watch?v=1111')
           >>> url.media_url
           'http://youtube.com/v/1111.swf'
           >>> url.mimetype
           'application/x-shockwave-flash'
    """
    implements(IMediaURL)
    adapts(str)
    def __init__(self, url):
        host, path, query, fragment = _break_url(url)
        video_id = query['v']
        self.mimetype = 'application/x-shockwave-flash'
        self.media_url = 'http://youtube.com/v/%s.swf'%video_id

# one.revver.com
@provider(IURLChecker)
def onerevver_check(url):
    host, path, query, fragment = _break_url(url)
    if host == 'one.revver.com':
        return True
    return False

onerevver_check.index = 200

FINALDIGITS = re.compile(r'.*?(\d+)$')
WATCHDIGITS = re.compile(r'.*?/(\d+)(?:/\D+?)?(?:/(\d+))?$')

def _onerevver_getids(url):
    host, path, query, fragment = _break_url(url)
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
        host, path, query, fragment = _break_url(url)
        video_id, affiliate_id = _onerevver_getids(url)
        self.mimetype = 'video/quicktime'
        self.media_url = 'http://media.revver.com/qt;sharer=%s/%s.mov'%(
                                                         affiliate_id, video_id)

# The original revver QT embed
@provider(IURLChecker)
def revver_check(url):
    host, path, query, fragment = _break_url(url)
    if host.endswith('revver.com'):
        return True
    return False

revver_check.index = 300

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
    host, path, query, fragment = _break_url(url)
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

# Google video
@provider(IURLChecker)
def google_check(url):
    host, path, query, fragment = _break_url(url)
    if host == 'video.google.com' and query.has_key('docid'):
        return True
    return False

google_check.index = 400

def google_generator(url, width):
    """ A quick check for the right url

    >>> print google_generator('http://video.google.com/videoplay?docid=-18281',
    ...                         width=400)
    <embed style="width:400px; height:326px;" id="VideoPlayback" type="application/x-shockwave-flash" src="http://video.google.com/googleplayer.swf?docId=-18281"></embed>

    """
    tag = []
    host, path, query, fragment = _break_url(url)
    height = int(round(0.815*width))
    video_id = query['docid']
    tag.append('<embed style="width:%spx; height:%spx;" '
               'id="VideoPlayback" type="application/x-shockwave-flash" '
               'src="http://video.google.com/googleplayer.swf?docId=%s">'%(
        width, height, video_id
        ))
    tag.append('</embed>')
    return u''.join(tag)

# Vimeo
@provider(IURLChecker)
def vimeo_check(url):
    host, path, query, fragment = _break_url(url)
    if host.endswith('vimeo.com'):
        return True
    return False

vimeo_check.index = 500

def vimeo_generator(url, width):
    """ A quick check for the right url

    >>> print vimeo_generator('http://www.vimeo.com/clip:18281', width=400)
    <embed src="http://www.vimeo.com/moogaloop.swf?clip_id=18281" quality="best" scale="exactfit" width="400" height="300" type="application/x-shockwave-flash"></embed>
    """
    tag = []
    host, path, query, fragment = _break_url(url)
    height = int(round(0.75*width))

    video_id = None
    try:
        video_id = int(path.split('%3A')[-1])
    except ValueError:
        pass
    if not video_id:
        return
    embed_url = urlunsplit(('http', host, 'moogaloop.swf',
                            'clip_id=%s'%video_id, ''))
    tag.append('<embed src="%s" quality="best" scale="exactfit" '
               'width="%s" height="%s" '
               'type="application/x-shockwave-flash">'%(embed_url,
                                                        width,
                                                        height))
    tag.append('</embed>')
    return u''.join(tag)

# Vmix
@provider(IURLChecker)
def vmix_check(url):
    host, path, query, fragment = _break_url(url)
    if host.endswith('.vmix.com') and query.has_key('id'):
        return True
    return False

vmix_check.index = 600

def vmix_generator(url, width):
    """ A quick check for the right url

    >>> print vmix_generator('http://www.vmix.com/view.php?id=1111&type=video',
    ...                      width=400)
    <embed src="http://www.vmix.com/flash/super_player.swf?id=1111&type=video&l=0&autoStart=0"width="400" height="333" wmode="transparent"pluginspage="http://www.macromedia.com/go/getflashplayer"></embed>

    """
    tag = []
    host, path, query, fragment = _break_url(url)
    height = int(round(0.833*width))
    video_id = query['id']
    p_type = query['type']
    tag.append('<embed '
'src="http://www.vmix.com/flash/super_player.swf?id=%s&type=%s&l=0&autoStart=0"'
'width="%s" height="%s" wmode="transparent"'
'pluginspage="http://www.macromedia.com/go/getflashplayer">'%(video_id,
                                                              p_type,
                                                              width,
                                                              height))
    tag.append('</embed>')
    return u''.join(tag)

# Yahoo! video
@provider(IURLChecker)
def yahoo_check(url):
    host, path, query, fragment = _break_url(url)
    if host == 'video.yahoo.com' and query.has_key('vid'):
        return True
    return False

yahoo_check.index = 700

def yahoo_generator(url, width):
    """ A quick check for the right url

    >>> print yahoo_generator(
    ... 'http://video.yahoo.com/video/play?vid=349edb18f0e2914a679d10f4754e689a.1106585&cache=1',
    ...                      width=400)
    <embed src="http://us.i1.yimg.com/cosmos.bcst.yahoo.com/player/media/swf/FLVVideoSolo.swf" flashvars="id=1106585&emailUrl=http%3A%2F%2Fvideo.yahoo.com%2Futil%2Fmail%3Fei%3DUTF-8%26vid%3D349edb18f0e2914a679d10f4754e689a.1106585%26cache%3D1&imUrl=http%253A%252F%252Fvideo.yahoo.com%252Fvideo%252Fplay%253Fvid%253D349edb18f0e2914a679d10f4754e689a.1106585%2526cache%253D1&imTitle=Unknown&searchUrl=http://video.yahoo.com/video/search?p=&profileUrl=http://video.yahoo.com/video/profile?yid=&creatorValue=&vid=349edb18f0e2914a679d10f4754e689a.1106585" type="application/x-shockwave-flash" width="400" height="330"></embed>

    """
    tag = []
    host, path, query, fragment = _break_url(url)
    height = int(round(0.824*width))
    video_id = query['vid']
    # The video id has two parts split by a . we need the latter one
    vid_end = video_id.split('.')[-1]
    title = 'Unknown'
    email_url = quote(
        'http://video.yahoo.com/util/mail?ei=UTF-8&vid=%s&cache=1' %
        video_id, '')
    # Double encode the IM url because that's what yahoo does
    im_url = quote(quote(url, ''), '')
    search_url = ('http://video.yahoo.com/video/search?p=&profileUrl='
                  'http://video.yahoo.com/video/profile?yid='
                  '&creatorValue=&vid=%s' %
                  video_id)

    tag.append('<embed '
               'src="http://us.i1.yimg.com/cosmos.bcst.yahoo.com/player'
               '/media/swf/FLVVideoSolo.swf" '
               'flashvars="id=%s'
               '&emailUrl=%s'
               '&imUrl=%s'
               '&imTitle=%s'
               '&searchUrl=%s" '
               'type="application/x-shockwave-flash" '
               'width="%s" height="%s">'%(vid_end, email_url,
                                          im_url, title,
                                          search_url, width,
                                          height))
    tag.append('</embed>')
    return u''.join(tag)

# Blip.tv (only accepts direct urls to flv videos!)
@provider(IURLChecker)
def blip_check(url):
    host, path, query, fragment = _break_url(url)
    if host.endswith('blip.tv') and path.endswith('.flv'):
        return True
    return False

blip_check.index = 800

def blip_generator(url, width):
    """ A quick check for the right url, this one requires a direct
    flv link:

    >>> print blip_generator('http://blip.tv/file/get/SomeVideo.flv', width=400)
    <embed wmode="transparent" src="http://blip.tv/scripts/flash/blipplayer.swf?autoStart=false&file=http://blip.tv/file/get/SomeVideo.flv&source=3" quality="high" width="400" height="320" name="movie" type="application/x-shockwave-flash" pluginspage="http://www.macromedia.com/go/getflashplayer"></embed>

    """
    tag = []
    host, path, query, fragment = _break_url(url)
    height = int(round(0.8*width))

    video_url = url
    path_elems = path.split('/')
    video_id = path_elems.pop(-1)
    tag.append('<embed wmode="transparent" '
        'src="http://blip.tv/scripts/flash/blipplayer.swf'
        '?autoStart=false&file=%s&source=3" '
        'quality="high" width="%s" height="%s" name="movie" '
        'type="application/x-shockwave-flash" '
        'pluginspage="http://www.macromedia.com/go/getflashplayer">'%(video_url,
                                                                      width,
                                                                      height))
    tag.append('</embed>')
    return u''.join(tag)

# ifilm
@provider(IURLChecker)
def ifilm_check(url):
    host, path, query, fragment = _break_url(url)
    if host.endswith('ifilm.com'):
        return True
    return False

ifilm_check.index = 900

def ifilm_generator(url, width):
    """ A quick check for the right url:

    >>> print ifilm_generator('http://www.ifilm.com/video/2690458', width=400)
    <embed width="400" height="326" src="http://www.ifilm.com/efp" quality="high" bgcolor="000000" name="efp" align="middle" type="application/x-shockwave-flash" pluginspage="http://www.macromedia.com/go/getflashplayer" flashvars="flvbaseclip=2690458&"></embed>
    """
    tag = []
    host, path, query, fragment = _break_url(url)
    height = int(round(0.815*width))

    path_elems = path.split('/')
    video_id = path_elems.pop(-1)
    tag.append('<embed width="%s" height="%s" src="http://www.ifilm.com/efp" '
               'quality="high" bgcolor="000000" name="efp" align="middle" '
               'type="application/x-shockwave-flash" '
               'pluginspage="http://www.macromedia.com/go/getflashplayer" '
               'flashvars="flvbaseclip=%s&">'%(width, height, video_id))
    tag.append('</embed>')
    return u''.join(tag)

# myspace
@provider(IURLChecker)
def myspace_check(url):
    host, path, query, fragment = _break_url(url)
    if host.endswith('vids.myspace.com') and query.has_key('videoid'):
        return True
    return False

myspace_check.index = 1000

def myspace_generator(url, width):
    """ A quick check for the right url:

    >>> print myspace_generator('http://vids.myspace.com/index.cfm?fuseaction=vids.individual&videoid=1577693374', width=400)
    <embed src="http://lads.myspace.com/videos/vplayer.swf" flashvars="m=1577693374&type=video" type="application/x-shockwave-flash" width="400" height="322"></embed>
    """
    tag = []
    host, path, query, fragment = _break_url(url)
    height = int(round(0.805*width))

    video_id = query['videoid']
    tag.append('<embed src="http://lads.myspace.com/videos/vplayer.swf" '
               'flashvars="m=%s&type=video" '
               'type="application/x-shockwave-flash" '
               'width="%s" height="%s">'%(video_id, width, height))
    tag.append('</embed>')
    return u''.join(tag)

# metacafe
@provider(IURLChecker)
def metacafe_check(url):
    host, path, query, fragment = _break_url(url)
    if host.endswith('metacafe.com'):
        return True
    return False

metacafe_check.index = 1100

def metacafe_generator(url, width):
    """ A quick check for the right url:

    >>> print metacafe_generator('http://www.metacafe.com/watch/344239/amazing_singing_parrot/', width=400)
    <embed src="http://www.metacafe.com/fplayer/344239/amazing_singing_parrot.swf" width="400" height="345" wmode="transparent" pluginspage="http://www.macromedia.com/go/getflashplayer" type="application/x-shockwave-flash"></embed>
    """
    tag = []
    host, path, query, fragment = _break_url(url)
    height = int(round(0.863*width))

    path_elems = path.split('/')
    last_elem = path_elems.pop(-1)
    if not last_elem:
        # in case the url ends with a '/'
        last_elem = path_elems.pop(-1)
    video_name = last_elem
    video_id = path_elems.pop(-1)
    try:
        # This should be an integer id if not fail
        int(video_id)
    except (ValueError, TypeError):
        return
    tag.append('<embed src="http://www.metacafe.com/fplayer/%s/%s.swf" '
               'width="%s" height="%s" wmode="transparent" '
               'pluginspage="http://www.macromedia.com/go/getflashplayer" '
               'type="application/x-shockwave-flash">'%(video_id, video_name, width, height))
    tag.append('</embed>')
    return u''.join(tag)

# College Humor (nearly identical to vimeo)
@provider(IURLChecker)
def collegehumor_check(url):
    host, path, query, fragment = _break_url(url)
    if host.endswith('collegehumor.com'):
        return True
    return False

collegehumor_check.index = 1200

def collegehumor_generator(url, width):
    """ A quick check for the right url

    >>> print collegehumor_generator('http://www.collegehumor.com/video:1752121', width=400)
    <embed src="http://www.collegehumor.com/moogaloop/moogaloop.swf?clip_id=1752121" quality="best" scale="exactfit" width="400" height="300" type="application/x-shockwave-flash"></embed>
    """
    tag = []
    host, path, query, fragment = _break_url(url)
    height = int(round(0.75*width))

    video_id = None
    try:
        video_id = int(path.split('%3A')[-1])
    except ValueError:
        pass
    if not video_id:
        return
    embed_url = urlunsplit(('http', host, 'moogaloop/moogaloop.swf',
                            'clip_id=%s'%video_id, ''))
    tag.append('<embed src="%s" quality="best" scale="exactfit" '
               'width="%s" height="%s" '
               'type="application/x-shockwave-flash">'%(embed_url,
                                                        width,
                                                        height))
    tag.append('</embed>')
    return u''.join(tag)
