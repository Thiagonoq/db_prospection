import logging
import re

import phonenumbers


def format_phone(phone, country="BR"):
    try:
        phone = re.sub(r"\D", "", str(phone))

        if len(phone) == 12:
            phone = phone[:4] + "9" + phone[4:]
        elif len(phone) == 10:
            phone = phone[:2] + "9" + phone[2:]

        parsed_phone = phonenumbers.parse(phone, country)

        if phonenumbers.is_valid_number(parsed_phone):
            return phonenumbers.format_number(
                parsed_phone, phonenumbers.PhoneNumberFormat.NATIONAL
            )
        else:
            logging.error(f"Invalid phone number: {phone}")
            return phone
    except phonenumbers.NumberParseException:
        return False
