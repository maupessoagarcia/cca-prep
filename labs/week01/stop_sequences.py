from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()
client = Anthropic()

# Without stop_sequences — Claude tends to add commentary after the JSON.

r1 = client.messages.create(
    model="claude-sonnet-4-6",
    max_tokens = 300,
    messages=[{
        "role":"user",
        "content":"Output a JSON array of three random colors as hex codes. Wrap in```json ... ```"
    }]
)

print("--- WITHOUT stop_sequences ---")
print(r1.content[0].text)

# With stop_sequences=["```"] — Claude stops the moment it closes the code fence

r2 = client.messages.create(
    model="claude-sonnet-4-6",
    max_tokens = 300,
    stop_sequences = ["\n```"],
    messages=[{
        "role":"user",
        "content":"Output a JSON array of three random colors as hex codes. Start with ```json"
    }]
)

print("--- WITH stop_sequences=[\"```\"] ---")
print(r2.content[0].text)
print(f"stop_reason: {r2.stop_reason}")