from xml.dom import minidom
from p4a.videoembed.utils import (break_url, xpath_text,
                                  xpath_attr, remote_content)
from p4a.videoembed.interfaces import provider
from p4a.videoembed.interfaces import IEmbedCode
from p4a.videoembed.interfaces import IURLChecker
from p4a.videoembed.interfaces import IVideoMetadataLookup
from zope.interface import implementer
from zope.component import adapter

# Dailymotion
@provider(IURLChecker)
def dailymotion_check(url):
    """Check to see if the given url matches.

      >>> dailymotion_check('http://someplace.com')
      False
      >>> dailymotion_check('http://www.dailymotion.com/video/xc8vyu_helmut-fritz-ca-m-enerve_creation')
      True
      >>> dailymotion_check('http://www.dailymotion.com/video/xc8vyu')
      True
      >>> dailymotion_check('http://www.dailymotion.com/video/')
      False

    """
    host, path, query, fragment = break_url(url)
    if host.startswith('www.dailymotion.com') and path.startswith('/video/') \
    and len(path.split('/')[2]) > 0:
        return True
    return False

dailymotion_check.index = 1800

@adapter(str, int)
@implementer(IEmbedCode)
def dailymotion_generator(url, width):
    """ A quick check for the right url

    >>> print dailymotion_generator('http://www.dailymotion.com/video/xajm2v_julio-cesar-skill-vs-materazzi_sport',
    ...                         width=400)
    <embed type="application/x-shockwave-flash" src="http://www.dailymotion.com/swf/video/xajm2v" width="400" allowfullscreen="true" allowscriptaccess="always"></embed>

    """
    tag = []
    host, path, query, fragment = break_url(url)
    height = int(round(0.824*width))
    video_id_title = path.split('/')[2]
    video_id = video_id_title.split('_')[0]
    tag.append('<embed type="application/x-shockwave-flash" '
               'src="http://www.dailymotion.com/swf/video/%s" '
               'width="%s" allowfullscreen="true" allowscriptaccess="always">'
               ''%(video_id, width
        ))
    tag.append('</embed>')
    return u''.join(tag)
