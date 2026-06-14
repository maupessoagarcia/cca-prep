import time
from anthropic import Anthropic
from typing import Literal
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()
client = Anthropic()


# A big static system prompt — caching only kicks in above 1024 tokens.
LONG_SYSTEM_BASE = """You extract structured information from product reviews.
Be thorough and capture specific phrases for positives and negatives."""

LONG_SYSTEM = LONG_SYSTEM_BASE + ("\nMore guidance: be precise. Quote specific phrases. " * 50)

class Review(BaseModel):
    product_category:str
    sentiment: Literal["positive","negative","mixed"]
    positives: list[str]
    negatives: list[str]
    price_mentioned: float | None = None
    would_recommend: bool


REVIEWS = [
"Loved the running shoes. Light, cushioned. Paid $130.",
"Coffee grinder works but is way too loud. $80.",
"Watch band broke after a month. Returning. Was $50.",
"Tent kept me dry through a storm — fantastic.",
"Backpack zipper failed on day 2. $120 down the drain.",
]


def extract(review_text:str, use_cache:bool):
    system_blocks = [{
        "type":"text",
        "text":LONG_SYSTEM,
        **({"cache_control":{"type":"ephemeral"}} if use_cache else {})
    }]

    response =  client.messages.parse(
        model = "claude-sonnet-4-6",
        max_tokens = 400,
        system = system_blocks,
        messages = [{"role":"user","content":review_text}],
        output_format = Review,
    )
    return response.usage


def run_batch(use_cache:bool):
    label = "WITH CACHE" if use_cache else "WITHOUT CACHE"
    print(f"\n=== {label} ===")
    total_input = total_cache_read = total_cache_create = 0
    t0 = time.time()
    for r in REVIEWS:
        u = extract(r, use_cache)
        total_input += u.input_tokens
        total_cache_read += getattr(u, "cache_read_input_tokens",0) or 0
        total_cache_create += getattr(u, "cache_creation_input_tokens",0) or 0
    print(f" Uncached input: {total_input:,}")
    print(f" Cache reads: {total_cache_read:,}")
    print(f" Cache creates: {total_cache_create:,}")
    print(f" Elapsed: {time.time() - t0:.2f}s")


run_batch(use_cache=False)
run_batch(use_cache=True)
