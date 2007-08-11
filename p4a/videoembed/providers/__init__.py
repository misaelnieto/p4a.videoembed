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

from p4a.videoembed.utils import break_url

# Vimeo
@provider(IURLChecker)
def vimeo_check(url):
    host, path, query, fragment = break_url(url)
    if host.endswith('vimeo.com'):
        return True
    return False

vimeo_check.index = 500

@adapter(str, int)
@implementer(IEmbedCode)
def vimeo_generator(url, width):
    """ A quick check for the right url

    >>> print vimeo_generator('http://www.vimeo.com/clip:18281', width=400)
    <embed src="http://www.vimeo.com/moogaloop.swf?clip_id=18281" quality="best" scale="exactfit" width="400" height="300" type="application/x-shockwave-flash"></embed>
    """
    tag = []
    host, path, query, fragment = break_url(url)
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
    host, path, query, fragment = break_url(url)
    if host.endswith('.vmix.com') and query.has_key('id'):
        return True
    return False

vmix_check.index = 600

@adapter(str, int)
@implementer(IEmbedCode)
def vmix_generator(url, width):
    """ A quick check for the right url

    >>> print vmix_generator('http://www.vmix.com/view.php?id=1111&type=video',
    ...                      width=400)
    <embed src="http://www.vmix.com/flash/super_player.swf?id=1111&type=video&l=0&autoStart=0"width="400" height="333" wmode="transparent"pluginspage="http://www.macromedia.com/go/getflashplayer"></embed>

    """
    tag = []
    host, path, query, fragment = break_url(url)
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
    host, path, query, fragment = break_url(url)
    if host == 'video.yahoo.com' and query.has_key('vid'):
        return True
    return False

yahoo_check.index = 700

@adapter(str, int)
@implementer(IEmbedCode)
def yahoo_generator(url, width):
    """ A quick check for the right url

    >>> print yahoo_generator(
    ... 'http://video.yahoo.com/video/play?vid=349edb18f0e2914a679d10f4754e689a.1106585&cache=1',
    ...                      width=400)
    <embed src="http://us.i1.yimg.com/cosmos.bcst.yahoo.com/player/media/swf/FLVVideoSolo.swf" flashvars="id=1106585&emailUrl=http%3A%2F%2Fvideo.yahoo.com%2Futil%2Fmail%3Fei%3DUTF-8%26vid%3D349edb18f0e2914a679d10f4754e689a.1106585%26cache%3D1&imUrl=http%253A%252F%252Fvideo.yahoo.com%252Fvideo%252Fplay%253Fvid%253D349edb18f0e2914a679d10f4754e689a.1106585%2526cache%253D1&imTitle=Unknown&searchUrl=http://video.yahoo.com/video/search?p=&profileUrl=http://video.yahoo.com/video/profile?yid=&creatorValue=&vid=349edb18f0e2914a679d10f4754e689a.1106585" type="application/x-shockwave-flash" width="400" height="330"></embed>

    """
    tag = []
    host, path, query, fragment = break_url(url)
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

# ifilm
@provider(IURLChecker)
def ifilm_check(url):
    host, path, query, fragment = break_url(url)
    if host.endswith('ifilm.com'):
        return True
    return False

ifilm_check.index = 900

@adapter(str, int)
@implementer(IEmbedCode)
def ifilm_generator(url, width):
    """ A quick check for the right url:

    >>> print ifilm_generator('http://www.ifilm.com/video/2690458', width=400)
    <embed width="400" height="326" src="http://www.ifilm.com/efp" quality="high" bgcolor="000000" name="efp" align="middle" type="application/x-shockwave-flash" pluginspage="http://www.macromedia.com/go/getflashplayer" flashvars="flvbaseclip=2690458&"></embed>
    """
    tag = []
    host, path, query, fragment = break_url(url)
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
    host, path, query, fragment = break_url(url)
    if host.endswith('vids.myspace.com') and query.has_key('videoid'):
        return True
    return False

myspace_check.index = 1000

