from __future__ import absolute_import

import os

__version__='0.1.3'

# Requred for a application-breaking bug in requests-oauthlib/oauthlib
os.environ['OAUTHLIB_RELAX_TOKEN_SCOPE'] = 'workaround'

from gtasks.gtasks import Gtasks
