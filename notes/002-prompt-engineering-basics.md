1. Be specific. "Summarize this" is vague. "Summarize this in three bullet points, each under 15 words, focused on financial
   implications" is specific. Specificity reduces variance.

2. Give examples (few-shot). Showing 2–3 worked examples of input→output is almost always more effective than describing the
   format in prose. Comes up tomorrow.

3. Use XML tags. Wrap distinct sections in tags like <document>...</document> and <instructions>...</
   instructions> . Claude was trained to attend to XML structure; this measurably improves performance on complex prompts.

4. Prefill the assistant turn. You can include an empty (or partial) assistant message at the end of messages ; Claude
   continues from where you left off. Starting with { forces JSON. Starting with <analysis> forces structured analysis. This is the
   most exam-favorite technique on the test.

5. Chain of thought. Ask Claude to think before answering — "think step by step in <thinking> tags, then give your final answer in
   <answer> tags." For hard reasoning tasks this dramatically improves correctness, at the cost of more output tokens.

---

Day 9 - Eval

Zero Shot accuracy - 72% (36/50)
Few shots accuracy - 76% (38/50)

Day 10 - JSON

Prefilling is deprecated in Claude 4 models. Basically not needed anymore, Claude understands the instructions to extract JSON only.

Day 11 -

The key insight is schema-prompt synchronization — the schema and the validator are derived from the same single source of truth.

The bug class it eliminates: schema drift
Without model_json_schema(), you'd write the schema in the prompt by hand:

system = "Return JSON with keys: sentiment (positive/negative/mixed), price (float), ..."
Now you have two independent definitions of the same structure:

The prompt's prose/schema description
The Pydantic model
They can drift apart silently. Common failure modes:

What drifts: You rename price_mentioned → price in the model but forget to update the prompt ----------> LLM returns price, Pydantic looks for price_mentioned, ValidationError every time

You add a required field to the model but not the prompt ------> LLM omits it, validation fails

You tighten a Literal constraint in the model ----------> LLM still returns old values, fails validation

Type changes (str → float) ---------> LLM returns a string, Pydantic rejects it

Why model_json_schema() closes this gap
In extract_typed.py:24:

schema = json.dumps(Review.model_json_schema(), indent=2)
The schema injected into the prompt is generated from the model at runtime. The Pydantic model is the only place you ever touch — the prompt description and the validator are both derived from it automatically. You physically cannot have them disagree.

The flow is:

Review (Pydantic model)
│
├──► model_json_schema() ──► prompt (tells LLM what to return)
│
└──► model_validate() ──► validator (checks what LLM returned)
Both arrows point from the same source. The schema in the prompt and the schema used for validation are identical by construction, not by discipline.

The remaining bugs (malformed JSON, LLM ignoring the schema entirely) still exist — but the whole class of "model and prompt got out of sync" bugs is structurally impossible.

Day 12 -> Validation Loop description

1- Generate output inside a loop with maximum tries (generally 3)
2- On try error block, catch a validation error
3- Write a corrective prompt for the model, citing the error caught, to rerun the loop
4- If the next tries (under max tries) generate a successful output, break the loop
5- Otherwise raise error and call for human intervention.

Claude correction ->

Strong pseudocode — you've got the core skeleton right. Five components, correct order, correctly identifies "raise + human intervention" as the terminal state. That's the exam-passing version.

Where it can get sharper for a whiteboard:

**1. Be explicit about state preservation between attempts.** Your step 3 says "write a corrective prompt citing the error" — true, but the canonical pattern doesn't _replace_ the prompt, it _appends_ to the conversation. The corrective prompt sits at the end of a growing message list that includes: the original request, Claude's failed output, your error message, and a fresh prefill. Showing that on a whiteboard is what separates "I know the pattern" from "I've built the pattern."

**2. Name what error types you catch.** Your "validation error" is one of two. The full pattern catches both `json.JSONDecodeError` (raw parse failure — Claude wrote prose instead of JSON) and `pydantic.ValidationError` (parsed but shape-wrong — sentiment is a list instead of a string). They're conceptually distinct and the exam may probe whether you know that.

**3. Distinguish retryable from non-retryable failures.** Your pseudocode treats every error the same. In production (and on the exam), the canonical pattern recognizes three buckets: (a) schema/parse errors → retry with correction, (b) transient API errors like 429 rate-limit or 529 overload → retry with exponential backoff (different pattern), (c) auth or model_not_found → don't retry, fail loudly. The exam loves a distractor that says "retry on every exception including auth failures."

**4. Step 4 is implicit, not a step.** Returning the validated object on success doesn't need its own line — it just happens. You can compress your 5 steps into 4.

**5. Tiny precision win:** "raise error" → "raise a custom exception type" (e.g. `ExtractionError`). The reason: callers up the stack need to distinguish "the retry loop gave up" from "some other error." Using the built-in `Exception` makes that hard.

Here's how I'd write the whiteboard version, keeping your structure:

```
def extract_with_retry(input, schema, max_retries=3):
    messages = [user(input), assistant_prefill("{")]
    last_error = None

    for attempt in range(1, max_retries + 1):
        response = call_claude(system+schema, messages)
        raw = "{" + response.text

        try:
            parsed = json.loads(raw)
            return Model.validate(parsed)        # success exits the loop
        except (JSONDecodeError, ValidationError) as e:
            last_error = e
            if attempt == max_retries:
                break

            # append the failed attempt + corrective turn + fresh prefill
            messages = [
                user(input),
                assistant(raw),                  # Claude's bad output
                user(f"That failed: {e}. Re-output corrected JSON."),
                assistant_prefill("{"),
            ]

    raise ExtractionError(f"failed after {max_retries} attempts: {last_error}")
```

Five things on this version that are exam-cited and worth memorizing:

- **The growing message list** — each retry, Claude sees the previous failure and the error message. That's what makes retry-with-correction different from retry-and-hope.
- **The bounded cap** — `max_retries=3` is the canonical default. Without a cap, a malformed prompt loops forever.
- **The prefill on every attempt** — even the corrective re-prompt ends with `{` to force JSON shape.
- **The custom exception** — terminal failure type is named.
- **The `last_error` capture** — when you finally raise, the message contains the _most recent_ failure, not the first one. Useful for debugging in production and for the exam scenario "the agent looped 3 times — what should the error message contain?"

One last thing — your step 5 "call for human intervention" is exactly right and worth keeping in your written version. The exam tests whether you know that the retry loop is _not_ the only failsafe; routing to human review on terminal failure is part of the pattern. Many candidates draw the retry loop and stop there. You didn't. Keep that.

Verdict: your pseudocode would pass on the exam. Add explicit error types and the growing message list, and you've got a whiteboard-ready version you can draw under pressure.

Day 13 - PROMPT CACHING

=== WITHOUT CACHE ===
Uncached input: 5,352
Cache reads: 0
Cache creates: 0
Elapsed: 14.44s

=== WITH CACHE ===
Uncached input: 15
Cache reads: 4,200
Cache creates: 1,137
Elapsed: 21.59s

Difference in time explanation ->
The short version: caching saves you on input processing, but input processing was never what was making your calls slow. Wall-clock latency in an LLM call is dominated by output generation, not input size — so trimming input does almost nothing to elapsed time, and the small overhead caching adds can make it net slower.
A few things worth unpacking.
First, notice your numbers reconcile: 4,200 cache reads + 1,137 cache creates + 15 uncached = 5,352, which is exactly the uncached total from the other run. So both runs pushed the same prompt content through the model. The caching didn't reduce how much the model had to "know" — it only changed how those input tokens were billed and processed. That's your first clue that the input difference is a red herring for latency.
Second, why input size barely matters for time: input tokens are processed in parallel in a single forward pass, which is fast. Output tokens are generated one at a time, sequentially — that's the slow part. A few thousand input tokens is a rounding error in latency terms. If the model happened to generate longer responses in the cached run (and with any nonzero temperature, output length varies call to call), that alone would explain the entire 7-second gap, completely independent of caching.
Third, caching isn't free on the write side. The first call in your cached run had to create the cache (your 1,137 cache-creation tokens), and writing to the cache carries its own overhead — it's slower and more expensive per token than a normal input token. You pay that penalty up front and only recoup it if the cached prefix is large and reused across many calls. With a prompt this small reused only a handful of times, you may never recoup it.
Fourth, and probably the biggest factor here: run-to-run variance. With a small workload and few calls, a 14s-vs-22s difference is well within normal noise from server load, queuing, and time-to-first-token jitter. If you reran both several times you'd likely see the gap shrink, vanish, or even flip.
So caching is doing its job — your uncached input dropped from 5,352 to 15, which is real cost savings on input. It's just that input cost and input latency are different things, and your prompt is too small for the input savings to show up in the clock.
Where caching actually pays off in latency: very large reused prefixes (think tens of thousands of tokens of context, long documents, big system prompts) hit on many subsequent calls, where re-reading that prefix from cache genuinely beats reprocessing it. To see the effect cleanly, scale the prompt way up, make many more repeated calls so the one-time write cost amortizes, and average elapsed time over several runs rather than trusting a single measurement. If you want, fix the output length (set a low, constant max_tokens or prompt for a one-word answer) so generation time stops masking the input effect you're trying to measure.

---

"Why is 'use response_format: json ' wrong on the Messages API, and what is the correct pattern?"

Good question — and the answer hinges on which Claude model you're targeting, because the API changed.

**The wrong pattern (outdated):**

```python
response = client.messages.create(
    model="claude-opus-4-6",
    max_tokens=1024,
    messages=[...],
    response_format="json"  # ❌ WRONG — this parameter doesn't exist
)
```

The `response_format` parameter you'd see on OpenAI's API doesn't exist on Anthropic's Messages API. That's the first mistake — you're reaching for a sibling API's syntax.

**The correct pattern (modern, Sonnet 4.6+):**

If you want _structured output_ on Claude Sonnet 4.6 or newer, use `client.messages.parse()`:

```python
from anthropic import Anthropic
from pydantic import BaseModel

class MyOutput(BaseModel):
    name: str
    age: int
    items: list[str]

client = Anthropic()
response = client.messages.parse(
    model="claude-sonnet-4-6",
    max_tokens=1024,
    messages=[
        {"role": "user", "content": "Extract: John is 30 and likes apples, oranges, and carrots."}
    ],
    response_schema=MyOutput
)

result = response.parsed_output
print(result.name)   # "John"
print(result.age)    # 30
print(result.items)  # ["apples", "oranges", "carrots"]
```

The key differences:

1. **Use `client.messages.parse()`** instead of `client.messages.create()`.
2. **Pass a Pydantic model as `response_schema`** — that's your contract for what shape you expect back.
3. **Access the structured result via `response.parsed_output`** — it's already deserialized into your Python class, not a raw JSON string.

**If you're stuck on an older model** (Claude 3 Sonnet, Opus 3, etc.) that doesn't support `parse()`:

You can't use structured outputs natively. Your workaround is to prompt for JSON in the system message and parse the raw text response yourself:

```python
response = client.messages.create(
    model="claude-3-5-sonnet-20241022",  # older model
    max_tokens=1024,
    system="Respond only with valid JSON, no markdown, no preamble.",
    messages=[
        {"role": "user", "content": "Extract: John is 30..."}
    ]
)

import json
result = json.loads(response.content[0].text)
```

**Why the change?** Anthropic moved from "prompt the model to spit JSON and parse it yourself" to native structured outputs with `parse()`, which is faster, cheaper (tokens-wise), and more reliable because the model's output is validated against your schema server-side before you even get it.

So: **If you're on Sonnet 4.6+, use `parse()`. If you're on an older model or need the old API, prompt for JSON and parse it yourself.** And never look for `response_format` on the Anthropic API — that's OpenAI syntax.
