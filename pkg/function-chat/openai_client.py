# openai_client.py
import os
import openai
import json
import logging
from typing import List, Dict, Any
from conversations_repository import SpeechBubble

class OpenAIClient:
    def __init__(self, organization, openai_api_key):
        self.organization = organization
        self.openai_api_key = openai_api_key
        openai.organization = self.organization
        openai.api_key = self.openai_api_key
        logging.info(f'OpenAIClient initialized with organization: {self.organization} and key: {self.openai_api_key}')

    def list_models(self):
        try:
            models = openai.Model.list()
            return models
        except Exception as e:
            logging.error(f"Error: {e}")
            return None

    def create_chat_completion(self, model: str, conversation: List[SpeechBubble]):
        # Convert SpeechBubble objects to the expected format and remove keys with None values      
        messages = [bubble.speech_bubble_to_dict() for bubble in conversation]
        
        # Check if messages follow the required pattern
        for message in messages:
            if "role" not in message or message["role"] not in ["system", "user", "assistant", "function"]:
                logging.error('Invalid role in message.')
                return None
            
            if "content" not in message:
                logging.error('Message does not contain the required content key.')
                return None

            if message["role"] == "function":
                if "name" not in message or not isinstance(message["name"], str) or not (0 < len(message["name"]) <= 64):
                    logging.error('Invalid function name in function role message.')
                    return None
                
        logging.info(f"messages sent to ChatGPT Completion: {messages}")

        try:
            completion = openai.ChatCompletion.create(
                model=model,
                messages=messages
            )

            if completion.choices:
                message_content = completion.choices[0].message.get('content', None)
                message_role = completion.choices[0].message.get('role', 'assistant')
                
                return SpeechBubble(content=message_content, role=message_role)
            
            return None
        except Exception as e:
            logging.error(f"Error: {e}")
            return None

        
    from typing import Dict, Any, List, Optional

    def create_chat_completion_with_functions(self, model: str, conversation: List[SpeechBubble], functions: List[Dict[str, Any]], function_callbacks: Dict[str, Any], function_messages: Optional[Dict[str, List[Dict]]] = None) -> List[Optional[SpeechBubble]]:
        """
        Creates a chat completion with the ability to call custom functions.
        
        Args:
        - model (str): Identifying the model (e.g. "gpt-4-0613").
        - conversation (List[SpeechBubble]): Conversation history.
        - functions (List[Dict[str, Any]]): Functions the model can call. Each function dictionary contains "name", "description", and "parameters" keys.
        - function_callbacks (Dict[str, Any]): Mapping of function names to callback functions.
        
        Returns:
        - List[Optional[SpeechBubble]]: Responses for each function call or None on errors.
        
        Raises:
        - ValueError: On invalid input.
        - Exception: On errors in creating the chat completion.
        """
        if not functions:
            raise ValueError("Functions list cannot be empty.")

        if not function_callbacks:
            raise ValueError("Function callbacks dictionary cannot be empty.")

        # Check if all functions have corresponding callbacks
        for function in functions:
            if function['name'] not in function_callbacks:
                raise ValueError(f"No callback provided for function: {function['name']}")

        messages = [bubble.speech_bubble_to_dict() for bubble in conversation]  

        responses = []

        for function in functions:
            try:
                # Check if there are predefined messages for the current function
                if function_messages and function['name'] in function_messages:
                    function_specific_messages = function_messages[function['name']]
                    all_messages = function_specific_messages + messages
                else:
                    all_messages = messages.copy()

                logging.info(f"messages sent to ChatGPT Function: {all_messages}")

                completion = openai.ChatCompletion.create(
                    temperature=0,
                    model=model,
                    messages=all_messages,
                    functions=[function],
                    function_call={"name": function['name']}
                )

                logging.info(f"ChatGPT Function response: {completion}")

                response_message = completion.choices[0].message

                if not response_message.get("function_call"):
                    logging.error("No function call in response message.")
                    continue

                function_call_name = response_message["function_call"]["name"]
                function_call_args = json.loads(response_message["function_call"]["arguments"])

                # Call the corresponding function from the provided callbacks
                function_response = function_callbacks[function_call_name](**function_call_args)

                function_call_data = {
                    "name": function_call_name,
                    "arguments": function_call_args 
                } 

                function_call_bubble = SpeechBubble(
                    content=response_message.get('content', ''),
                    role=response_message.get('role', ''),
                    name=function_call_name if function_call_name else None,
                    function_call=json.dumps(function_call_data, ensure_ascii=False, separators=(',', ': '))
                )

                # Convert the object back to a formatted string
                cleaned_content = json.dumps(function_response, ensure_ascii=False, separators=(',', ': '))

                function_response_bubble = SpeechBubble(role="function", name=function_call_name, content=cleaned_content)

                responses.append(function_call_bubble)
                responses.append(function_response_bubble)

            except Exception as e:
                logging.error(f"Error: {e}")
                responses.append(None)

        return responses


