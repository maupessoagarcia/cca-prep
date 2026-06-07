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
