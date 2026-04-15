import json
import logging
import re
import string
from pathlib import Path
from typing import Optional

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from config import Config

logger = logging.getLogger(__name__)

FALLBACK_RESPONSE = (
    "I'm sorry, I couldn't find a relevant answer to your question. "
    "Could you please rephrase it or ask about courses, certificates, "
    "payments, account, or support?"
)

SYNONYM_MAP = {
    "cert": "certificate", "certs": "certificate",
    "certification": "certificate", "certifications": "certificate",
    "certified": "certificate",
    "finish": "complete", "finished": "complete", "completing": "complete",
    "done": "complete", "completed": "complete",
    "once i finish": "after completing",
    "after finishing": "after completing",
    "when i finish": "after completing",
    "after i complete": "after completing",
    "join": "enroll", "joining": "enroll", "enrollment": "enroll",
    "enrolled": "enroll", "register": "enroll", "registration": "enroll",
    "signup": "sign up",
    "login": "log in", "signin": "sign in",
    "cant login": "cannot log in", "cant sign in": "cannot log in",
    "unable to login": "cannot log in",
    "pw": "password", "pwd": "password",
    "forgot password": "reset password",
    "forgot my password": "reset password",
    "lost password": "reset password",
    "recover password": "reset password",
    "pay": "payment", "paid": "payment", "paying": "payment",
    "bill": "invoice", "billing": "invoice", "receipt": "invoice",
    "charge": "payment", "charged": "payment",
    "money deducted": "amount deducted",
    "money cut": "amount deducted",
    "get": "download", "obtain": "download", "receive": "download",
    "earn": "earn",
    "helpdesk": "support", "help desk": "support",
    "reach": "contact",
    "app": "mobile app", "mobile": "mobile app", "phone": "mobile app",
    "videos": "video", "lecture": "video", "lectures": "video",
    "quiz": "assignment", "quizzes": "assignment",
    "test": "assignment", "exam": "assignment",
    "submission": "submit", "submitting": "submit",
    "forum": "community", "discussion": "community",
    "badges": "badge", "achievement": "badge",
    "plan": "subscription", "expired": "expired", "inactive": "inactive",
    "photo": "profile", "pic": "profile", "picture": "profile",
    "locked": "locked", "delete": "delete", "remove": "delete",
    "deactivate": "delete",
    "linkedin": "linkedin",
    "refund": "refund", "money back": "refund",
    "progress": "progress", "resume": "resume",
}

STOP_WORDS = {
    "i", "my", "the", "a", "an", "is", "it", "do", "how", "can",
    "will", "what", "where", "when", "why", "to", "in", "on", "of",
    "for", "and", "or", "not", "be", "are", "was", "were", "have",
    "has", "had", "this", "that", "with", "from", "at", "me", "we",
    "you", "your", "our", "their", "if", "so", "but", "just", "get",
    "got", "did", "does", "am", "im", "ive", "id", "its", "please",
    "want", "need", "help", "tell", "show", "give", "let", "make",
    "about", "after", "before", "during", "while", "then", "than",
    "also", "still", "already", "again", "back", "up", "down",
}


class ChatbotEngine:
    """
    NLP chatbot engine that reads faq_replica.json (structured with intent +
    questions array + answer) and matches user input using TF-IDF cosine
    similarity combined with keyword overlap scoring.
    """

    def __init__(self, faq_path: Optional[str] = None, threshold: Optional[float] = None):
        self.faq_path = Path(faq_path or Config.FAQ_PATH)
        self.threshold = threshold if threshold is not None else Config.SIMILARITY_THRESHOLD

        self.intents: list[str] = []
        self.combined_questions: list[str] = []
        self.answers: list[str] = []

        self.vectorizer = TfidfVectorizer(
            stop_words="english",
            ngram_range=(1, 3),
            analyzer="word",
            min_df=1,
            sublinear_tf=True,
        )
        self._load_and_fit()

    def _load_and_fit(self) -> None:
        if not self.faq_path.exists():
            raise FileNotFoundError(f"FAQ file not found: {self.faq_path}")

        with open(self.faq_path, "r", encoding="utf-8") as f:
            faqs: list[dict] = json.load(f)

        if not faqs:
            raise ValueError("FAQ file is empty.")

        for item in faqs:
            if isinstance(item.get("questions"), list):
                combined = " ".join(item["questions"])
            else:
                combined = item.get("question", "")

            self.intents.append(item.get("intent", "unknown"))
            self.combined_questions.append(combined)
            self.answers.append(item["answer"])

        self.tfidf_matrix = self.vectorizer.fit_transform(self.combined_questions)
        logger.info(
            "ChatbotEngine loaded %d FAQ entries from %s",
            len(faqs), self.faq_path.name
        )

    @staticmethod
    def _clean(text: str) -> str:
        text = text.lower().strip()
        text = text.translate(str.maketrans("", "", string.punctuation))
        text = re.sub(r"\s+", " ", text)
        return text

    def _expand(self, text: str) -> str:
        phrases = sorted(
            [(k, v) for k, v in SYNONYM_MAP.items() if " " in k],
            key=lambda x: -len(x[0])
        )
        for phrase, replacement in phrases:
            text = text.replace(phrase, replacement)
        words = text.split()
        return " ".join(SYNONYM_MAP.get(w, w) for w in words)

    def _keyword_overlap(self, query_words: set, faq_text: str) -> float:
        faq_words = set(self._clean(faq_text).split())
        meaningful = query_words - STOP_WORDS
        if not meaningful:
            return 0.0
        return len(meaningful & faq_words) / len(meaningful)

    def get_best_answer(self, user_input: str) -> str:
        cleaned = self._clean(user_input)
        if not cleaned:
            return FALLBACK_RESPONSE

        expanded = self._expand(cleaned)
        query_words = set(expanded.split())

        user_vec = self.vectorizer.transform([expanded])
        tfidf_scores = cosine_similarity(user_vec, self.tfidf_matrix).flatten()

        overlap_scores = [
            self._keyword_overlap(query_words, q)
            for q in self.combined_questions
        ]

        combined = [
            0.7 * tfidf_scores[i] + 0.3 * overlap_scores[i]
            for i in range(len(self.combined_questions))
        ]

        best_idx = int(max(range(len(combined)), key=lambda i: combined[i]))
        best_score = combined[best_idx]

        logger.debug(
            "Input: '%s' | Intent: '%s' | Score: %.4f",
            user_input, self.intents[best_idx], best_score
        )

        if best_score >= self.threshold:
            return self.answers[best_idx]

        return FALLBACK_RESPONSE


_engine: Optional[ChatbotEngine] = None


def get_engine() -> ChatbotEngine:
    global _engine
    if _engine is None:
        _engine = ChatbotEngine()
    return _engine
