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
            ))

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
