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
