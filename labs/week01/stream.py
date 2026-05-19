import time
from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()
client = Anthropic()

PROMPT = "Write a 200-word vivid description of a thunderstorm at sea."

# --- Pattern 1: Non-streaming (baseline) ---
print("=== NON-STREAMING ===")
t0 = time.time()

response = client.messages.create(
    model="claude-sonnet-4-6",
    max_tokens=1024,
    messages=[{"role": "user", "content": PROMPT}],
)

elapsed = time.time() - t0
print(response.content[0].text)
print(f"\n[took {elapsed:.2f}s total, nothing shown until end]\n")

# --- Pattern 2: Streaming (text only) ---
print("=== STREAMING ===")
t0 = time.time()
first_byte_time = None

with client.messages.stream(
    model="claude-sonnet-4-6",
    max_tokens=1024,
    messages=[{"role": "user", "content": PROMPT}],
) as stream:
    for text in stream.text_stream:
        if first_byte_time is None:
            first_byte_time = time.time() - t0
        print(text, end="", flush=True)

total = time.time() - t0
print(f"\n[first byte at {first_byte_time:.2f}s, total {total:.2f}s]")