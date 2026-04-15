import json
import string

# Load FAQ data
with open("faq.json", "r") as f:
    faqs = json.load(f)

# Text preprocessing function
def preprocess(text):
    text = text.lower()
    text = text.translate(str.maketrans('', '', string.punctuation))
    return text.split()

# Similarity function
def similarity(user_input, faq_question):
    user_words = set(preprocess(user_input))
    faq_words = set(preprocess(faq_question))
    
    return len(user_words & faq_words) / len(user_words | faq_words)

# Find best answer
def get_best_answer(user_input):
    best_score = 0
    best_answer = "Sorry, I don't understand your question."
    
    for faq in faqs:
        score = similarity(user_input, faq["question"])
        if score > best_score:
            best_score = score
            best_answer = faq["answer"]
    
    return best_answer if best_score > 0.2 else "Please rephrase your question."

# Chat loop
print("FAQ Chatbot (type 'exit' to quit)")
while True:
    user_input = input("You: ")
    
    if user_input.lower() == "exit":
        break
    
    response = get_best_answer(user_input)
    print("Bot:", response)

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity