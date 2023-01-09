import jwt, datetime, os
from flask import Flask, request
from flask_mysqldb import MySQL

# Create server (registry for views, URLs, template configs, etc.)
server = Flask(__name__)

# Create mysql object (database to store user credentials)
mysql = MySQL(server)

# Set up config
server.config["MYSQL_HOST"] = os.environ.get("MYSQL_HOST")
server.config["MYSQL_USER"] = os.environ.get("MYSQL_USER")
server.config["MYSQL_PASSWORD"] = os.environ.get("MYSQL_PASSWORD")
server.config["MYSQL_DB"] = os.environ.get("MYSQL_DB")
server.config["MYSQL_PORT"] = os.environ.get("MYSQL_PORT")

# Create routes
@server.route("/login", methods=["POST"])
def login() -> tuple[str, int]:
    # retrieve login authentication header
    auth = request.authorization
    if not auth:
        return "Missing login credentials", 401

    # check mysqldb for authorized users
    username = auth.username
    password = auth.password

    # create mysql cursor
    cursor = mysql.connection.cursor()
    
    # query user table
    res = cursor.execute(
        f"SELECT email, password FROM user WHERE email={username}"
    )

    # Validate login
    if res > 0:
        user_row = cursor.fetch(1)
        email, password_db = user_row[0], user_row[1]

        # Check if provided email and password are valid
        if (username != email) or (password != password_db):
            return "Invalid username and/or password", 401
        else:
            return create_jwt(username, os.environ.get("JWT_SECRET"), True)
    else:
        return "Invalid credentials", 401

@server.route("/validate", methods=["POST"])
def validate() -> tuple[str, int]:
    # Get encoded JWT
    encoded_jwt = request.headers["authorization"]

    # Return error if missing auth
    if not encoded_jwt:
        return "No authorization", 401
    
    # Split encoded_jwt
    auth_type, enc_token = encoded_jwt.split(" ")

    # Return error if auth_type is not bearer
    if auth_type != "Bearer":
        return "Not authorized.", 403
    
    # Decode the token
    try:
        dec_token = jwt.decode(enc_token, os.environ.get("JWT_SECRET"), algorithm="HS256")
    except:
        return "Not authorized", 403
    
    return dec_token, 200

def create_jwt(username: str, secret: str, is_admin: bool) -> tuple[str, int]:
    """
    Generate JWT for validated user.
    """
    return jwt.encode(
        payload={
            "username": username,
            "exp": datetime.datetime.utcnow() + datetime.timedelta(days=1), # token valid for one day
            "iat": datetime.datetime.utcnow(),
            "admin": is_admin
            },
        key=secret,
        algorithm="HS256"
    )

if __name__ == "__main__":
    # run server on port 5000
    server.run(host="0.0.0.0", port=5000)