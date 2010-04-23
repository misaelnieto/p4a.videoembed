"""Test library
"""
import doctest
import unittest
from zope.component import testing

def test_suite():
    from zope.testing.doctestunit import DocTestSuite
    return unittest.TestSuite((
            DocTestSuite('p4a.videoembed.registry',
                         setUp=testing.setUp,
                         tearDown=testing.tearDown,
                         optionflags=doctest.ELLIPSIS),
            DocTestSuite('p4a.videoembed.converters',
                         optionflags=doctest.ELLIPSIS),
            DocTestSuite('p4a.videoembed.utils',
                         optionflags=doctest.ELLIPSIS),

            DocTestSuite('p4a.videoembed.providers',
                         optionflags=doctest.ELLIPSIS),
            DocTestSuite('p4a.videoembed.providers.bliptv',
                         optionflags=doctest.ELLIPSIS),
            DocTestSuite('p4a.videoembed.providers.ustreamtv',
                         optionflags=doctest.ELLIPSIS),
            DocTestSuite('p4a.videoembed.providers.flash',
                         optionflags=doctest.ELLIPSIS,
                         setUp=testing.setUp,
                         tearDown=testing.tearDown),
            DocTestSuite('p4a.videoembed.providers.googlevideo',
                         optionflags=doctest.ELLIPSIS),
            DocTestSuite('p4a.videoembed.providers.revver',
                         optionflags=doctest.ELLIPSIS),
            DocTestSuite('p4a.videoembed.providers.youtube',
                         optionflags=doctest.ELLIPSIS),
            DocTestSuite('p4a.videoembed.providers.dailymotion',
                         optionflags=doctest.ELLIPSIS),
            ))

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
