# backend/translation_service.py
"""
Localization & Translation Service
Provides localized UI strings, labels, and notices in English, Hindi, and Telugu.
"""
import os
import json
import logging

logger = logging.getLogger(__name__)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TRANSLATIONS_PATH = os.path.join(BASE_DIR, "data", "translations.json")

SUPPORTED_LANGUAGES = ["en", "hi", "te"]

class TranslationService:
    def __init__(self):
        self.translations = self._load_translations()

    def _load_translations(self) -> dict:
        if os.path.exists(TRANSLATIONS_PATH):
            try:
                with open(TRANSLATIONS_PATH, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Failed to load translations from {TRANSLATIONS_PATH}: {e}")
        return {}

    def get_translations_for_lang(self, lang="en") -> dict:
        lang = lang if lang in SUPPORTED_LANGUAGES else "en"
        return self.translations.get(lang, self.translations.get("en", {}))

    def get_text(self, key: str, lang="en", default=None) -> str:
        lang = lang if lang in SUPPORTED_LANGUAGES else "en"
        lang_dict = self.translations.get(lang, {})
        val = lang_dict.get(key)
        if val is None:
            # Fallback to English
            val = self.translations.get("en", {}).get(key, default or key)
        return val

translation_service = TranslationService()

