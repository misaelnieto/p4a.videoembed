from zope.interface import Interface, Attribute
from zope.interface import directlyProvides
from zope.schema.interfaces import IText

class IEmbedCode(IText):
    """An html video embed code"""


class IEmbedCodeConverterRegistry(Interface):
    """A registry of embed code adapters which can convert a url from
    a video sharing site to an embed code"""

    def get_code(url, width):
        """Converts the given url into an embed code of the desired width"""


class IURLChecker(Interface):
    """Determines whether a given url corresponds to a particular format"""

    def __call__(url):
        """Returns a boolean indicating whether the given url matches the
        desired format"""

    index = Attribute("An index indicating the order in which the check should "
                       "be run")


class IURLType(Interface):
    """A utility which can indicate the converter to which a given url
    corresponds"""

    def __call__(url):
        """Returns the name of the adapter to be used to convert the passed in
        url"""


class ILinkProvider(Interface):
    """A silly adapter declaring that an object provides a getLink method"""

    def getLink():
        """Returns a url which may correspond to a video embed code"""


# A simple decorator to indicate that a function provides a particular interface
# useful for marking utility functions
class provider(object):
    def __init__(self, *interfaces):
        self.interfaces = interfaces

    def __call__(self, ob):
        directlyProvides(ob, *self.interfaces)
        return ob
