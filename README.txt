p4a.videoembed Package Readme
=========================

Overview
--------

A registry and adapters for converting urls for various video sharing sites
into embed codes.

This package provides some functions and zope3 components for converting urls
from common streaming video sites into embed codes.  The purpose is to allow
for content types that provide a user entered url to display embeded video
based on that url.  This is to avoid allowing users to enter raw html embed
codes which is potentially dangerous and cumbersome.  It also allows for
dynamic scaling of the generated embed code to fit with your page layout.

Components
----------

At the heart of this product is a set of named adapters.  These adapters adapt
a string (url) and an integer (width) and return a unicode embed code.
Currently, adapters are provided for the following video sharing sites:

YouTube
Google Video
Yahoo Video
Revver (both the original site and one.revver.com)
Vimeo
Vmix
Blip.tv

But adding more is as simple as creating a function that checks if the url
is appropriate for the site you want, and another to convert it into an
embed code.  You register the latter function as a named adapter, like:

  <adapter
      for="str int"
      name="youtube"
      provides=".interfaces.IEmbedCode"
      factory=".converters.youtube_generator"
      />

And then register the name and url checking method with a global registry:

    from p4a.videoembed.registry import register_converter
    register_converter('youtube', youtube_check_func)

You may optionally provide an integer 'index' on registration to determine the
relative order in which the check is made (more specific checks should go
earlier).

Getting the Embed Code
----------------------

There are a couple ways to generate an embed code, depending on your usecase.
The easiest is single adaptation of a url:

    from p4a.videoembed.interfaces import IEmbedCode
    embed_code = IEmbedCode(url)

This gives an embed of a preset width (425px), to get a custom width, you
multiadapt:

    from zope.component import getMultiAdapter
    embed_code = getMultiAdapter((url, width), IEmbedCode)

There is also a convenient view provided fro use from restricted code, it
optionally takes a url and width and returns an embed code.  If the url
is omitted, then it will try and get one from the context by adapting to
ILinkProvider (which indicates the presence of a getLink method).

       <div class="EmbedCode"
            tal:define="embed_view nocall:context.@@video-embed.htm;
                        default_embed embed_view;
                        custom_width python:embed_view(width=500);
                        custom_url python:embed_view(url='http://www.youtube.com/watch?v=1111', width=250)"
            tal:replace="structure default_embed"

This shows how you can use the view from tal to generate a url from an object
that implements or is adaptable to ILinkProvider, or using an explicit url
from any object.

In all of these methods the adapter checks the global utility that the named
adapters are registered with and finds the appropriate one for the given url.

I hope you find this useful.

Author: Alec Mitchell <apm13@columbia.edu>
Sponsor: The Daily Reel http://www.thedailyreel.com
