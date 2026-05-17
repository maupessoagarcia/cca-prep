Claude is stateless between API calls
Two roles only: user (you, or your app's user) and assistant (Claude). They must alternate — never two user messages in a
row, never two assistant messages in a row. Always end on a user message; Claude's response becomes the next assistant turn that
you append.
System prompts are separate. A system is not a message in the list — it's its own top-level parameter

Claude's API surface is organized into five areas:

    Model capabilities: Control how Claude reasons and formats responses.
    Tools: Let Claude take actions on the web or in your environment.
    Tool infrastructure: Handles discovery and orchestration at scale.
    Context management: Keeps long-running sessions efficient.
    Files and assets: Manage the documents and data you provide to Claude.


This is a simple multi-turn chatbot that talks to Claude via the Anthropic Python SDK.This is a simple multi-turn chatbot that talks to Claude via the Anthropic Python SDK. Here's how it works:
Setup

Imports the Anthropic client and dotenv (which loads your ANTHROPIC_API_KEY from a .env file)
Initializes the client and defines a system prompt that makes Claude behave as a concise Python tutor
Creates an empty history list to store the conversation

The main loop
The while True loop runs forever until the user hits Ctrl-C, which raises a KeyboardInterrupt and triggers the except block to exit cleanly.
Each iteration:

Gets user input — skips empty lines with continue
Appends to history — adds the user's message as {"role": "user", "content": ...}
Calls the API — sends the full conversation history each time, which is what gives Claude memory of the conversation (the API itself is stateless)
Extracts the reply — response.content[0].text gets the text from the first content block
Appends Claude's reply to history — so it's included in the next API call
Prints the response

Key design pattern: The history list grows with every exchange. By sending the entire list on every request, Claude can refer back to earlier messages — this is how all multi-turn Claude apps work.
One small bug: the print statement uses {{assistant_text}} with double braces, which would literally print {assistant_text} instead of the variable's value. It should be {assistant_text} (single braces)