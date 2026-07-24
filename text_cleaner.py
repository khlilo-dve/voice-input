"""Rule-based ASR text cleaner — no LLM, no hallucinations."""
import re

# ── Filler phrases to remove ──────────────────────────
FILLER_PHRASES = [
    "就是说", "这个那个", "然后然后", "那个那个",
    "对吧", "你懂吧", "你懂吗", "你知道吗",
    "对不对",
]
# NOTE: "是不是" intentionally kept — it's a legitimate question marker

# Single-char fillers (removed unconditionally)
FILLER_CHARS = "嗯啊呃哦咳欸诶呢呀嘛哈哪哇"

# ── Patterns ──────────────────────────────────────────
# Space between two Chinese characters
ZH_SPACE = re.compile(r"([一-鿿])\s+([一-鿿])")

# Repeated character 3+ times
REPEAT = re.compile(r"(.)\1{2,}")

# English period between Chinese → Chinese period (any Chinese char before/after)
EN_DOT = re.compile(r"([一-鿿])\.([一-鿿\s]|$)")

# English comma between Chinese chars
EN_COMMA_ZH = re.compile(r"([一-鿿]),([一-鿿])")

# Multiple newlines
MULTI_NL = re.compile(r"\n{3,}")

# Punctuation repeats
PUNCT_DUP = re.compile(r"([。，！？、])\1+")

# "那个" as filler at start of text
LEADING_NAGE = re.compile(r"^那个")
# "就是那个" → "就是"
JIUSHI_NAGE = re.compile(r"就是那个")


def clean_text(raw: str) -> str:
    """Clean ASR — deterministic, no LLM, no hallucinations."""
    text = raw.strip()

    # 1. Multi-char filler phrases
    for phrase in FILLER_PHRASES:
        text = text.replace(phrase, "")

    # 2. Single-char fillers
    for ch in FILLER_CHARS:
        text = text.replace(ch, "")

    # 3. "那个" as filler
    text = LEADING_NAGE.sub("", text)      # "那个今天" → "今天"
    text = JIUSHI_NAGE.sub("就是", text)   # "就是那个voice" → "就是voice"

    # 4. Spaces between Chinese characters
    text = ZH_SPACE.sub(r"\1\2", text)

    # 5. Repeated chars
    text = REPEAT.sub(r"\1\1", text)

    # 6. English → Chinese punctuation
    text = EN_DOT.sub(r"\1。\2", text)
    text = EN_COMMA_ZH.sub(r"\1，\2", text)

    # 7. Newlines
    text = MULTI_NL.sub("\n\n", text)

    # 8. Deduplicate punctuation
    text = PUNCT_DUP.sub(r"\1", text)

    return text.strip()