@adapter(str, int)
@implementer(IEmbedCode)
def myspace_generator(url, width):
    """ A quick check for the right url:

    >>> print myspace_generator('http://vids.myspace.com/index.cfm?fuseaction=vids.individual&videoid=1577693374', width=400)
    <embed src="http://lads.myspace.com/videos/vplayer.swf" flashvars="m=1577693374&type=video" type="application/x-shockwave-flash" width="400" height="322"></embed>
    >>> print myspace_generator('http://vids.myspace.com/index.cfm?fuseaction=vids.individual&VideoID=1577693374', width=400)
    <embed src="http://lads.myspace.com/videos/vplayer.swf" flashvars="m=1577693374&type=video" type="application/x-shockwave-flash" width="400" height="322"></embed>
    """
    tag = []
    host, path, query, fragment = break_url(url)
    height = int(round(0.805*width))

    video_id = query.get('videoid', None)
    if video_id is None:
        video_id = query.get('VideoID', None)
    if video_id is None:
        return None
    tag.append('<embed src="http://lads.myspace.com/videos/vplayer.swf" '
               'flashvars="m=%s&type=video" '
               'type="application/x-shockwave-flash" '
               'width="%s" height="%s">'%(video_id, width, height))
    tag.append('</embed>')
    return u''.join(tag)

# metacafe
@provider(IURLChecker)
def metacafe_check(url):
    host, path, query, fragment = break_url(url)
    if host.endswith('metacafe.com'):
        return True
    return False

metacafe_check.index = 1100

@adapter(str, int)
@implementer(IEmbedCode)
def metacafe_generator(url, width):
    """ A quick check for the right url:

    >>> print metacafe_generator('http://www.metacafe.com/watch/344239/amazing_singing_parrot/', width=400)
    <embed src="http://www.metacafe.com/fplayer/344239/amazing_singing_parrot.swf" width="400" height="345" wmode="transparent" pluginspage="http://www.macromedia.com/go/getflashplayer" type="application/x-shockwave-flash"></embed>
    """
    tag = []
    host, path, query, fragment = break_url(url)
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
    host, path, query, fragment = break_url(url)
    if host.endswith('collegehumor.com'):
        return True
    return False

collegehumor_check.index = 1200

@adapter(str, int)
@implementer(IEmbedCode)
def collegehumor_generator(url, width):
    """ A quick check for the right url

    >>> print collegehumor_generator('http://www.collegehumor.com/video:1752121', width=400)
    <embed src="http://www.collegehumor.com/moogaloop/moogaloop.swf?clip_id=1752121" quality="best" scale="exactfit" width="400" height="300" type="application/x-shockwave-flash"></embed>
    """
    tag = []
    host, path, query, fragment = break_url(url)
    height = int(round(0.75*width))

    video_id = None
    try:
        video_id = int(path.split('%3A')[-1])
    except ValueError:
        return
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

# Veoh
@provider(IURLChecker)
def veoh_check(url):
    host, path, query, fragment = break_url(url)
    if host.endswith('veoh.com'):
        return True
    return False

veoh_check.index = 1300



@adapter(str, int)
@implementer(IEmbedCode)
def veoh_generator(url, width):
    """ A quick check for the right url

    >>> print veoh_generator('http://www.veoh.com/videos/v360719D94bNyJd', width=400)
    <embed src="http://www.veoh.com/videodetails.swf?permalinkId=v360719D94bNyJd&id=anonymous&player=videodetailsembedded&videoAutoPlay=0" width="400" height="324" bgcolor="#000000" type="application/x-shockwave-flash" pluginspage="http://www.macromedia.com/go/getflashplayer"></embed>

    """
    tag = []
    host, path, query, fragment = break_url(url)
    height = int(round(0.81*width))
    path_list = path.split('/')

    video_id = None
    try:
        # Use the path element imediately after '/videos/'
        video_id = path_list[path_list.index('videos')+1]
    except (ValueError, IndexError):
        return
    embed_url = urlunsplit(('http', host, 'videodetails.swf',
                            'permalinkId=%s&id=anonymous&'
                            'player=videodetailsembedded'
                            '&videoAutoPlay=0'%video_id, ''))
    tag.append('<embed src="%s" width="%s" height="%s" bgcolor="#000000" '
               'type="application/x-shockwave-flash" '
               'pluginspage="http://www.macromedia.com/go/getflashplayer">'%
                        (embed_url,
                         width,
                         height))
    tag.append('</embed>')
    return u''.join(tag)


