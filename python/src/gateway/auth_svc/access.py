import os
from flask import request
import requests

def login(req: request) -> tuple[str, int]:
    # Get authorization
    auth = req.authorization

    # Return error for no authorization
    if not auth:
        return None, ("Missing login credentials", 401)

    # Create user authorization
    basic_auth = (auth.username, auth.password)

    # Send login request to auth service
    response = requests.post(f"http://{os.environ.get('AUTH_SVC_ADDRESS')}/login",
        auth=basic_auth)
    
    # Check response status
    if response.status_code == 200:
        return response.txt, None
    else:
        return None, (response.txt, response.status_code)