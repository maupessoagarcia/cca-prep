from anthropic import Anthropic
from dotenv import load_dotenv


load_dotenv()
client = Anthropic()

# Pricing as of May 2026 — verify at https://docs.claude.com/en/about-claude/pricing
PRICE_PER_MTOK = {
"claude-sonnet-4-6": {"input": 3.0, "output": 15.0},
"claude-opus-4-7": {"input": 5.0, "output": 25.0},
"claude-haiku-4-5": {"input": 1.0, "output": 5.0},
}

def estimate_batch(prompts:list[str], model:str,expected_output_tokens:int=200):
    rates=PRICE_PER_MTOK[model]
    total_input=0
    for p in prompts:
        # count_tokens gives you the exact token count Anthropic will bill for
        result = client.messages.count_tokens(
            model=model,
            messages=[{"role":"user","content":p}],
        )
        total_input += result.input_tokens
    total_output_est = expected_output_tokens *len(prompts)

    input_cost = total_input/1_000_000*rates["input"]
    output_cost = total_output_est / 1_000_000*rates["output"]
    total = input_cost + output_cost

    print(f"Model: {model}")
    print(f" Requests: {len(prompts)}")
    print(f" Input tokens: {total_input:,}")
    print(f" Est. output toks: {total_output_est:,}")
    print(f" Estimated cost: ${total:.4f} (input ${input_cost:.4f} + output ${output_cost:.4f})") 


#Try it
sample_prompts = [
"Summarize the French Revolution in one paragraph.",
"Explain why the sky is blue in terms a child would understand.",
"Write a haiku about debugging."] * 10 # pretend you have 30 documents to process

estimate_batch(sample_prompts, "claude-sonnet-4-6", expected_output_tokens=150)
estimate_batch(sample_prompts, "claude-opus-4-7", expected_output_tokens=150)
estimate_batch(sample_prompts, "claude-haiku-4-5", expected_output_tokens=150)