# The original revver QT embed
@provider(IURLChecker)
def quicktime_check(url):
    host, path, query, fragment = break_url(url)
    if path.endswith('.mov') or path.endswith('.qt') or path.endswith('.m4v'):
        return True
    return False

#this goes last
quicktime_check.index = 100000

@adapter(str, int)
@implementer(IEmbedCode)
def quicktime_generator(url, width):
    """ A quick check for the right url

    >>> print quicktime_generator('http://mysite.com/url/to/qt.mov',
    ...                         width=400)
    <object codebase="http://www.apple.com/qtactivex/qtplugin.cab" width="400" classid="clsid:02BF25D5-8C17-4B23-BC80-D3488ABDDC6B" height="340"><param name="src" value="http://mysite.com/url/to/qt.mov" /><param name="controller" value="True" /><param name="cache" value="False" /><param name="autoplay" value="False" /><param name="kioskmode" value="False" /><param name="scale" value="tofit" /><embed src="http://mysite.com/url/to/qt.mov" pluginspage="http://www.apple.com/quicktime/download/" scale="tofit" kioskmode="False" qtsrc="http://mysite.com/url/to/qt.mov" cache="False" width="400" height="340" controller="True" type="video/quicktime" autoplay="False"></embed></object>

    >>> print quicktime_generator('http://mysite.com/url/to/movie.qt',
    ...                         width=400)
    <object codebase="http://www.apple.com/qtactivex/qtplugin.cab" width="400" classid="clsid:02BF25D5-8C17-4B23-BC80-D3488ABDDC6B" height="340"><param name="src" value="http://mysite.com/url/to/movie.qt" /><param name="controller" value="True" /><param name="cache" value="False" /><param name="autoplay" value="False" /><param name="kioskmode" value="False" /><param name="scale" value="tofit" /><embed src="http://mysite.com/url/to/movie.qt" pluginspage="http://www.apple.com/quicktime/download/" scale="tofit" kioskmode="False" qtsrc="http://mysite.com/url/to/movie.qt" cache="False" width="400" height="340" controller="True" type="video/quicktime" autoplay="False"></embed></object>

    """
    tag = []
    height = int(round(0.85*width))
    tag.append('<object '
          'codebase="http://www.apple.com/qtactivex/qtplugin.cab" width="%s" '
          'classid="clsid:02BF25D5-8C17-4B23-BC80-D3488ABDDC6B" height="%s">'%(
                      width, height))
    tag.append('<param name="src" value="%s" />'%url)
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
               'autoplay="False"></embed>'%(url, url, width, height))
    tag.append('</object>')
    return u''.join(tag)

# VH1 VSpot
@provider(IURLChecker)
def vspot_check(url):
    host, path, query, fragment = break_url(url)
    if host.endswith('vh1.com') and 'vspot' in path and query.has_key('id') \
           and query.has_key('vid'):
        return True
    return False

vspot_check.index = 1400



@adapter(str, int)
@implementer(IEmbedCode)
def vspot_generator(url, width):
    """ A quick check for the right url

    >>> print vspot_generator('http://www.vh1.com/vspot/?id=1557493&vid=147375', width=400)
    <object classid="clsid:D27CDB6E-AE6D-11cf-96B8-444553540000" width="400" height="392"><param name="movie" value="http://synd.vh1.com/player.jhtml"/><param name="FlashVars" value="id=1557493&vid=147375"/><param name="wmode" value="transparent"/><param name="scale" value="default"/><embed src="http://synd.vh1.com/player.jhtml" FlashVars="id=1557493&vid=147375" type="application/x-shockwave-flash" width="400" height="392" wmode="transparent" scale="default"></embed></object>

    """
    tag = []
    host, path, query, fragment = break_url(url)
    height = int(round(0.98*width))

    video_id = query['vid']
    other_id = query['id']
    tag.append('<object classid="clsid:D27CDB6E-AE6D-11cf-96B8-444553540000" '
               'width="%s" height="%s">'%(width, height))
    tag.append('<param name="movie" value="http://synd.vh1.com/player.jhtml"/>')
    tag.append('<param name="FlashVars" value="id=%s&vid=%s"/>'%(other_id,
                                                                  video_id))
    tag.append('<param name="wmode" value="transparent"/>')
    tag.append('<param name="scale" value="default"/>')
    tag.append('<embed src="http://synd.vh1.com/player.jhtml" FlashVars="'
               'id=%s&vid=%s" type="application/x-shockwave-flash" width="%s" '
               'height="%s" wmode="transparent" scale="default">'%(other_id, video_id, width,
                                                   height))
    tag.append('</embed>')
    tag.append('</object>')
    return u''.join(tag)



