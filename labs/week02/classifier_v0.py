from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()
client = Anthropic()

EMAIL = """Hi,
Our entire payment system has been down for the last 3 hours. Customers are calling. We are
bleeding revenue. Please help ASAP. We pay $5000/month for this service.
— Jamie, COO, Acme Corp"""

EMAIL = "Hi, when you get a chance — could you update my billing address?"

# v0: naive prompt

def classify_naive(email:str) -> str:
    r = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens = 100,
        messages=[{"role": "user", "content": f"What is the urgency of this email? Email:{email}"}],
        )
    return r.content[0].text


#v1 specific instructions + constrained vocabulary

def classify_specific(email:str) -> str:
    r = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=20,
        temperature=0,
        system=("You classify support emails by urgency. "
    "Reply with exactly one word from this set: LOW, MEDIUM, HIGH, CRITICAL. "
    "No explanation, no punctuation, no extra text."),
        messages=[{"role": "user", "content": email}],
    )
    return r.content[0].text.strip()


# v2: XML tags (parsed from response; prefill not supported on this model)
def classify_xml_prefill(email:str)-> str:
    import re
    r = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=30,
        temperature=0,
        system=("You classify support emails by urgency into one of LOW, MEDIUM, HIGH, CRITICAL. "
    "Respond with ONLY: <label>LEVEL</label>"),
        messages=[{"role":"user","content":f"{email}"}],
    )
    text = r.content[0].text.strip()
    m = re.search(r"<label>(.*?)</label>", text)
    return m.group(1).strip() if m else text


print("v0 naive: ", classify_naive(EMAIL))
print("v1 specific: ", classify_specific(EMAIL))
print("v2 xml+prefill: ", classify_xml_prefill(EMAIL))


    