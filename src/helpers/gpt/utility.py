import base64
from pathlib import Path

from config import openai
from src.handlers.session import Session
from src.helpers import date
from src.helpers.gpt import ChatAssistant
from src.helpers.message import extract_json
from src.helpers.ner import json_to_named_entity_relational
from src.helpers.validate import check_non_null_values, get_null_keys
from src.models.analytics import GPTAvailableModels
from src.models.client import ClientActions


async def generate_json_gpt4(
    chat: ChatAssistant,
    json_data: str,
    message_extra: str = "",
    check_null_values: bool = True,
    null_keys: bool = False,
    expect_type=None,
):
    if type(json_data) == dict:
        json_data = json_to_named_entity_relational(json_data)

    now = date.now().strftime("%d/%m/%Y, %H:%M:%S")

    message = f"Hoje é dia: {now}\n{message_extra}\n\nSiga a seguinte estrutura de JSON:\n{json_data}"

    await chat.change_assistant("generateJSON")

    trys = 2

    while trys:
        result = await chat.create_message(message)

        parsed_json = extract_json(result)

        if expect_type and type(parsed_json) != expect_type:
            trys -= 1
            continue

        if null_keys:
            return parsed_json, get_null_keys((parsed_json or {}).get("data", {}))

        if not check_null_values or check_non_null_values(parsed_json):
            return parsed_json

        trys -= 1

    raise Exception("Failed to generate JSON")


async def identify_image_is_logo(session: Session):
    assistant = await ChatAssistant.get_assistant("identifyLogo")

    model = assistant.get("model", GPTAvailableModels.gpt_4_vision_preview)

    result = await openai.chat.completions.create(
        model=model,
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": assistant["system"]},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{base64.b64encode(Path(session.message.value).read_bytes()).decode()}",
                            "detail": "low",
                        },
                    },
                ],
            }
        ],
    )

    await ChatAssistant.analytics(
        result, session.analytics, session.flow.currentTemplate, model
    )

    data = extract_json(result.choices[0].message.content)

    return type(data) == dict and data.get("logo", False)


async def identify_user_action(session: Session):
    assistant = await ChatAssistant.get_assistant("identifyAction")

    model = assistant.get("model", "gpt-3.5-turbo-0125")

    args = {
        "temperature": assistant.get("temperature", 0),
        "model": model,
        "messages": [
            {
                "role": "system",
                "content": assistant.get("system", ""),
            },
            {
                "role": "assistant",
                "content": session.message.caption or session.message.value,
            },
        ],
    }

    result = await openai.chat.completions.create(**args)

    content = result.choices[0].message.content

    data = extract_json(content)

    await ChatAssistant.analytics(
        result, session.analytics, session.flow.currentTemplate, model
    )

    return (data or {}).get("action", "create_art")
