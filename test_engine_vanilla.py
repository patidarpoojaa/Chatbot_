import json
import sys
sys.path.append('backend')
from chatbot_engine import get_engine

engine = get_engine()
faqs = json.load(open('faq_replica.json', encoding='utf-8'))
errors = []

def get_best_answer_vanilla(user_input: str) -> str:
    cleaned = engine._clean(user_input)
    if not cleaned:
        return "fallback"
        
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

    return "fallback"

for faq in faqs:
    for q in faq.get('questions', []):
        ans = get_best_answer_vanilla(q)
        if ans != faq['answer']:
            predicted_intent = "FALLBACK"
            for i, a in enumerate(engine.answers):
                if ans == a:
                    predicted_intent = engine.intents[i]
                    break
            errors.append((q, faq.get('intent', 'unknown'), predicted_intent))

print(f"Total vanilla errors: {len(errors)}")
for e in errors[:10]:
    print(e)
