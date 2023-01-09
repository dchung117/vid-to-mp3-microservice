import os
import gridfs
import pika
import json

from flask import Flask, request
from flask_pymongo import PyMongo

from auth import validate
from auth_svc import access
from storage import util

# Create server
server = Flask(__name__)

# Initialize mongo db uri
server.config["MONGO_URI"] = "mongodb://host.minikube.internal:27017/videos"

# Allow PyMongo to manage connections between server and mongo db (store video and converted mp3 files)
mongo = PyMongo(server)

# Use MongoDB grid fs (grid file storage) (i.e. spec for storing large files in shards)
# (one collection stores file chunks, other collection stores metadata)
fs = gridfs.GridFS(mongo.db)

# Create connection to RabbitMQ (queue to send messages for video processing jobs)
connection = pika.BlockingConnection(pika.ConnectionParameters(host="rabbitmq"))
channel = connection.channel()

# login route
@server.route("/login", methods=["POST"])
def login():
    # Attempt to log user in
    token, err = access.login(request)

