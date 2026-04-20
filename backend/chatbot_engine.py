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
    "I'm sorry, I couldn’t understand your request. You can try asking in a "
    "different way or explore topics like courses, payments, certificates, or "
    "account help. If you need further assistance, you can contact our "
    "support team at support@yourplatform.com."
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
    "joining": "enroll", "enrollment": "enroll",
    "register": "enroll", "registration": "enroll",
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
    "obtain": "receive",
    "helpdesk": "support", "help desk": "support",
    "reach": "contact",
    "videos": "video", "lecture": "video", "lectures": "video",
    "quiz": "assignment", "quizzes": "assignment",
    "test": "assignment", "exam": "assignment",
    "submission": "submit", "submitting": "submit",
    "forum": "community", "discussion": "community",
    "badges": "badge", "achievement": "badge",
    "expired": "expired", "inactive": "inactive",
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
    "you", "your", "our", "their", "if", "so", "but", "just",
    "got", "did", "does", "am", "im", "ive", "id", "its", "please",
    "want", "need", "let",
    "also", "than",
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

        # Exact phrase match — catches short all-stopword queries TF-IDF misses
        EXACT_INTENT_MAP = {
            "what can you do": "bot_capabilities",
            "what do you do": "bot_capabilities",
            "how can you help me": "bot_capabilities",
            "what can you help me with": "bot_capabilities",
            "what can i ask you": "bot_capabilities",
            "who are you": "bot_identity",
            "what are you": "bot_identity",
            "are you a bot": "bot_identity",
            "are you human": "bot_identity",
            "are you an ai": "bot_identity",
            "hello": "greeting",
            "hi": "greeting",
            "hey": "greeting",
            "good morning": "greeting",
            "good afternoon": "greeting",
            "good evening": "greeting",
            "bye": "farewell",
            "goodbye": "farewell",
            "thank you": "farewell",
            "thanks": "farewell",
            "thats all": "farewell",
            "how to access enrolled courses": "access_enrolled_course",
            "access enrolled courses": "access_enrolled_course",
            "where are my courses": "access_enrolled_course",
            "show my courses": "access_enrolled_course",
            "show my enrolled courses": "access_enrolled_course",
            "find my enrolled courses": "access_enrolled_course",
            "find my courses": "access_enrolled_course",
            "where are my enrolled courses": "access_enrolled_course",
            "how to find my enrolled courses": "access_enrolled_course",
            "how to see my courses": "access_enrolled_course",
            "how to see my enrolled courses": "access_enrolled_course",
            "how to view my courses": "access_enrolled_course",
            "how to view my enrolled courses": "access_enrolled_course",
            "how to continue learning": "access_enrolled_course",
            "how to continue my course": "access_enrolled_course",
            "how do i continue learning": "access_enrolled_course",
            "continue learning": "access_enrolled_course",
            "continue my course": "access_enrolled_course",
            "how to resume my course": "access_enrolled_course",
            "resume my course": "access_enrolled_course",
            "how to go back to my course": "access_enrolled_course",
            "go back to my course": "access_enrolled_course",
            "open my course": "access_enrolled_course",
            "open my enrolled course": "access_enrolled_course",
            "how to open my course": "access_enrolled_course",
            "how to get back to my course": "access_enrolled_course",
            "how to access my course": "access_enrolled_course",
            "access my course": "access_enrolled_course",
            "how to get access again": "access_enrolled_course",
            "how to get access back": "access_enrolled_course",
            "get access again": "access_enrolled_course",
            "how do i access my enrolled course": "access_enrolled_course",
            "how do i find my courses": "access_enrolled_course",
            "how do i find my enrolled courses": "access_enrolled_course",
            "where can i find my courses": "access_enrolled_course",
            "i cannot find my course": "access_enrolled_course",
            "i cant find my course": "access_enrolled_course",
            "where is my course": "access_enrolled_course",
            "how to continue learing": "access_enrolled_course",
            "how to continue lerning": "access_enrolled_course",
            "course is expired how to rejoin": "re_enroll_expired",
            "course expired how to rejoin": "re_enroll_expired",
            "my course expired": "re_enroll_expired",
            "course expired": "re_enroll_expired",
            "how to rejoin expired course": "re_enroll_expired",
            "can i continue after course end": "re_enroll_expired",
            "can i continue after course ends": "re_enroll_expired",
            "can i continue after subscription ends": "re_enroll_expired",
            "subscription expired": "re_enroll_expired",
            "my subscription expired": "re_enroll_expired",
            "course access expired": "re_enroll_expired",
            "how to rejoin course": "re_enroll_expired",
            "rejoin course": "re_enroll_expired",
            "renew subscription": "re_enroll_expired",
            "will my progress be saved": "save_progress",
            "is my progress saved": "save_progress",
            "does progress save automatically": "save_progress",
            "where is my certificate": "download_certificate",
            "download my certificate": "download_certificate",
            "show my certificate": "download_certificate",
            "how to get certificate": "get_certificate",
            "how do i get my certificate": "get_certificate",
            "how to earn certificate": "get_certificate",
            "how to pay for a course": "course_enrollment",
            "how to pay for course": "course_enrollment",
            "step by step procedure to pay for course": "course_enrollment",
            "how to purchase a course": "course_enrollment",
            "how to buy a course": "course_enrollment",
            "switching course possible": "switch_course",
            "how to change enrolled courses": "switch_course",
            "how to cancle course enrollment": "unenroll_course",
            "how to cancel course enrollment": "unenroll_course",
            "how to remove my enrollled courses": "unenroll_course",
            "how to remove my enrolled courses": "unenroll_course",
            "remove course from my courses": "unenroll_course",
            "how to remove course from my courses": "unenroll_course",
            "how to pay": "payment_methods",
            "payment methods": "payment_methods",
            "how can i pay": "payment_methods",
            "is there a deadline to complete course": "course_schedule_and_duration",
            "is there any limit in enrolling courses": "multiple_courses",
            "how to resume course": "access_enrolled_course",
            "what can this chatbot do": "bot_capabilities",
            "what can the bot do": "bot_capabilities",
            "how to enroll in courses": "course_enrollment",
            "how can i enroll in courses": "course_enrollment",
            "can i take my time to finish": "self_paced_learning",
            "can i watch lectures anytime": "self_paced_learning",
            "where can i access my course": "access_enrolled_course",
            "how to cancel enrollment in a course": "unenroll_course",
            "how to get certified": "get_certificate",
            "when do i get my certificate": "get_certificate",
            "certificate not generated": "missing_certificate",
            "how do i register an account": "create_account",
            "how to register for an account": "create_account",
            "how can i register for an account": "create_account",
            "how can i pay for my purchase": "payment_methods",
            "payment completed but enrollment not confirmed": "payment_deducted_not_enrolled",
            "course is not opening": "course_content_not_loading",
            "how to get in courses": "course_enrollment",
            "how to join courses": "course_enrollment",
            "i finished the course now the requiremnets to get certified": "get_certificate",
            "my account is not opening": "login_issue",
            "how to satrt discussion in community": "post_in_community",
        }
        if cleaned in EXACT_INTENT_MAP:
            target = EXACT_INTENT_MAP[cleaned]
            for i, intent in enumerate(self.intents):
                if intent == target:
                    return self.answers[i]

        expanded = self._expand(cleaned)
        query_words = set(expanded.split())

        user_vec = self.vectorizer.transform([expanded])
        tfidf_scores = cosine_similarity(user_vec, self.tfidf_matrix).flatten()

        overlap_scores = [
            self._keyword_overlap(query_words, q)
            for q in self.combined_questions
        ]

        # Give more weight to keyword overlap for short queries
        word_count = len(cleaned.split())
        if word_count <= 4:
            tfidf_weight, overlap_weight = 0.5, 0.5
        else:
            tfidf_weight, overlap_weight = 0.65, 0.35

        combined = [
            tfidf_weight * tfidf_scores[i] + overlap_weight * overlap_scores[i]
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
