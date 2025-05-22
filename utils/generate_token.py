"""Generate a token for testing the api."""

import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from people_api.auth import create_token

if len(sys.argv) > 1:
    try:
        registration_id = int(sys.argv[1])
    except ValueError:
        print("Invalid registration_id. Must be an integer.")
        sys.exit(1)
else:
    registration_id = 5

print(create_token(registration_id=registration_id, ttl=3600))
