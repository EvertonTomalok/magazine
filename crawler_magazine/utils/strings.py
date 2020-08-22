import unicodedata


def normalize_text(text: str, upper=True):
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode("utf-8")

    return text.upper() if upper else text
