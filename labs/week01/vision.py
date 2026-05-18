import base64
from pathlib import Path
from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()
client = Anthropic()

#Read the image and base64-encode it

image_path = Path("labs/week01/datachart.png")
image_data = base64.standard_b64encode(image_path.read_bytes()).decode("utf-8")
media_type = "image/png"

response = client.messages.create(
    model="claude-sonnet-4-6",
    max_tokens=1024,
    messages=[
        {"role": "user",
         "content": [
             {"type": "image",
              "source": {
                  "type": "base64",
                  "media_type": media_type,
                  "data": image_data,
                  },
                },
                {"type": "text", 
                 "text": "Summarize the data trends on this chart"},
                 ],
            }
        ],
    )

print(response.content[0].text)