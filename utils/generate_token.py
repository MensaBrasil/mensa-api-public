"""Generate a token for testing the api."""

import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from people_api.auth import create_token

print(create_token(registration_id=5, ttl=3600))
