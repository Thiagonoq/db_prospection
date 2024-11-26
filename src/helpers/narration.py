import re

import requests
from num2words import num2words


def cellphone(phone: str):
    phone = re.sub(r"[^\d]", "", phone).strip()

    phone_match = re.match(
        r"(\d{2})?(\d{2})(\d{1})?(\d{2})(\d{2})(\d{2})(\d{2})", phone, re.I | re.M
    )

    if not phone_match:
        return phone

    return ", ".join(
        ("zero, " if number[0] == "0" else "") + num2words(number, lang="pt_BR")
        for number in phone_match.groups()
        if number
    )


def numbers_to_text(text: str):
    new_text = ""

    for char in text:
        if char.isdigit():
            new_text += num2words(char, lang="pt_BR") + " "
        else:
            new_text += char

    return re.sub(r"\s+", " ", new_text)


def numbers_to_text_grouped(text: str):
    def process(group: re.Match):
        return num2words(group.group(), lang="pt_BR")

    return re.sub(r"\d+", lambda number: process(number), text)


def get_syllables(phrase: str):
    new_word = ""
    new_syllables = ""

    try:
        for word in phrase.split():
            response = requests.get(
                f"https://www.separaremsilabas.com/index.php?lang=index.php&p={word}&button=Separa%C3%A7%C3%A3o+das+s%C3%ADlabas"
            )

            map_vowel = {"a": "â", "e": "ê", "i": "î", "o": "ô", "u": "û"}

            def process_tonic(tonic):
                vowels = re.findall(r"[aeiou]", tonic, re.I | re.M)

                if not vowels:
                    return tonic

                replace_vowel = (
                    vowels[-1] if vowels[0] == "u" and len(vowels) > 1 else vowels[0]
                )

                return tonic.replace(replace_vowel, map_vowel[replace_vowel])

            regex = r"([\w-]+)?<strong>(\w+)</strong>([\w-]+)?"

            if find := re.findall(regex, response.text, re.I | re.M):
                syllables = list(find[0])

                if not syllables[0] and not syllables[2] and not syllables[1].isascii():
                    new_syllables += syllables[1] + " "
                    new_word += syllables[1] + " "
                    continue

                tonic = process_tonic(syllables[1])

                syllables[1] = tonic
                syllables = [y for x in syllables for y in x.split("-") if y]

                new_syllables += "-".join(syllables) + " "
                new_word += "".join(syllables) + " "
    except:
        return {"syllables": None, "word": phrase}

    return {"syllables": new_syllables, "word": new_word}


def replace_using_words(text: str, words_map: dict = {}):
    for regex, value in words_map.items():
        text = re.sub(regex, value, text, flags=re.IGNORECASE)

    return text


def remove_articles(text):
    return re.sub(
        r"\b(a|o|as|os|um|uma|uns|umas|ao|aos|da|das|do|dos|na|nas|no|nos|pela|pelas|pelo|pelos)\b",
        "",
        text,
        flags=re.IGNORECASE,
    )


def text_to_narration(text: str, words_map: dict = {}):
    narration_text = []

    for word in text.split():
        lower_word = word.lower()
        word = replace_using_words(lower_word, words_map)

        if word == lower_word and not word.isnumeric():
            word = get_syllables(word)["word"]

        narration_text.append(numbers_to_text_grouped(word))

    return " ".join(narration_text)


def number_to_price(price):
    return num2words(
        float(str(re.sub(r"[^0-9\.,]", "", price)).replace(",", ".")),
        to="currency",
        lang="pt_BR",
    ).replace("zero reais e ", "")
