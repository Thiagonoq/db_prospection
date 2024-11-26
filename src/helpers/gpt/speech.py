import uuid

from pydub import AudioSegment

from config import TMP_PATH, openai
from src.helpers.download import download_file
from src.models.analytics import (
    GPT,
    GPTAvailableModels,
    GPTWhisperModel,
    TemplateAnalytics,
)
from src.models.zapi import MessageTypes


async def speech_to_text(message: MessageTypes, session):
    session.flow.lockCreation = True
    await session.flow.update()

    tmp_audio_file = await download_file(
        message.audio.audioUrl, session.session_path, ""
    )
    tmp_file_path = session.session_path / f"{uuid.uuid4().hex}.mp3"

    audio = AudioSegment.from_file(tmp_audio_file)

    audio.export(tmp_file_path, format="mp3")

    expense = (audio.duration_seconds / 60) * 0.006

    template_name = session.flow.currentTemplate

    if not session.flow.currentTemplate:
        template_name = "NotIdentified"

    if template_name not in [template.name for template in session.analytics.templates]:
        session.analytics.templates.append(
            TemplateAnalytics(
                name=template_name,
                gpt=GPT(
                    usage=[
                        GPTWhisperModel(
                            name=GPTAvailableModels.whisper,
                            seconds=audio.duration_seconds,
                            expense=expense,
                        )
                    ],
                ),
            )
        )
    else:
        for template in session.analytics.templates:
            if template.name == template_name:
                if GPTAvailableModels.whisper not in [
                    model.name for model in template.gpt.usage
                ]:
                    template.gpt.usage.append(
                        GPTWhisperModel(
                            name=GPTAvailableModels.whisper,
                            expense=expense,
                            seconds=audio.duration_seconds,
                        )
                    )
                else:
                    for model in template.gpt.usage:
                        if model.name == GPTAvailableModels.whisper:
                            model.seconds += audio.duration_seconds
                            model.expense += expense
                            break
                break

    await session.analytics.save()

    text = (
        await openai.audio.transcriptions.create(
            model="whisper-1", file=open(tmp_file_path, "rb")
        )
    ).text

    session.flow.lockCreation = False
    await session.flow.update()

    return text
