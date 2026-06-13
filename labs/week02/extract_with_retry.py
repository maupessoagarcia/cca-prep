import json
from anthropic import Anthropic
from dotenv import load_dotenv
from pydantic import BaseModel, ValidationError
from typing import Literal


load_dotenv()
client = Anthropic()

MAX_RETRIES = 3

class Review(BaseModel):
    product_category:str
    sentiment:Literal["positive","negative","mixed"]
    positives:list[str]
    negatives:list[str]
    price_mentioned: float | None=None
    would_recommend: bool


class ExtractionError(Exception):
    """Raised when extraction fails after all retries."""

def extract(review:str)-> Review:
    schema = json.dumps(Review.model_json_schema(),indent=2)
    system = (f"Extract structured information from the review. "
              #f"Output a JSON object with a sentiment field that is a list of strings"
              f"Output a single JSON object conforming to this JSON Schema:{schema}"
              f"Output JSON only, no markdown, no preamble."
              
              )
    messages: list[dict] = [{
        "role":"user", "content":f"{review}"
    }]
    last_error = None
    for attempt in range(1,MAX_RETRIES + 1):
        r=client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=500,
            temperature=0,
            system=system,
            messages = messages
        )
        raw = r.content[0].text

        try:
            data = json.loads(raw)
            return Review.model_validate(data)
        except (json.JSONDecodeError,ValidationError) as e:
            last_error = e
            print(f" [attempt {attempt} failed: {type(e).__name__}: {str(e)[:120]}]")

            if attempt == MAX_RETRIES:
                break

            # Re-prompt: append Claude's bad output + a corrective user message,
            # then a fresh prefill.

            messages = [
                {"role":"user","content":f"{review}"},
                {"role":"assistant","content":raw},
                {"role":"user","content":(
                    f"That output failed validation with: {type(e).__name__}: {str(e)[:200]}."
                    f"Please re-output a corrected JSON object that matches the schema. "
                    f"Output JSON only."
                )}
            ]
    raise ExtractionError(f"Failed after {MAX_RETRIES} attempts. Last error: {last_error}")

REVIEW = """Bought these for my morning runs. Cushioning is excellent. Laces came untied
constantly. Sized up because toe box runs narrow. Would recommend. Paid $130."""

result = extract(REVIEW)
print(result.model_dump_json(indent=2))
    