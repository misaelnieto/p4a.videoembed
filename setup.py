from setuptools import setup, find_packages

version = '1.1b1'

setup(name='p4a.videoembed',
      version=version,
      description="A registry and adapters for converting urls for various video sharing sites into embed codes.",
      long_description="""\
""",
      classifiers=[
          'Framework :: Zope3',
          'Programming Language :: Python',
          'License :: OSI Approved :: GNU General Public License (GPL)',
          'Topic :: Software Development :: Libraries :: Python Modules',
          'Topic :: Multimedia :: Video'
          ],
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
          'setuptools',
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
