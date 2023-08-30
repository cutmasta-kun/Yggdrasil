from typing import Dict, Iterable, List, Tuple, TypedDict, Optional
import json
import chainlit as cl

from litechain import debug
from litechain.contrib import OpenAIChatChain, OpenAIChatDelta, OpenAIChatMessage
import logging
from chains.weather import get_current_weather



class Memory(TypedDict):
    history: List[OpenAIChatMessage]


memory = Memory(history=[])


def save_message_to_memory(message: OpenAIChatMessage) -> OpenAIChatMessage:
    print(f"\n\n{memory['history']}\n\n")

    memory["history"].append(message)
    return message

def update_delta_on_memory(delta: OpenAIChatDelta) -> OpenAIChatDelta:
    if memory["history"][-1].role != delta.role and delta.role is not None:
        memory["history"].append(
            OpenAIChatMessage(role=delta.role, content=delta.content, name=delta.name if delta.name else None)
        )
    else:
        memory["history"][-1].content += delta.content
    return delta

translator_chain = OpenAIChatChain[Iterable[OpenAIChatDelta], OpenAIChatDelta](
    "TranslatorChain",
    lambda user_message: [
        OpenAIChatMessage(
            role="user",
            content=f"'{user_message}'. Reply in English and Russian.",
        )
    ],
    model="gpt-3.5-turbo",
)

chat_chain = OpenAIChatChain[str, OpenAIChatDelta](
    "ChatChain",
    lambda user_message: [
        *memory["history"],
        save_message_to_memory(
            OpenAIChatMessage(
                role="user", content=user_message
            )
        ),
    ],
    model="gpt-3.5-turbo-0613",
)



weather_chain = (
    debug(
        OpenAIChatChain[str, OpenAIChatDelta](
            "WeatherChain",
            lambda user_message: [
                *memory["history"],
                save_message_to_memory(
                    OpenAIChatMessage(
                        role="user", content=user_message
                    )
                ),
            ],
            functions=[get_current_weather],
            model="gpt-3.5-turbo-0613",
            temperature=0,
        )
    )
    .map(update_delta_on_memory)
    .collect()
    .and_then(debug(translator_chain))
)

@cl.on_message
async def on_message(message: str):
    messages_map: Dict[str, Tuple[bool, cl.Message]] = {}

    async for output in weather_chain(message):
        if "@" in output.chain and not output.final:
            continue
        if output.chain in messages_map:
            sent, cl_message = messages_map[output.chain]
            if not sent:
                await cl_message.send()
                messages_map[output.chain] = (True, cl_message)
            await cl_message.stream_token(output.data.content)
        else:
            messages_map[output.chain] = (
                False,
                cl.Message(
                    author=output.chain,
                    content=output.data.content,
                    indent=0 if output.final else 1,
                ),
            )
