import hashlib
import re
import unicodedata


_HTML_TAG_RE = re.compile(r"<[^>]+>")
_URL_RE = re.compile(r"https?://\S+|www\.\S+")
_MULTI_SPACE_RE = re.compile(r"\s+")


def normalize_text(text: str | None) -> str | None:
    if text is None:
        return None
    text = unicodedata.normalize("NFC", text)
    text = _HTML_TAG_RE.sub(" ", text)
    text = _URL_RE.sub(" ", text)
    text = _MULTI_SPACE_RE.sub(" ", text).strip()
    return text or None


def content_hash(text: str | None) -> str | None:
    if not text:
        return None
    normalized = normalize_text(text.lower()) or ""
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()
