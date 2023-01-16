import sys
import os
import time

import pika
from pika.channel import Channel
from pika.spec import BasicDeliver
from pika.spec import BasicProperties

from pymongo import MongoClient
import gridfs

from convert import to_mp3

def main():
    # Start mongoclient
    client = MongoClient("host.minikube.internal", 27017)

    # Get video and mp3 databases
    db_vid = client.videos
    db_mp3 = client.mp3s

    # Create gridfs instance
    fs_vid = gridfs.GridFS(db_vid)
    fs_mp3 = gridfs.GridFS(db_mp3)

    # Connect to rabbitmq
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host="rabbitmq")
    )
    channel = connection.channel()

    def callback(channel: Channel, method: BasicDeliver, properties: BasicProperties, body: bytes):
        # Convert video to MP3
        err = to_mp3.start(body, fs_vid, fs_mp3, channel)
        if err:
            # negative acknowledgement if video processing fails - keep msg on queue
            channel.basic_nack(delivery_tag=method.delivery_tag)
        else:
            # acknowledge if video processing succeeds - remove from queue
            channel.basic_ack(delivery_tag=method.delivery_tag)

    # Bind channel to video queue for video processing
    channel.basic_consume(
        queue=os.environ.get("VID_QUEUE"),
        on_message_callback=callback
    )
    print("Awaiting messages. Press CTRL+C to exit.")

    # Commence channel to consume messages from video queue
    channel.start_consuming()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("Video channel processing interrupted.")

        # Shutdown channel service
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)