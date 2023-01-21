import os
from typing import Union, Optional
import gridfs
import pika
import json

from flask import Flask, request, send_file, Response
from flask_pymongo import PyMongo
from bson.objectid import ObjectId

from auth import validate
from auth_svc import access
from storage import util

# Create server
server = Flask(__name__)

# Allow PyMongo to manage connections between server and mongo video/mp3 db (store video and converted mp3 files)
mongo_vid = PyMongo(server, uri="mongodb://host.minikube.internal:27017/videos")
mongo_mp3 = PyMongo(server, uri="mongodb://host.minikube.internal:27017/mp3s")

# Use MongoDB grid fs (grid file storage) (i.e. spec for storing large files in shards)
# (one collection stores file chunks, other collection stores metadata)
fs_vid = gridfs.GridFS(mongo_vid.db)
fs_mp3 = gridfs.GridFS(mongo_mp3.db)

# Create connection to RabbitMQ (queue to send messages for video processing jobs)
connection = pika.BlockingConnection(pika.ConnectionParameters(host="rabbitmq"))
channel = connection.channel()

# login route
@server.route("/login", methods=["POST"])
def login() -> Union[Optional[str], tuple[str, Optional[int]]]:
    # Attempt to log user in
    token, err = access.login(request)

    # Return result
    if err != None:
        return token
    else:
        return err

# video upload route
@server.route("/upload", methods=["POST"])
def upload() -> Union[str, tuple[str, int]]:
    # Attempt to valid user's provided JWT token
    valid_access, err = validate.validate_token(request)
    if err:
        return err

    # Deserialize JSON access string to Python string
    valid_access = json.loads(valid_access)

    # Check if user has admin privileges
    if valid_access["admin"]:
        if len(request.files) != 1:
            return "Only one file required", 400

        for f in request.files.values():
            # Upload file
            err = util.upload(f, fs_vid, channel, valid_access)

            # Return error
            if err:
                return err
        
        return "Upload successful", 200
    else:
        return "Unauthorized user", 401

# MP3 download route
@server.route("/download", methods=["GET"])
def download() -> Union[tuple[str, int], Response]:
    # Attempt to valid user's provided JWT token
    valid_access, err = validate.validate_token(request)
    if err:
        return err

    # Deserialize JSON access string to Python string
    valid_access = json.loads(valid_access)

    # Check if user has admin privileges
    if valid_access["admin"]:
        # Check that mp3 file ID exists
        fid = request.args.get("fid")
        if fid is None:
            return "File ID must be provided", 401
        
        # Retrieve MP3 file from fs_mp3
        try:
            mp3_file = fs_mp3.get(ObjectId(fid))
            return send_file(mp3_file, download_name=f"{fid}.mp3")
        except Exception as err:
            print(err)
            return "Internal server error", 400
    return "Unauthorized user", 401

if __name__ == "__main__":
    server.run(host="0.0.0.0", port=8080)