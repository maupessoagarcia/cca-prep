import json
import pandas as pd
from pathlib import Path
from classify import zero_shot, few_shot

def run_eval(name: str, fn, df: pd.DataFrame = None):
    gold = [json.loads(line) for line in Path("labs/week02/gold.jsonl").read_text().splitlines() if line.strip()]
    correct = 0
    misses = []
    preds = []
    for item in gold:
        pred = fn(item["email"])
        preds.append(pred)
        if pred == item["label"]:
            correct += 1
        else:
            misses.append((item["email"][:60] + "...", item["label"], pred))
    acc = correct / len(gold) * 100
    print(f"{name}: {correct}/{len(gold)} = {acc:.1f}%")
    print("Misclassifications:")
    for email, gold_label, pred in misses:
        print(f" [{gold_label} -> {pred}] {email}")

    if df is None:
        df = pd.DataFrame({
            "Email": [item["email"] for item in gold],
            "Real Classification": [item["label"] for item in gold],
            "Zero Shot Result": preds,
            "Few Shot Result": [None] * len(gold),
        })
    else:
        df["Few Shot Result"] = preds
    return df

df = run_eval("zero_shot", zero_shot)
df = run_eval("few_shot", few_shot, df)
print(df)
df.to_csv("labs/week02/eval_results.csv", index=False)
