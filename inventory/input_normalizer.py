import unicodedata


def input_normalize(text):
    result = ""
    if text is None:
        return text
    else:
        for char in text:
            if char in ['(', ')', '（', '）']:  # Explicitly check for brackets
                result += char
            else:
                result += unicodedata.normalize('NFKC', char)
        return result
