from urlparse import urlunsplit
from p4a.videoembed.utils import break_url
from p4a.videoembed.interfaces import provider
from p4a.videoembed.interfaces import IEmbedCode
from p4a.videoembed.interfaces import IMediaURL
from p4a.videoembed.interfaces import IURLChecker
from p4a.videoembed.interfaces import IVideoMetadataLookup
from p4a.videoembed.interfaces import VideoMetadata
from zope.interface import implements, implementer
from zope.component import adapts, adapter

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

      >>> xml = '''
      ... <video_details>
      ...     <author>youtubeuser</author>
      ...     <title>My Trip to California</title>
      ...     <tags>california trip redwoods</tags>
      ...     <description>This video shows some highlights of my trip to California last year.</description>
      ...     <length_seconds>8</length_seconds>
      ...     <thumbnail_url>http://img.youtube.com/vi/bkZHmZmZUJk/default.jpg</thumbnail_url>
      ... </video_details>'''

      >>> _youtube_metadata_lookup(xml)
      <VideoMetadata ... thumbnail_url=http://img.youtube.com/vi/bkZHmZmZUJk/default.jpg>

    """

    thumbstart = xml.find('<thumbnail_url>')
    thumbend = xml.find('</thumbnail_url>')

    thumbnail_url = xml[thumbstart+15:thumbend].strip()

    return VideoMetadata(thumbnail_url=thumbnail_url)

@adapter(str)
@implementer(IVideoMetadataLookup)
def youtube_metadata_lookup(url):
    """Retrieve metadata information regarding a youtube video url.

      >>> youtube_metadata_lookup('http://www.youtube.com/watch?v=foo')
      <VideoMetadata ... thumbnail_url=http://img.youtube.com/vi/foo/default.jpg>
    """

    host, path, query, fragment = break_url(url)
    video_id = query['v']
    thumbnail_url = 'http://img.youtube.com/vi/%s/default.jpg' % video_id
    return VideoMetadata(thumbnail_url=thumbnail_url)

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

