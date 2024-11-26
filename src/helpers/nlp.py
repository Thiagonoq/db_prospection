import spacy

spacy_nlp = spacy.load("pt_core_news_sm")


def make_ngrams(word, min_size: int = 2, prefix_only: bool = False):
    length = len(word)
    size_range = range(min_size, max(length, min_size) + 1)

    if prefix_only:
        return [word[0:size] for size in size_range]

    return list(
        set(
            word[i : i + size]
            for size in size_range
            for i in range(0, max(0, length - size) + 1)
        )
    )


def create_ngrams(name_varietys):
    new_varieties_ngrams = []
    new_varieties_pre_ngrams = []

    for variety in name_varietys:
        new_varieties_ngrams.append(" ".join(make_ngrams(process_text(variety))))

    for variety in name_varietys:
        new_varieties_pre_ngrams.append(
            " ".join(make_ngrams(process_text(variety), prefix_only=True))
        )

    return new_varieties_ngrams, new_varieties_pre_ngrams


def process_text(text):
    doc = spacy_nlp(text)

    filtered_words = [token.text for token in doc if not token.is_stop]

    return " ".join(filtered_words)
