import urllib2
from xml.dom import minidom
from xml.sax import saxutils
from urlparse import urlsplit
from urllib import quote
from p4a.videoembed._cache import BufferCache

def _break_url(url):
    """A helper method for extracting url parts and parsing the query string

      >>> _break_url('http://www.blah.com/foo/bar?blah=2&blee=bix#1234')
      ('www.blah.com', '/foo/bar', {'blee': 'bix', 'blah': '2'}, '1234')

    Needs to do url quoting:

      >>> _break_url('http://www.blah.com/foo / bar?bla=2>&blee=bix#1234')
      ('www.blah.com', '/foo%20/%20bar', {'blee': 'bix', 'bla': '2%3E'}, '1234')

    Make sure {'': ''} doesn't get returned for the query when there are no
    query args (this used to be the case).
      >>> _break_url('http://www.blah.com/foo')
      ('www.blah.com', '/foo', {}, '')

    """
    # Splits and encodes the url, and breaks the query string into a dict
    proto, host, path, query, fragment = urlsplit(url)
    path = quote(path)
    query = quote(query, safe='&=')
    fragment = quote(fragment, safe='')
    query_elems = {}
    # Put the query elems in a dict
    for pair in query.split('&'):
        pos = pair.find('=')
        if pos > -1:
            key = pair[:pos]
            value = pair[pos+1:]
        else:
            key = pair
            value = ''
        if key:
            query_elems[key] = value
    return host, path, query_elems, fragment

# We make this method cache its results because it will be called
# once for most url checks and also when generating the embed code
# no need to reparse the url n times
break_url = BufferCache(_break_url)

def xpath_node(node, path, prefix=''):
    """Find nodes with a basic xpath path given the node tree.

      >>> from xml.dom import minidom
      >>> doc = minidom.parseString('<foo><bar></bar></foo>')

      >>> xpath_node(doc, 'abcdef/bar') is None
      True
      >>> xpath_node(doc, 'foo/bar').tagName
      u'bar'

    """

    full = getattr(node, 'tagName', '')
    if prefix:
        full = prefix + '/' + full

    if full == path:
        return node

    for child in node.childNodes:
        if isinstance(child, minidom.Element):
            n = xpath_node(child, path, full)
            if n is not None:
                return n

DEFAULT_ENTITIES = {
    '&quot;': '"'
    }

def node_value(node, entities=DEFAULT_ENTITIES):
    """Return the flattened body value of the given node.  If the given
    node has elements as children, they will be converted to textual XML.

      >>> from xml.dom.minidom import parseString

      >>> node = parseString('<foo> abc --</foo>').childNodes[0]
      >>> node.tagName
      u'foo'
      >>> node_value(node)
      u'abc --'

      >>> node = parseString('<foo> abc<bar>def</bar></foo>').childNodes[0]
      >>> node.tagName
      u'foo'
      >>> node_value(node)
      u'abc<bar>def</bar>'

    Make sure entities are getting processed properly.

      >>> node = parseString('<foo>&gt;&quot;abc&quot;&lt;</foo>').childNodes[0]
      >>> node_value(node)
      u'>"abc"<'

    """

    v = ''
    for x in node.childNodes:
        v += x.toxml().strip()
    return saxutils.unescape(''.join(v.split('\n')), entities)

def xpath_text(node, path):
    node = xpath_node(node, path)
    if node is not None:
        return node_value(node)
    return u''

def xpath_attr(node, path, attr):
    node = xpath_node(node, path)
    if node is not None and isinstance(node, minidom.Element) \
           and node.hasAttribute(attr):
        return node.getAttribute(attr)
    return u''

def squeeze_xml(xml):
    new_xml = u''
    for piece in xml.split():
        new_xml += ' ' + piece
    return new_xml.strip()

def remote_content(url):
    """Retrieve the remote HTTP content for the given video url."""
    host, path, query, fragment = break_url(url)
    fin = urllib2.urlopen(url)
    content = fin.read()
    fin.close()
    return content
