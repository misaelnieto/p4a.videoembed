from setuptools import setup, find_packages
import sys, os

version = '0.1'

setup(name='videoembed',
      version=version,
      description="A registry and adapters for converting urls for various video sharing sites into embed codes.",
      long_description="""\
""",
      classifiers=[], # Get strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      keywords='Embedded Video Plone',
      author='Alec Mitchell',
      author_email='apm13@columbia.edu',
      url='http://www.plone4artists.org/svn/projects/p4a.videoembed',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['p4a'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
