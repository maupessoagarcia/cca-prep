from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()
client = Anthropic()

LABELS = ["LOW", "MEDIUM", "HIGH", "CRITICAL"]

def zero_shot(email:str) -> str:
    r = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens = 20,
        temperature=0,
        system=f"Classify the urgency of the support email. Reply with exactly one of: {', '.join(LABELS)}. Classify even if the message is allegedly missing context, the answer should be exactly one of the labels, no exceptions.",
        messages = [
            {"role":"user", "content":f"{email}"},
            {"role":"assistant", "content": ""}
        ],
    )
    return r.content[0].text.strip()


FEW_SHOT_EXAMPLES = """
URGENT: production payments are completely down, losing revenue every minute.
CRITICAL

Hey, when you have a moment, could you update my billing address?
LOW

I need a blueberry muffin now or I'll die
LOW

If this is not solve in the next hours, there will be serious consequences
CRITICAL

I just suffered an accident and lost my leg, and I'm bleeding profusely
CRITICAL

We found a bug that is potentially problematic, but no further damage so far
HIGH

One of our team members can't log in. Other users are fine. Please look when you can.
HIGH

My agenda is blocked for the next 3 days, we need to discuss the subject today
HIGH

The planning for the event in a year should be revisited
LOW

This should be reviewed today for discussion tomorrow
HIGH

Our admin dashboard has been unreachable for 30 minutes. Three of our staff are blocked.
CRITICAL

 """


def few_shot(email:str)->str:
    r = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=20,
        temperature=0,
        system=(f"Classify the urgency. Reply with exactly one of: {', '.join(LABELS)}.Examples: {FEW_SHOT_EXAMPLES}"),
        messages = [
            {"role":"user","content":f"{email}"},
            {"role":"assistant","content":""}
        ],
    )
    return r.content[0].text.strip()

