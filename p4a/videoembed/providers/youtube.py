import urllib2
from xml.dom import minidom
from xml.parsers import expat
from urlparse import urlunsplit
from p4a.videoembed.utils import break_url, xpath_text
from p4a.videoembed.interfaces import provider
from p4a.videoembed.interfaces import IEmbedCode
from p4a.videoembed.interfaces import IMediaURL
from p4a.videoembed.interfaces import IURLChecker
from p4a.videoembed.interfaces import IVideoMetadataLookup
from p4a.videoembed.interfaces import VideoMetadata
from zope.component import adapts, adapter, queryUtility
from zope.interface import implements, implementer, Interface
from zope.schema import TextLine

import logging
logger = logging.getLogger('p4a.videoembed.providers.youtube')

class IYoutubeConfig(Interface):
    """Configuration for accessing the RESTful api for youtube."""

    dev_id = TextLine(title=u'Developer Id',
                      required=True)

# YouTube!
@provider(IURLChecker)
def youtube_check(url):
    host, path, query, fragment = break_url(url)
    if host.endswith('youtube.com') and query.has_key('v'):
        return True
    return False

youtube_check.index = 100

# This is the appropriate way of getting the thumbnail image.  Due to not
# wanting to add the dev_id requirement, this code will not be used yet
def _youtube_metadata_lookup(xml):
    """Parse the given xml and get appropriate metadata.

      >>> xml = '''<?xml version="1.0" ?>
      ... <ut_response status="ok">
      ...   <video_details>
      ...     <author>youtubeuser</author>
      ...     <title>Random Title</title>
      ...     <rating_avg>3.25</rating_avg>
      ...     <rating_count>10</rating_count>
      ...     <tags>california trip redwoods</tags>
      ...     <description>Random description.</description>
      ...     <update_time>1129803584</update_time>
      ...     <view_count>7</view_count>
      ...     <upload_time>1127760809</upload_time>
      ...     <length_seconds>8</length_seconds>
      ...     <recording_date>None</recording_date>
      ...     <recording_location/>
      ...     <recording_country/>
      ...     <thumbnail_url>http://blah.com/default.jpg</thumbnail_url>
      ...   </video_details>
      ... </ut_response>'''

      >>> data = _youtube_metadata_lookup(xml)
      >>> data.author
      u'youtubeuser'
      >>> data.title
      u'Random Title'
      >>> data.description
      u'Random description.'
      >>> data.tags
      [u'california', u'trip', u'redwoods']
      >>> data.thumbnail_url
      u'http://blah.com/default.jpg'
      >>> data.duration
      8.0

    """

    try:
        doc = minidom.parseString(xml)
    except expat.ExpatError:
        logger.exception('Error while trying to parse RSS XML - "%s"' % xml)
        return None

    metadata = VideoMetadata()
    metadata.title = xpath_text(doc, u'ut_response/video_details/title')
    metadata.author = xpath_text(doc, u'ut_response/video_details/author')
    metadata.description = xpath_text(\
        doc, u'ut_response/video_details/description')
    metadata.thumbnail_url = xpath_text(\
        doc, u'ut_response/video_details/thumbnail_url')
    metadata.tags = xpath_text(\
        doc, u'ut_response/video_details/tags').split(' ')

    duration = xpath_text( \
        doc, u'ut_response/video_details/length_seconds')
    if duration is not None and duration.strip() != '':
        try:
            metadata.duration = float(duration)
        except:
            # probably wasn't an int, ignoring
            pass

    return metadata

def _get_metadata_xml(url, dev_id):
    """Retrieve the remote XML for the given video url."""

    base_url = 'http://www.youtube.com/api2_rest' \
               '?method=youtube.videos.get_details' \
               '&dev_id=%(dev_id)s&video_id=%(video_id)s'

    host, path, query, fragment = break_url(url)
    video_id = query['v']
    fin = urllib2.urlopen(base_url % dict(dev_id=dev_id, video_id=video_id))
    xml = fin.read()
    fin.close()
    return xml

@adapter(str)
@implementer(IVideoMetadataLookup)
def youtube_metadata_lookup(url):
    """Retrieve metadata information regarding a youtube video url.

      >>> youtube_metadata_lookup('http://www.youtube.com/watch?v=foo') is None
      True

    """

    config = queryUtility(IYoutubeConfig)
    if config is None:
        logger.warn("No IYoutubeConfig utility found, remote metadata "
                    "retrieval disabled")
        return None

    xml = _get_metadata_xml(url, config.dev_id)
    return _youtube_metadata_lookup(xml)

@adapter(str, int)
@implementer(IEmbedCode)
def youtube_generator(url, width):
    """ A quick check for the right url

    >>> print youtube_generator('http://www.youtube.com/watch?v=1111',
    ...                         width=400)
    <object width="400" height="330"><param name="movie" value="http://www.youtube.com/v/1111"></param><param name="wmode" value="transparent"></param><embed src="http://www.youtube.com/v/1111" type="application/x-shockwave-flash" wmode="transparent" width="400" height="330"></embed></object>

    """
    tag = []
    host, path, query, fragment = break_url(url)
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
        host, path, query, fragment = break_url(url)
        video_id = query['v']
        self.mimetype = 'application/x-shockwave-flash'
        self.media_url = 'http://youtube.com/v/%s.swf'%video_id
