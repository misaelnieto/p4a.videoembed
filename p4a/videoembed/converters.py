"""Used to be a module for embed providers.  Now just a delegator to the
``providers`` package for BBB reasons.
"""

# BBB
from p4a.videoembed.providers.youtube import (youtube_check,
                                              youtube_generator,
                                              youtube_mediaurl)
from p4a.videoembed.providers.googlevideo import (google_check,
                                                  google_generator)
from p4a.videoembed.providers.genericflv import (flv_check,
                                                 flv_generator)
from p4a.videoembed.providers.revver import (onerevver_check,
                                             onerevver_generator,
                                             revver_check,
                                             revver_generator)
from p4a.videoembed.providers import (vimeo_check,
                                      vimeo_generator)
from p4a.videoembed.providers import (vmix_check,
                                      vmix_generator)
from p4a.videoembed.providers import (yahoo_check,
                                      yahoo_generator)
from p4a.videoembed.providers import (ifilm_check,
                                      ifilm_generator)
from p4a.videoembed.providers import (myspace_check,
                                      myspace_generator)
from p4a.videoembed.providers import (metacafe_check,
                                      metacafe_generator)
from p4a.videoembed.providers import (collegehumor_check,
                                      collegehumor_generator)
from p4a.videoembed.providers import (veoh_check,
                                      veoh_generator)
from p4a.videoembed.providers import (quicktime_check,
                                      quicktime_generator)
from p4a.videoembed.providers import (vspot_check,
                                      vspot_generator)
from p4a.videoembed.providers import (liveleak_check,
                                      liveleak_generator)
from p4a.videoembed.providers import (superdeluxe_check,
                                      superdeluxe_generator)
