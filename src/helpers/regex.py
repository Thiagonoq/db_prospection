import re

flags = re.MULTILINE | re.IGNORECASE | re.DOTALL

json_regex = re.compile(r"{.*}", flags)
json_replace_regex = re.compile(r"(```)?(json)?\n?{.*}\n?(```)?", flags)
questions_actions_regex = re.compile(
    r" ?-? ?\(?(exempl(o|e)?: )?#((text|int|float|list|search|image(m)?|date|enum|bool(ean)?))?(_.+\)?)?(\)?)(:.+)\)\ ?",
    re.MULTILINE | re.IGNORECASE,
)
url_replace_regex = re.compile(
    ""
    r"(^-? ?(((link da ?)imagem?)|((search ?)? ?url(.+)?)?):? ?)?http(s)?:\/\/((25[0-5]|(2[0-4]|1\d|[1-9]|)\d)\.?\b){4}\/card-generator\/.+\.(png|jpeg|jpg|webp)",
    flags,
)
file_replace_regex = re.compile(r"^([^\n]+)\/?([^\/\n]+).(png|jpe?g)", flags)
questions_type_regex = re.compile(r"^(?!^exemplo:).*?: ", re.MULTILINE | re.IGNORECASE)
array_regex = re.compile(r'\[ ?(".+",?)* ?\]', flags)
hex_color_regex = re.compile(r"#[\w\d]{6}", flags)
address_regex = re.compile(r"( - bairro - cidade\/uf)|( - cidade\/uf)", flags)
product_inquiry_regex = re.compile(r"product_inquiry:(\d+)")
emoji_pattern = re.compile(
    "["
    "\U0001F600-\U0001F64F"  # emoticons
    "\U0001F300-\U0001F5FF"  # symbols & pictographs
    "\U0001F680-\U0001F6FF"  # transport & map symbols
    "\U0001F1E0-\U0001F1FF"  # flags (iOS)
    "]+",
    flags=re.UNICODE,
)
