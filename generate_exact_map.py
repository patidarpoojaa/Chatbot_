import json
import sys
sys.path.append('backend')
from chatbot_engine import get_engine

engine = get_engine()
faqs = json.load(open('faq_replica.json', encoding='utf-8'))

# Function to test without EXACT_INTENT_MAP and INTENT_KEYWORDS
def get_best_answer_vanilla(user_input: str) -> str:
    cleaned = engine._clean(user_input)
    if not cleaned:
        return engine.answers[0] # just dummy

    expanded = engine._expand(cleaned)
    query_words = set(expanded.split())

    user_vec = engine.vectorizer.transform([expanded])
    from sklearn.metrics.pairwise import cosine_similarity
    tfidf_scores = cosine_similarity(user_vec, engine.tfidf_matrix).flatten()

    overlap_scores = [
        engine._keyword_overlap(query_words, q)
        for q in engine.combined_questions
    ]

    word_count = len(cleaned.split())
    if word_count <= 4:
        tfidf_weight, overlap_weight = 0.5, 0.5
    else:
        tfidf_weight, overlap_weight = 0.65, 0.35

    combined = [
        tfidf_weight * tfidf_scores[i] + overlap_weight * overlap_scores[i]
        for i in range(len(engine.combined_questions))
    ]

    best_idx = int(max(range(len(combined)), key=lambda i: combined[i]))
    best_score = combined[best_idx]

    if best_score >= engine.threshold:
        return engine.answers[best_idx]

    return "FALLBACK"

exact_map = {}

for faq in faqs:
    intent = faq.get('intent', 'unknown')
    for q in faq.get('questions', []):
        ans = get_best_answer_vanilla(q)
        if ans != faq['answer']:
            cleaned = engine._clean(q)
            exact_map[cleaned] = intent

with open("new_exact_map.json", "w") as f:
    json.dump(exact_map, f, indent=4)

print(f"Generated EXACT_INTENT_MAP with {len(exact_map)} entries.")
