import os
import base64
from openai import OpenAI

def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')


api_key = os.environ.get("API_KEY", None)
if api_key is None:
    print(os.environ.keys())
    assert False, "Missing API_KEY"


client = OpenAI(api_key=api_key)

base64_image = encode_image("./uploaded_images/test.jpg")

response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[
        {
            "role": "user",
            "content": [
                {"type": "text", "text": "What’s in this image? Less text is better. Do not lead with the image shows"},
                {
                    "type": "image_url",
                    "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}
                }
            ]
        }
    ]
)

print(response.choices[0].message.content)
