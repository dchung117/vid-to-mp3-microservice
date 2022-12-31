import jwt, datetime, os
from flask import Flask, request
from flask_mysqldb import MySQL

# Create server (registry for views, URLs, template configs, etc.)
server = Flask(__name__)

# Create mysql object
mysql = MySQL(server)

# Set up config
server.config["MYSQL_HOST"] = os.environ.get("MYSQL_HOST")
server.config["MYSQL_USER"] = os.environ.get("MYSQL_USER")
server.config["MYSQL_PASSWORD"] = os.environ.get("MYSQL_PASSWORD")
server.config["MYSQL_DB"] = os.environ.get("MYSQL_DB")
server.config["MYSQL_PORT"] = os.environ.get("MYSQL_PORT")

# Create routes
@server.route("/login", methods=["POST"])
def login():
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