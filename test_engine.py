import json
import sys
sys.path.append('backend')
from chatbot_engine import get_engine

engine = get_engine()
faqs = json.load(open('faq_replica.json', encoding='utf-8'))
errors = []

for faq in faqs:
    for q in faq.get('questions', []):
        ans = engine.get_best_answer(q)
        if ans != faq['answer']:
            # Find the intent that was actually predicted
            predicted_intent = "FALLBACK"
            for i, a in enumerate(engine.answers):
                if ans == a:
                    predicted_intent = engine.intents[i]
                    break
            errors.append((q, faq.get('intent', 'unknown'), predicted_intent))

with open('test_errors.txt', 'w', encoding='utf-8') as f:
    f.write(f"Total errors: {len(errors)}\n")
    for q, exp, pred in errors:
        f.write(f"'{q}' -> Expected: {exp}, Predicted: {pred}\n")
