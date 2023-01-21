import sys
import os

import pika
from pika.channel import Channel
from pika.spec import Basic
from pika.spec import BasicProperties
from send import email

def main():
    # Connect to rabbitmq
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host="rabbitmq")
    )
    channel = connection.channel()

    def callback(channel: Channel, method: Basic.Deliver, properties: BasicProperties, body: bytes):
        # Convert video to MP3
        err = email.notify(body)
        if err:
            # negative acknowledgement if video processing fails - keep msg on queue
            channel.basic_nack(delivery_tag=method.delivery_tag)
        else:
            # acknowledge if video processing succeeds - remove from queue
            channel.basic_ack(delivery_tag=method.delivery_tag)

    # Bind channel to video queue for video processing
    channel.basic_consume( \
        queue=os.environ.get("MP3_QUEUE"),
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