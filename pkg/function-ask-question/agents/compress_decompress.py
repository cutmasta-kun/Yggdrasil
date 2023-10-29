# compress_decompress_py

import autogen
import os
import argparse
import logging

# Konfigurieren der Anwendung
logging.basicConfig(level=logging.INFO)

OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', 'replace-me-af')

config_list = [
    {
        'model': 'gpt-4',
        'api_key': OPENAI_API_KEY,
    }
]

llm_config = {
    "request_timeout": 600,
    "seed": 1,
    "config_list": config_list,
    "temperature": 0
}

def is_termination_msg(content):
    have_content = content.get("content", None) is not None
    if have_content and "APPROVED" in content["content"]:
        return True
    return False

COMPRESS_SYSTEM_MESSAGE = """
# MISSION
You are a Sparse Priming Representation (SPR) writer. An SPR is a particular kind of use of language for advanced NLP, NLU, and NLG tasks, particularly useful for the latest generation Large Language Models (LLMs). You will be given information by the USER which you are to render as an SPR.

# THEORY
LLMs are a kind of deep neural network. They have been demonstrated to embed knowledge, abilities, and concepts, ranging from reasoning to planning, and even to theory of mind. These are called latent abilities and latent content, collectively referred to as latent space. The latent space of a LLM can be activated with the correct series of words as inputs, which will create a useful internal state of the neural network. This is not unlike how the right shorthand cues can prime a human mind to think in a certain way. Like human minds, LLMs are associative, meaning you only need to use the correct associations to "prime" another model to think in the same way.

# METHODOLOGY
Render the input as a distilled list of succinct statements, assertions, associations, concepts, analogies, and metaphors. The idea is to capture as much, conceptually, as possible but with as few words as possible. Write it in a way that makes sense to you, as the future audience will be another language model, not a human.
"""

DECOMPRESS_SYSTEM_MESSAGE = """
# MISSION
You are a Sparse Priming Representation (SPR) decompressor. An SPR is a particular kind of use of language for advanced NLP, NLU, and NLG tasks, particularly useful for the latest generation Large Language Models (LLMs). You will be given an SPR and your job is to fully unpack it.

# THEORY
LLMs are a kind of deep neural network. They have been demonstrated to embed knowledge, abilities, and concepts, ranging from reasoning to planning, and even to theory of mind. These are called latent abilities and latent content, collectively referred to as latent space. The latent space of a LLM can be activated with the correct series of words as inputs, which will create a useful internal state of the neural network. This is not unlike how the right shorthand cues can prime a human mind to think in a certain way. Like human minds, LLMs are associative, meaning you only need to use the correct associations to "prime" another model to think in the same way.

# METHODOLOGY
Use the primings given to you to fully unpack and articulate the concept. Talk through every aspect, impute what's missing, and use your ability to perform inference and reasoning to fully elucidate this concept. Your output should in the form of the original article, document, or material.
"""

USER_PROXY_PROMPT = """
# MISSION
You are a Review Assistant for Sparse Priming Representations (SPR). Your task is to carefully review the SPR message you receive. If the message appears correct and satisfactory, please respond with 'APPROVED'. Otherwise, provide feedback for improvements.

# ROLE
As a Review Assistant, your role is to ensure the quality and accuracy of SPR messages. You are the final checkpoint before an SPR is considered complete.

# GUIDELINES
Review the SPR message for clarity, coherence, and relevance. Make sure it aligns with the intended purpose and follows the principles of SPR. If you find any issues or areas for improvement, provide constructive feedback.
"""


user_proxy = autogen.UserProxyAgent(
   name="user_proxy",
   human_input_mode="NEVER",
   system_message=USER_PROXY_PROMPT,
   code_execution_config=False,
   max_consecutive_auto_reply=1,
   is_termination_msg=is_termination_msg,
   llm_config=llm_config
)

def get_last_message_before_approval(messages):
    """
    Searches messages in reverse order and returns the last assistant's message before approval.

    Parameters:
    messages (list): List of message dictionaries.

    Returns:
    dict: The last message from the assistant before approval, or None if not found.
    """
    for i in range(len(messages) - 1, 0, -1):
        if messages[i]['content'] == 'APPROVED' and messages[i - 1]['role'] == 'assistant':
            return messages[i - 1]
    return None

def initiate_chat_with_agent(agent, text):
    """
    Initiates a chat with an agent and returns the messages.

    Parameters:
    agent (Agent): The agent to chat with.
    text (str): The initial message to start the chat.

    Returns:
    list: Copy of the chat messages.
    """
    user_proxy.initiate_chat(agent, message=text, silent=True)
    messages = agent.chat_messages

    user_proxy_key = list(messages.keys())[0]
    message_list_copy = messages[user_proxy_key].copy()
    return message_list_copy

def get_last_message_before_approval_or_fail(messages):
    """
    Retrieves the last message before approval or raises an error if not found.

    Parameters:
    messages (list): List of message dictionaries.

    Returns:
    dict: The last message from the assistant before approval.

    Raises:
    ValueError: If no valid response is found before approval.
    """
    last_message = get_last_message_before_approval(messages)
    if not last_message:
        raise ValueError("Keine gültige Antwort vor der Genehmigung gefunden.")
    return last_message

def compress(text: str) -> str:
    """
    Compresses the given text.

    Parameters:
    text (str): The text to be compressed.

    Returns:
    str: The compressed text.

    Raises:
    ValueError: If the text to compress is empty.
    """
    if not text:
        raise ValueError("Der zu komprimierende Text darf nicht leer sein.")

    compress_assistant = autogen.AssistantAgent(
        name="compress_assistant",
        llm_config=llm_config,
        code_execution_config=False,
        system_message=COMPRESS_SYSTEM_MESSAGE,
        is_termination_msg=is_termination_msg,
    )

    messages = initiate_chat_with_agent(compress_assistant, text)
    return get_last_message_before_approval_or_fail(messages)['content']

def decompress(text: str) -> str:
    """
    Decompresses the given text.

    Parameters:
    text (str): The text to be decompressed.

    Returns:
    str: The decompressed text.

    Raises:
    ValueError: If the text to decompress is empty.
    """
    if not text:
        raise ValueError("Der zu dekomprimierende Text darf nicht leer sein.")

    decompress_assistant = autogen.AssistantAgent(
        name="decompress_assistant",
        llm_config=llm_config,
        code_execution_config=False,
        system_message=DECOMPRESS_SYSTEM_MESSAGE,
        is_termination_msg=is_termination_msg,
    )

    messages = initiate_chat_with_agent(decompress_assistant, text)
    return get_last_message_before_approval_or_fail(messages)['content']

def main(args):
    try:
        if not args.text:
            raise ValueError("Text must not be empty.")

        result = None  # Variable to store the result of the compress or decompress function

        if args.action == 'compress':
            result = compress(args.text)
        elif args.action == 'decompress':
            result = decompress(args.text)
        else:
            print("Invalid action specified. Please use 'compress' or 'decompress'.")
            return

        # Print the result to the console in a more user-friendly format
        print("\n" + "="*50)
        print("Result:")
        print("="*50 + "\n")
        print(result)
        print("\n" + "="*50)
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Compresses or decompresses text using AutoGen.")
    parser.add_argument("text", type=str, help="The text to be compressed or decompressed.")
    parser.add_argument("action", type=str, choices=['compress', 'decompress'], help="The action to be performed. Either 'compress' or 'decompress'.")
    args = parser.parse_args()
    main(args)