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
