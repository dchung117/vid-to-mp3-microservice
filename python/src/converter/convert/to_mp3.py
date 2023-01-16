import os
import json
from pathlib import Path
from typing import Optional
from bson.objectid import ObjectId
import tempfile

import pika
from pika.channel import Channel
from gridfs import GridFS

import moviepy.editor

def start(msg: bytes, fs_vid: GridFS, fs_mp3: GridFS, channel: Channel) -> Optional[str]:
    # Load message as Python JSON object
    msg = json.loads(msg)

    # Create empty temp file
    tmp_file = tempfile.NamedTemporaryFile()

    # Get the video file from fs_vid
    vid_out = fs_vid.get(ObjectId(msg["video_fid"]))

    # Add video file content to tmp_file
    tmp_file.write(vid_out.read())

    # Extract audio from video
    audio_out = moviepy.editor.VideoFileClip(tmp_file.name).audio

    # Close tmp_file; will be deleted
    tmp_file.close()

    # Write audio to tmp_file directory
    tmp_file_audio_path = Path(tempfile.gettempdir()) / f"{msg['video_fid']}.mp3"
    audio_out.write_audiofile(tmp_file_audio_path)

    # Save audio file to fs_mp3
    with open(tmp_file_audio_path, "rb") as f:
        data = f.read()
        audio_fid = fs_mp3.put(data)
    
    # Remove audio tmp_file
    os.remove(tmp_file_audio_path)

    # Update msg
    msg["mp3_fid"] = str(audio_fid)

    # Enqueue msg to mp3 queue
    try:
        channel.basic_publish(
            exchange="",
            routing_key=os.environ.get("MP3_QUEUE"),
            body=json.dumps(msg),
            properties=pika.BasicProperties(
                delivery_mode=pika.spec.PERSISTENT_DELIVERY_MODE
            )
        )
    except Exception as err:
        # Delete the audio file if error occured
        fs_mp3.delete(audio_fid)
        return "Failed to publish message on mp3 queue."

