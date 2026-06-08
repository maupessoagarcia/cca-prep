import json
from anthropic import Anthropic
from dotenv import load_dotenv

from pydantic import BaseModel, ValidationError
from typing import Literal

client = Anthropic()
load_dotenv()

class Review(BaseModel):
    product_category:str
    sentiment:Literal["positive","negative","mixed"]
    positives: list[str]
    negatives: list[str]
    price_mentioned: float | None=None
    would_recommend: bool

REVIEW = """Bought these for my morning runs. The cushioning is excellent and they're very
lightweight. However the laces came untied constantly and the toe box runs narrow — had to
size up. Overall happy, would recommend to other neutral-foot runners. Paid $130 on sale."""

def extract(review:str) -> Review:
    schema = json.dumps(Review.model_json_schema(),indent=2)
    r=client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=500,
        temperature=0,
        system=((f"Extract structured information from the review. "
                f"Output a single JSON object conforming to this JSON Schema:{schema}"
                f"Output JSON only.")),
        messages = [{"role":"user", "content":f"{review}"}]
        )

    text = r.content[0].text.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()
    data = json.loads(text)
    return Review.model_validate(data)


result = extract(REVIEW)
print(result.model_dump_json(indent=2))
print(f"Type is: {type(result).__name__}")
print(f"Would recommend: {result.would_recommend} (bool, not string)")