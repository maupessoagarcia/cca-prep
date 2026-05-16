Day 1 - What did I just see/learn?

1- Installed packages, including UV and anthropic.
2- Learned how to set .gitignore and .dotenv, to protect my API key
3- "Created" a python script that talks to API, and answers questions

Explanation of the MCP:

## What MCP Does 🌉

**MCP is like building special doors** that let me safely peek into different places and tools!

Think of it like this:

- **Without MCP**: I'm a brain in a jar - smart but can't reach anything
- **With MCP**: I have special tunnels connecting me to your files, apps, and tools

## A Simple Example 🎮

Imagine you have:

- A toy box (your files)
- A coloring book (a drawing app)
- A calendar on your wall

**MCP creates safe "helper robots"** that can:

1. Look in your toy box and tell me what's there
2. Draw in your coloring book when I give instructions
3. Read your calendar to me

## Why Is It Cool? ✨

- It's **safe** - like having a trusted grown-up helper
- It works with **lots of different things** - one system, many connections
- Other people can build **new doors** to new places!

**In short**: MCP helps AI assistants like me actually DO things in the real world, not just talk about them! 🎉

Python File Debunk (hello_claude.py):

Good instinct — never run code you don't understand. Let me walk through it line by line.

```python
import os
from anthropic import Anthropic
from dotenv import load_dotenv
```

These three lines pull in tools from elsewhere so you don't have to write them yourself.

- `os` is a standard Python module for interacting with the operating system — reading environment variables, file paths, etc. You don't actually use it directly in this file (I included it out of habit, you can delete that line and the script still works), but it's commonly there for env var work.
- `from anthropic import Anthropic` reaches into the `anthropic` package you installed with `uv add anthropic` and grabs the `Anthropic` class. That class is your gateway to the API.
- `from dotenv import load_dotenv` grabs a helper function from `python-dotenv` that reads `.env` files. Without it, your API key would have to live as a system-wide environment variable or — worse — hardcoded in the script.

```python
load_dotenv()
```

This call opens the `.env` file in your current directory, reads each `KEY=VALUE` line, and sets each one as an environment variable for the running Python process. After this line runs, the line `ANTHROPIC_API_KEY=sk-ant-...` in your `.env` file becomes an env var that Python can see. The variable disappears when the script exits — it's not permanently added to Windows. This is a security pattern: your key never gets typed into code, never gets committed to git (because `.env` is in `.gitignore`), and only exists in memory while your script runs.

```python
client = Anthropic()
```

This creates an instance of the `Anthropic` class — a "client" object that knows how to talk to Anthropic's servers. Notice there are no arguments inside the parentheses. That's deliberate: the client automatically looks for an environment variable named exactly `ANTHROPIC_API_KEY`. It finds the one `load_dotenv()` just set, reads it, and stores it for later use. From this point on, `client` is your handle for every API call you'll make. Think of it like opening a phone line to Anthropic — you do it once and reuse the connection.

```python
response = client.messages.create(
    model="claude-sonnet-4-5",
    max_tokens=1024,
    messages=[{"role": "user", "content": "In one sentence, what is the Model Context Protocol?"}],
)
```

This is the actual API call — where money changes hands and Claude does its thinking. Breaking it down:

- `client.messages.create(...)` is the method that sends a request to the **Messages API** (Anthropic's main endpoint). The `.messages.create` naming follows a pattern used across many APIs: a resource (`messages`) and an action on it (`create`). You're literally asking the API to create a new message in a conversation.

- `model="claude-sonnet-4-5"` tells the API which model to use. Anthropic publishes a few — Haiku (fastest, cheapest), Sonnet (balanced default), Opus (most capable, slowest, most expensive). The exact string `claude-sonnet-4-5` is a model identifier that may have changed since I wrote the script. If the script errors with "model not found," you'll need to check the current docs for the right ID. I'll verify the current names for you in a second.

- `max_tokens=1024` is a safety ceiling on how long Claude's response can be. Tokens are roughly ¾ of a word — 1024 tokens is around 750 words. If Claude tries to write something longer, it gets cut off mid-sentence. You set this to protect yourself from runaway costs (you pay per token output) and to keep responses reasonable.

- `messages=[...]` is the conversation history you're sending. It's a list because, in multi-turn conversations, you'd send the whole history each time — Claude is stateless between calls, it doesn't remember anything from previous requests. Right now you're sending just one message.

- `{"role": "user", "content": "In one sentence..."}` is a single message in that list. Every message needs a `role` (either `"user"` or `"assistant"`) and `content` (the text). You're playing the user role here.

When this method runs, your script pauses for a couple of seconds while:

1. Your local Python code packages the request as JSON.
2. The `anthropic` library sends it over HTTPS to Anthropic's servers, including your API key in the headers.
3. Anthropic's servers verify the key, route the request to a Claude model, the model generates a response token by token.
4. The full response is bundled up and sent back to your script.
5. The `anthropic` library parses the JSON into a Python object called `Message`, and that object is assigned to your `response` variable.

```python
print(response.content[0].text)
```

The `response` object has structure. The most important field is `content`, which is a **list** (not a string!) of "content blocks." Most simple text responses contain exactly one block — a text block — so `response.content[0]` grabs it, and `.text` pulls out the actual string Claude wrote.

The reason it's a list of blocks rather than a single string is forward-looking: when you get to tool use in Week 3, Claude's response can contain _multiple_ blocks — say, a text block ("Let me check the weather...") followed by a `tool_use` block (the actual tool call). The list-of-blocks design accommodates that. For now, you only ever look at `content[0].text`.

`print(...)` writes that text to your terminal.

---

**A small but important detail** — let me verify the current model name so the script actually runs, since model identifiers do change:Good — the model string I gave you is now outdated. Models have moved on since the script was written. Two corrections for your `hello_claude.py`:

**1. Use a current model name.** As of today, the right choice for learning is `claude-sonnet-4-6` — it's the daily-driver model, balanced cost ($3 in / $15 out per million tokens, so your test calls cost fractions of a cent). Replace this line:

```python
model="claude-sonnet-4-5",
```

with:

```python
model="claude-sonnet-4-6",
```

If you want to try the most capable model for the "switch and feel the difference" experiment I described, the current Opus is `claude-opus-4-7`.

**2. Don't worry about memorizing model names.** They change every few months — `claude-sonnet-4-6` will eventually be deprecated too. The pattern (family-size-version) stays stable, and you can always look up the current list at [docs.claude.com → Models overview](https://docs.claude.com/en/about-claude/models/overview).

Try running the script with the updated model name and let me know what happens — either the haiku of an answer comes back, or you hit an error and we debug together. Both outcomes are progress.
