import json
from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()
client = Anthropic()

REVIEW = """Bought these for my morning runs. The cushioning is excellent and they're very
lightweight. However the laces came untied constantly and the toe box runs narrow — had to
size up. Overall happy, would recommend to other neutral-foot runners. Paid $130 on sale."""

SCHEMA = """{
"product_category": string,
"sentiment": "positive" | "negative" | "mixed",
"positives": [string],
"negatives": [string],
"price_mentioned": number | null,
"would_recommend": boolean
}"""


def extract(review:str)-> dict:
    r = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens = 500,
        temperature = 0,
        system = ("Extract structured information from the review. "
                  f"Output a single valid JSON object matching this schema:{SCHEMA}"
                  "Output JSON only. No markdown, no preamble."),
        messages = [
            {"role":"user","content":f"{review}"},
            ],
    )
    raw = r.content[0].text
    return json.loads(raw)

result = extract(REVIEW)
print(json.dumps(result,indent=2))