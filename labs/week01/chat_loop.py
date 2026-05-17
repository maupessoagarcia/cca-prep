from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()
client = Anthropic()
SYSTEM = "You are a friendly Python tutor. Keep answers under 3 sentences."
history = []
print("Chat with Claude. Press Ctrl-C to exit.")

while True:
    try:
        user_input = input("You: ").strip()
        if not user_input:
            continue

        history.append({"role": "user", "content": user_input})

        response = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=1024,
            system=SYSTEM,
            messages=history,
            )
        assistant_text = response.content[0].text
        history.append({"role": "assistant", "content": assistant_text})
        print(f"Claude: {assistant_text}")

    except KeyboardInterrupt:
        print("Bye.")
        break