# LiveLeak.com
@provider(IURLChecker)
def liveleak_check(url):
    host, path, query, fragment = break_url(url)
    if host.endswith('liveleak.com') and query.has_key('i'):
        return True
    return False

liveleak_check.index = 1500



@adapter(str, int)
@implementer(IEmbedCode)
def liveleak_generator(url, width):
    """ A quick check for the right url

    >>> print liveleak_generator('http://www.liveleak.com/view?i=311_1179355691', width=400)
    <object type="application/x-shockwave-flash" width="400" height="328" wmode="transparent" data="http://www.liveleak.com/player.swf?autostart=false&token=311_1179355691"><param name="movie" value="http://www.liveleak.com/player.swf?autostart=false&token=311_1179355691" /><param name="wmode" value="transparent" /><param name="quality" value="high" /></object>

    """
    tag = []
    host, path, query, fragment = break_url(url)
    height = int(round(0.82*width))

    video_id = query['i']
    tag.append('<object type="application/x-shockwave-flash" '
               'width="%s" height="%s" wmode="transparent" '
               'data="http://www.liveleak.com/player.swf?autostart=false&token=%s">'
                  %(width, height, video_id))
    tag.append('<param name="movie" '
               'value="http://www.liveleak.com/player.swf?autostart=false&token=%s" />'
                  %video_id)
    tag.append('<param name="wmode" value="transparent" />')
    tag.append('<param name="quality" value="high" />')
    tag.append('</object>')
    return u''.join(tag)


# SuperDeluxe.com
@provider(IURLChecker)
def superdeluxe_check(url):
    host, path, query, fragment = break_url(url)
    if host.endswith('superdeluxe.com') and query.has_key('id'):
        return True
    return False

superdeluxe_check.index = 1500

@adapter(str, int)
@implementer(IEmbedCode)
def superdeluxe_generator(url, width):
    """ A quick check for the right url

    >>> print superdeluxe_generator('http://www.superdeluxe.com/sd/contentDetail.do?id=D81F2344BF5AC7BB20E4789DE29A20C721C3765DC38D406E', width=400)
    <object width="400" height="350"><param name="allowFullScreen" value="true" /><param name="movie" value="http://www.superdeluxe.com/static/swf/share_vidplayer.swf" /><param name="FlashVars" value="id=D81F2344BF5AC7BB20E4789DE29A20C721C3765DC38D406E" /><embed src="http://www.superdeluxe.com/static/swf/share_vidplayer.swf" FlashVars="id=D81F2344BF5AC7BB20E4789DE29A20C721C3765DC38D406E" type="application/x-shockwave-flash" width="400" height="350" allowFullScreen="true" ></embed></object>

    """
    tag = []
    host, path, query, fragment = break_url(url)
    height = int(round(0.875*width))

    video_id = query['id']
    tag.append('<object width="%s" height="%s">'%(width, height))
    tag.append('<param name="allowFullScreen" value="true" />')
    tag.append('<param name="movie" '
               'value="http://www.superdeluxe.com/static/swf/share_vidplayer.swf" />')
    tag.append('<param name="FlashVars" value="id=%s" />'%(video_id))
    tag.append('<embed src="http://www.superdeluxe.com/static/swf/share_vidplayer.swf" '
               'FlashVars="id=%s" type="application/x-shockwave-flash" '
               'width="%s" height="%s" allowFullScreen="true" >'%(video_id,
                                                                  width,
                                                                  height))
    tag.append('</embed>')
    tag.append('</object>')
    return u''.join(tag)
