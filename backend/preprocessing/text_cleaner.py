import re
import unicodedata
from typing import Tuple, List

URL_PATTERN = re.compile(r"http[s]?://\S+")
MENTION_PATTERN = re.compile(r"@\w+")
HASHTAG_PATTERN = re.compile(r"#\w+")
RT_PATTERN = re.compile(r"\bRT\b")
MULTI_SPACE_PATTERN = re.compile(r"\s+")
EMOJI_PATTERN = re.compile(
    "["
    "\U0001F300-\U0001F5FF"
    "\U0001F600-\U0001F64F"
    "\U0001F680-\U0001F6FF"
    "\U0001F700-\U0001F77F"
    "\U0001F780-\U0001F7FF"
    "\U0001F800-\U0001F8FF"
    "\U0001F900-\U0001F9FF"
    "\U0001FA00-\U0001FAFF"
    "]+",
    flags=re.UNICODE
)
PUNCTUATION_REPEAT_PATTERN = re.compile(r"([!?\.]){2,}")


def normalize_unicode(text: str) -> str:
    """Normalize unicode characters (NFKC)."""
    return unicodedata.normalize("NFKC", text)


def extract_hashtags(text: str) -> List[str]:
    """ Extract hashtags from raw text and store hashtag words without # """
    hashtags = HASHTAG_PATTERN.findall(text)
    return [h[1:].lower() for h in hashtags]


def extract_emojis(text: str) -> List[str]: 
    """ Extract emojis from raw text and store separately"""
    emojis = EMOJI_PATTERN.findall(text)
    return [e for e in emojis]


def clean_text(text: str) -> str:
    """Text Cleaning Pipeline"""
    if not text or not text.strip():
        return ""

    # Unicode normalization
    text = normalize_unicode(text)
    # Remove URLs
    text = URL_PATTERN.sub("", text)
    # Remove emojis
    text = EMOJI_PATTERN.sub("", text)
    # Remove mentions
    text = MENTION_PATTERN.sub("", text)
    # Remove RT markers
    text = RT_PATTERN.sub("", text)
    # Strip hashtag symbols, keeping words
    text = text.replace("#", "")
    # Normalize whitespace
    text = MULTI_SPACE_PATTERN.sub(" ", text)
    # Remove excessive repeated punctuation
    text = PUNCTUATION_REPEAT_PATTERN.sub(r"\1", text)

    return text


def process_raw_text(text_raw: str) -> Tuple[str, List[str], List[str]]:
    """Main raw text processing pipeline"""
    hashtags = extract_hashtags(text_raw)
    emojis = extract_emojis(text_raw) 
    text_clean = clean_text(text_raw)
    return text_clean, hashtags, emojis
