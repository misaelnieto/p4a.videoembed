from zope.interface import implementer, Interface
from zope.schema import TextLine
from zope.component import adapter, queryUtility
from p4a.videoembed.utils import break_url, squeeze_xml
from p4a.videoembed.interfaces import provider
from p4a.videoembed.interfaces import IEmbedCode
from p4a.videoembed.interfaces import IURLChecker

# Any flv (only accepts direct urls to flv videos!) uses blip's player
@provider(IURLChecker)
def flv_check(url):
    """Check to see if the given url matches.

      >>> flv_check('http://someplace.com')
      False
      >>> flv_check('http://someplace.com/file.flv')
      True

    """

    host, path, query, fragment = break_url(url)
    if path.endswith('.flv'):
        return True
    return False

flv_check.index = 10100

class IFlvPlayerConfig(Interface):
    """Configuration for accessing the RESTful api for youtube."""

    player_url = TextLine(title=u'URL to Player',
                          description=u'FLV player url (requires the flv '
                                      u'player from '
                                      u'http://www.jeroenwijering.com/)',
                          required=True)

FLV_PLAYER_URL = "http://location/path/to/flvplayer.swf"

@adapter(str, int)
@implementer(IEmbedCode)
def flv_generator(url, width):
    ''' A quick check for the right url, this one requires a direct
    flv link:

      >>> print flv_generator('http://blip.tv/file/get/SomeVideo.flv', width=400)
      <embed src="http://location/path/to/flvplayer.swf" width="400" height="320" bgcolor="#FFFFFF" type="application/x-shockwave-flash" pluginspage="http://www.macromedia.com/go/getflashplayer" flashvars="file=http://blip.tv/file/get/SomeVideo.flv&autostart=true"></embed>

    To get a proper url for the actual flash player we register a new
    IFlvPlayerConfig utility.

      >>> from zope.component import provideUtility
      >>> class FlvPlayerConfig(object):
      ...     implements(IFlvPlayerConfig)
      ...     player_url = "http://somehost.com/someplayer.swf"
      >>> provideUtility(FlvPlayerConfig())

      >>> print flv_generator('http://blip.tv/file/get/SomeVideo.flv', width=400)
      <embed src="http://somehost.com/someplayer.swf" width="400" height="320" bgcolor="#FFFFFF" type="application/x-shockwave-flash" pluginspage="http://www.macromedia.com/go/getflashplayer" flashvars="file=http://blip.tv/file/get/SomeVideo.flv&autostart=true"></embed>

    '''

    tag = []
    height = int(round(0.8*width))

    player_url = FLV_PLAYER_URL
    config = queryUtility(IFlvPlayerConfig)
    if config is not None:
        player_url = config.player_url or player_url

    video_url = url
    tag.append('<embed src="%s" width="%s" height="%s" bgcolor="#FFFFFF" '
        'type="application/x-shockwave-flash" '
        'pluginspage="http://www.macromedia.com/go/getflashplayer" '
        'flashvars="file=%s&autostart=true">'%(player_url, width, height,
                                               video_url))
    tag.append('</embed>')
    return u''.join(tag)

# Any swf
@provider(IURLChecker)
def swf_check(url):
    """Check to see if the given url matches.

      >>> swf_check('http://someplace.com')
      False
      >>> swf_check('http://someplace.com/file.swf')
      True

    """

    host, path, query, fragment = break_url(url)
    if path.endswith('.swf'):
        return True
    return False

swf_check.index = 10100

@adapter(str, int)
@implementer(IEmbedCode)
def swf_generator(url, width):
    ''' A quick check for the right url, this one requires a direct
    swf link:

      >>> print swf_generator('http://somehost.com/file/get/SomeVideo.swf', width=400)
      <object classid="clsid:d27cdb6e-ae6d-11cf-96b8-444553540000" codebase="http://fpdownload.macromedia.com/pub/shockwave/cabs/flash/swflash.cab#version=7,0,0,0" width="400" height="320" id="Untitled-1" align="middle"> <param name="allowScriptAccess" value="sameDomain" /> <param name="movie" value="http://somehost.com/file/get/SomeVideo.swf" /> <param name="quality" value="high" /> <param name="bgcolor" value="#ffffff" /> <embed src="http://somehost.com/file/get/SomeVideo.swf" quality="high" bgcolor="#ffffff" width="400" height="320" name="video" align="middle" allowScriptAccess="sameDomain" allowNetworking="all" type="application/x-shockwave-flash" pluginspage="http://www.adobe.com/go/getflashplayer" /> </object>

    '''

    height = int(round(0.8*width))

    return squeeze_xml(u'''
  <object classid="clsid:d27cdb6e-ae6d-11cf-96b8-444553540000"
          codebase="http://fpdownload.macromedia.com/pub/shockwave/cabs/flash/swflash.cab#version=7,0,0,0" 
          width="%(width)s" height="%(height)s" id="Untitled-1" align="middle">
    <param name="allowScriptAccess" value="sameDomain" />
    <param name="movie" value="%(file_url)s" />
    <param name="quality" value="high" />
    <param name="bgcolor" value="#ffffff" />
    <embed src="%(file_url)s" quality="high" bgcolor="#ffffff"
           width="%(width)s" height="%(height)s" name="video"
           align="middle" allowScriptAccess="sameDomain"
           allowNetworking="all"
           type="application/x-shockwave-flash"
           pluginspage="http://www.adobe.com/go/getflashplayer" />
  </object>
''' % {'file_url': url,
       'width': unicode(width),
       'height': unicode(height)})

