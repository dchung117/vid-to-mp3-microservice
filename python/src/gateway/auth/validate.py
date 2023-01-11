import os
from typing import Union, Optional
import requests
from flask import request

def validate_token(req: request) -> Union[Optional[str], Optional[tuple[str, int]]]:
    # Check for authorization header
    if "Authorization" not in req.headers:
        return None, ("Missing credentials", 401)
    
    # Set authorization token
    token = request.headers["Authorization"]
    if token != None:
        return None, ("Missing credentials", 401)
    
    # Validate the user JWT token
    response = requests.post(f"http://{os.environ.get('AUTH_SVC_ADDRESS')}/validate",
        headers={"Authorization": token}
    )

    # Return response
    if response.status_code == 200:
        return response.txt, None
    else:
        return None, (response.txt, response.status_code)