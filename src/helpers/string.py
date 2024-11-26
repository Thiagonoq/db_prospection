import re
import unicodedata


def normalize(value: str, remove_spaces: bool = True):
    value = (
        unicodedata.normalize("NFKD", value)
        .encode("ASCII", "ignore")
        .decode("ASCII")
        .strip()
        .lower()
    )

    if remove_spaces:
        return re.sub("\W+", "", value)

    return value


def slugify(value, allow_unicode=False):
    value = str(value)
    if allow_unicode:
        value = unicodedata.normalize("NFKC", value)
    else:
        value = (
            unicodedata.normalize("NFKD", value)
            .encode("ascii", "ignore")
            .decode("ascii")
        )
    value = re.sub(r"[^\w\s-]", "", value.lower())
    return re.sub(r"[-\s]+", "-", value).strip("-_")


def snake_case(string: str):
    return "".join(["_" + i.lower() if i.isupper() else i for i in string]).lstrip("_")
