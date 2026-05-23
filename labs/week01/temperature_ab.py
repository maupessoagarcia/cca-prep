from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()
client = Anthropic()

PROMPT = "Write a short opening line for a fantasy novel."

def run(temp: float, n:int = 3):
    print(f"--- temperature = {temp} ---")
    for i in range(n):
        r = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens = 100,
            temperature=temp,
            messages=[{"role":"user","content":PROMPT}],
        )
        print(f"{i+1}:{r.content[0].text}")

run(0.0)
run(1.0)