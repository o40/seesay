"""
HTTP server to listen to POST messages containing images.
The image is then sent to a AI description service which
result is used to update a local page.
"""


import base64
import io
import os
import time

from datetime import datetime
from PIL import Image

from flask import Flask, request, render_template
from flask_cors import CORS
from flask_socketio import SocketIO
from openai import OpenAI

app = Flask(__name__)
socketio = SocketIO(app)
CORS(app, resources={r"/*": {"origins": "*"}})

api_key = os.environ.get("API_KEY", None)
if api_key is None:
    assert False, "Missing API_KEY"
client = OpenAI(api_key=api_key)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/upload", methods=["POST"])
def upload_image():
    image_received_time = time.time()
    image = Image.open(io.BytesIO(request.get_data()))

    _save_image(image)
    description = _get_description_from_image(image)
    _save_description(description)

    print(
        f"Emitting new description: {description} (latency: {time.time() - image_received_time}) s"
    )
    socketio.emit("new_description", {"message": description})

    return "OK", 200


def _base64_encode_image(image):
    img_buffer = io.BytesIO()
    image.save(img_buffer, format="JPEG")
    byte_data = img_buffer.getvalue()
    return base64.b64encode(byte_data).decode("utf-8")


def _get_description_from_image(image):
    base64_image = _base64_encode_image(image)

    # TODO: Optimize prompt to reduce fluff (use test.py)

    # prompt = "Start with the main subject or scene. "
    # prompt += "List key objects using brief, descriptive phrases. "
    # prompt += "Use spatial prepositions to indicate locations. "
    # prompt += "Employ concise modifiers for essential details. "

    prompt = "What’s in this scene and where? Less text is better."

    # prompt = "Describe the scene for blind person less text is better"

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"},
                    },
                ],
            }
        ],
    )

    return response.choices[0].message.content


def _save_image(image):
    datestr = datetime.now().strftime("%Y-%m-%d_%H%M%S.%f")[:-3]
    filename = f"./uploaded_images/{datestr}.jpg"
    image.save(fp=filename)


def _save_description(description):
    datestr = datetime.now().strftime("%Y-%m-%d_%H%M%S.%f")[:-3]
    filename = f"./uploaded_images/{datestr}.txt"
    with open(
        file=filename,
        mode="w",
        encoding="utf-8",
    ) as message_file:
        message_file.write(description)


if __name__ == "__main__":
    if not os.path.exists("uploaded_images"):
        os.makedirs("uploaded_images")
    socketio.run(app, host="<YOUR HOST>", port=80, allow_unsafe_werkzeug=True)
