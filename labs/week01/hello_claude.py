import os
from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()
client = Anthropic()

response = client.messages.create(
    model="claude-sonnet-4-6",
    max_tokens=1024,
    system = "You answer in a way a 10 year old child can understand and never forget",
    messages=[{"role": "user", "content": "What is the Model Context Protocol?"}],
)
print(response.content[0].text)