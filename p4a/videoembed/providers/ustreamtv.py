from zope.interface import Interface, implements, implementer
from zope.component import adapts, adapter, queryUtility
from p4a.videoembed.interfaces import provider, IURLChecker, IEmbedCode
from p4a.videoembed.utils import break_url

# Ustream!
@provider(IURLChecker)
def ustreamtv_check(url):
    host, path, query, fragment = break_url(url)
    if host.endswith('ustream.tv'):
        return True
    return False

EMBED_HTML = '''
  <embed width="416" height="340" flashvars="autoplay=false"
         src="http://www.ustream.tv/%(video_id)s.usv"
         type="application/x-shockwave-flash" wmode="transparent" \>
'''

@adapter(str, int)
@implementer(IEmbedCode)
def ustreamtv_generator(url, width):
    """ A quick check for the right url

    >>> html = ustreamtv_generator('http://www.ustream.tv/MrTopf/videos/SZlo2.JzT4vroml1YqwHck0MZvteE4Pm', width=400)
    >>> 'http://www.ustream.tv/SZlo2.JzT4vroml1YqwHck0MZvteE4Pm.usv' in html
    True

    """

    host, path, query, fragment = break_url(url)
    height = int(round(0.815*width))

    video_id = path.split('/')[-1]

    kwargs = dict(width=width,
                  height=height,
                  video_id=video_id)

    return EMBED_HTML % kwargs
