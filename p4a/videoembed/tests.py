"""Test library
"""
import unittest

def test_suite():
    from zope.testing.doctestunit import DocTestSuite
    return unittest.TestSuite((
            DocTestSuite('p4a.videoembed.registry'),
            DocTestSuite('p4a.videoembed.converters'),),)

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
