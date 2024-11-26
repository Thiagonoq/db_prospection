import logging
import uuid

from config import openai
from src.database import mongo
from src.helpers import date
from src.helpers.analytics import Analytics
from src.helpers.async_object import AsyncObject
from src.helpers.maps import input_pricing, output_pricing
from src.models.analytics import (
    GPT,
    GPTAvailableModels,
    GPTTextModel,
    TemplateAnalytics,
)
from src.models.models import GPTRole


class ChatAssistant(AsyncObject):
    async def __init__(
        self,
        session,
        assistant: str = None,
        thread_id: str = None,
        thread_name: str = None,
    ):
        self.session = session

        self.phone = session.phone
        self.assistant = assistant
        self.thread_id = thread_id
        self.thread_name = thread_name or "thread"

        self.model = GPTAvailableModels.gpt_3_5_turbo_0125

        self.__system = ""
        self.__temperature = 0
        self.__max_tokens = 4095

        await self.__load()

        return self

    async def __load(self):
        assistant = await self.get_assistant(self.assistant)

        data = await mongo.database.threads.find_one({"id": self.thread_id})

        self.model = assistant.get("model", GPTAvailableModels.gpt_3_5_turbo_0125)

        self.__system = assistant.get("system", "")
        self.__temperature = assistant.get("temperature", 1)
        self.__max_tokens = assistant.get("max_tokens", 4095)

        if data:
            self.thread_id = data.get("id")
            self.status = data.get("status")
            self.messages = data.get("messages")

            if self.messages and self.messages[0].get("role") == "system":
                self.messages[0]["content"] = self.__system
        else:
            self.status = "standby"
            self.thread_id = uuid.uuid4().hex
            self.messages = [{"role": "system", "content": self.__system}]

            await mongo.database.threads.insert_one(
                {
                    "id": self.thread_id,
                    "messages": self.messages,
                    "status": self.status,
                    "phone": self.phone,
                    "created_at": date.now(),
                    "threadName": self.thread_name,
                }
            )

    @staticmethod
    async def get_assistant(assistant_name: str = None):
        assistant = await mongo.database.assistants.find_one({"name": assistant_name})

        if not assistant:
            return {}

        return assistant

    async def change_assistant(self, assistant: str):
        self.assistant = assistant

        await self.__load()

    async def add_extra_to_system(self, content: str, prepend: bool = False):
        if prepend:
            self.__system = content + self.__system
        else:
            self.__system = self.__system + content

        if self.messages:
            self.messages[0]["content"] = self.__system

        await mongo.database.threads.update_one(
            {"id": self.thread_id}, {"$set": {"messages": self.messages}}
        )

    async def add(self, role: GPTRole, content: str):
        message_data = {"role": role, "content": content}

        self.messages.append(message_data)

        await mongo.database.threads.update_one(
            {"id": self.thread_id}, {"$push": {"messages": message_data}}
        )

    async def batch_add(self, messages: list):
        self.messages.extend(messages)

        await mongo.database.threads.update_one(
            {"id": self.thread_id}, {"$push": {"messages": {"$each": messages}}}
        )

    async def remove_user_text(self, text: str):
        await mongo.database.threads.update_one(
            {"id": self.thread_id},
            {"$pull": {"messages": {"role": "user", "content": text}}},
        )

    async def remove_last_entry(self):
        await mongo.database.threads.update_one(
            {"id": self.thread_id}, {"$pop": {"messages": 1}}
        )

    async def remove_all_assistants_messages(self):
        await mongo.database.threads.update_one(
            {"id": self.thread_id}, {"$pull": {"messages": {"role": "assistant"}}}
        )

    async def run(self):
        self.status = "running"

        await mongo.database.threads.update_one(
            {"id": self.thread_id}, {"$set": {"status": "running"}}
        )

        try:
            result = await openai.chat.completions.create(
                model=self.model,
                max_tokens=self.__max_tokens,
                temperature=self.__temperature,
                messages=self.messages,
            )

            template_name = self.session.flow.currentTemplate

            if not self.session.flow.currentTemplate:
                template_name = "NotIdentified"

            await self.analytics(
                result, self.session.analytics, template_name, self.model
            )

            await self.add(GPTRole.assistant, result.choices[0].message.content)

            return result.choices[0].message.content
        except Exception as e:
            logging.exception(e)
            return False

    async def create_message(self, content: str = ""):
        if content:
            try:
                await self.add("user", content)
            except:
                pass

        return await self.run()

    @staticmethod
    async def analytics(
        gpt_response,
        analytics: "Analytics",
        template_name="NotIdentified",
        model_name: str = GPTAvailableModels.gpt_3_5_turbo_1106,
    ):
        expense = (
            (gpt_response.usage.prompt_tokens * input_pricing[model_name]) / 1000
        ) + ((gpt_response.usage.completion_tokens * output_pricing[model_name]) / 1000)

        if not template_name:
            template_name = "NotIdentified"

        if template_name not in [template.name for template in analytics.templates]:
            new_template_analytics = TemplateAnalytics(
                name=template_name,
                gpt=GPT(
                    usage=[
                        GPTTextModel(
                            name=model_name,
                            expense=expense,
                            promptTokens=gpt_response.usage.prompt_tokens,
                            completionTokens=gpt_response.usage.completion_tokens,
                        )
                    ],
                ),
            )

            analytics.templates.append(new_template_analytics)
        else:
            for template in analytics.templates:
                if template.name == template_name:
                    if model_name not in [model.name for model in template.gpt.usage]:
                        template.gpt.usage.append(
                            GPTTextModel(
                                name=model_name,
                                expense=expense,
                                promptTokens=gpt_response.usage.prompt_tokens,
                                completionTokens=gpt_response.usage.completion_tokens,
                            )
                        )
                    else:
                        for model in template.gpt.usage:
                            if model.name == model_name:
                                model.expense += expense
                                model.promptTokens += gpt_response.usage.prompt_tokens
                                model.completionTokens += (
                                    gpt_response.usage.completion_tokens
                                )
                                break
                    break

        await analytics.save()
