from typing import Optional
from werkzeug.datastructures import FileStorage
import pika, json
from gridfs import GridFS
from pika.adapters.blocking_connection import BlockingChannel

def upload(file: FileStorage, grid_fs: GridFS, channel: BlockingChannel, valid_access: dict) -> Optional[tuple[str, int]]:
    # Try to upload file to MongoDB via GridFS
    try:
        fid = grid_fs.put(file)
    except Exception as err:
        return "Internal server error", 500
    
    # Create message to pass to queue
    msg = {
        "video_fid": str(fid),
        "mp3_fid": None,
        "username": valid_access["username"]
    }

    try:
        channel.basic_publish(
            exchange="",
            routing_key="video",
            body=json.dumps(msg),
            properties=pika.BasicProperties(
                delivery_mode=pika.spec.PERSISTENT_DELIVERY_MODE # queue and messages are retained if a pod needs to be restarted
            )
        )
    except:
        # Delete video file from mongodb if enqueue fails
        grid_fs.delete(file_id=fid)
        
        return "Internal server error", 500