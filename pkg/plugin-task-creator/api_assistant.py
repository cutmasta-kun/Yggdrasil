# api_assistant.py
# 
# version 1.5
#
# is needed by:
#   fast_api_boilerplate.py =>1.8

import logging
from typing import Dict, Any, Optional, Union
from instructor import Maybe, patch
from openai import OpenAI
from pydantic import BaseModel, Field, model_validator
import os

class Message(BaseModel):
    content: str
    role: str

class Validation(BaseModel):
    is_valid: bool = Field(
        ..., description="Whether the value is valid given the rules"
    )
    error_message: Optional[str] = Field(
        ...,
        description="The error message if the value is not valid, to be used for re-asking the model",
    )

class ApiValidation(BaseModel):
    is_valid: bool = Field(..., description="Indicates whether the API request is valid or not.")
    explanation: str = Field(..., description="Provides a precise explanation or reason for the validity status.")

MaybeValidation = Maybe(ApiValidation)

class ApiPayload(BaseModel):
    action: str = Field(..., description="The interpreted operation from the user request.")
    parameters: Union[Dict[str, Any], None] = Field(default_factory=None, description="The interpreted parameters from the user request.")

MaybeApiPayload = Maybe(ApiPayload)

class InternalState(BaseModel):
    raw: str = Field(..., description="The raw text of the internal state")

class ApiAssistant:
    def __init__(self, documentation: Dict[str, str], withState: bool = False):
        self.documentation = documentation
        self.client = patch(OpenAI())
        self.validation: MaybeValidation = None
        self.withState = withState
        self.state = None
        self.events = []

        if self.withState:
            self._initialize_state()

    @staticmethod
    def _get_format_from_name(doc_name: str) -> str:
        if 'yaml' in doc_name or 'openapi' in doc_name:
            return 'yaml'
        if 'json' in doc_name:
            return 'json'
        if 'md' in doc_name:
            return 'markdown'
        return 'text'

    def _compose_system_message(self, base_message: str) -> str:
        system_message = base_message
        for doc_name, doc_content in self.documentation.items():
            system_message += f"\n\nHere is the {doc_name} documentation:\n```{self._get_format_from_name(doc_name)}\n{doc_content}\n```"
        return system_message
    
    def add_event(self, event: str):
        """
        Adds an event to the list of events.
        """
        if isinstance(event, str):
            self.events.append(event)
        else:
            logging.error(f"Event must be a string, got: {type(event)}")


    def validate_user_request_against_api(self, userRequest: str, context: dict = None) -> MaybeValidation:
        base_message = """You are an evaluation system for an API, capable of understanding requests in multiple languages. Your task is to determine if a user request, regardless of its language, can theoretically be translated into a valid API call based on the provided API documentation. Focus on the intent and content of the request, not the language. Consider:
- Does the request's intent match any of the API's capabilities?
- Can the request be associated with a specific API route, considering its intent?
- Are there sufficient details in the request to infer necessary parameters for that route?

Your explanation is crucial for guiding subsequent actions. Therefore, please ensure your response is concise and precise, containing all necessary information."""
        system_message = self._compose_system_message(base_message)

        user_message = f"""Based on the API documentation, evaluate if this user request can be theoretically translated into a valid API call: 

User Request: #--{userRequest}--#"""
        
        try:
            validation: MaybeValidation = self.client.chat.completions.create(
                model="gpt-4-1106-preview",
                response_model=MaybeValidation,
                messages=[
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": user_message}
                ]
            )
            self.validation = validation
            
            self.events.append(f"Validation: {validation.model_dump()}")

            return validation
        except Exception as e:
            logging.error(f"Fehler bei der API-Anfrage: {e}")
            return MaybeValidation(error=True, message=f"Fehler bei der API-Anfrage: {e}")

    def interpret_user_request(self, userRequest: str, context: dict = None) -> MaybeApiPayload:
        base_message = """You are an intelligent agent tasked with interpreting user requests for an API. Your goal is to understand the request in any language and deduce the appropriate API action (operationId) and parameters needed to fulfill it, based on the provided API documentation. Consider the following:

- Identify the 'operationId' from the API documentation that best matches the intent of the user request. Consider this as the 'action' to be performed.
- Determine the necessary parameters required for this action by carefully analyzing the user request and the API route specifications. Consider parameters like 'uuid', 'message', or 'limit', which might be explicitly mentioned or implied in the user request.
- Ensure that the user request's intent aligns with the capabilities and actions defined in the API documentation. Use the context and information from the validation phase to guide your interpretation.

When providing the action and parameters, structure your response to clearly delineate the 'action' as the operationId and list the 'parameters' along with their values derived from the user request."""
        system_message = self._compose_system_message(base_message)

        user_message = f"""Based on the API documentation, extract the neccessary `action` and `parameters` for this User Request: 

User Request: #--{userRequest}--#

The validation of this user request resulted with this explaination to proof it's validity:

Validation Explanation: #--{self.validation.result.explanation}--#

Additional context: #--{context}--#
"""

        try:
            api_payload: MaybeApiPayload = self.client.chat.completions.create(
                model="gpt-4-1106-preview",
                response_model=MaybeApiPayload,
                max_retries=1,
                messages=[
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": user_message}
                ]
            )

            self.events.append(f"Generated Payload: {api_payload.model_dump()}")
            
            return api_payload
        except Exception as e:
            logging.error(f"Fehler bei der Interpretation der Benutzeranfrage: {e}")
            return MaybeApiPayload(error=True, message=f"Fehler bei der Interpretation der Benutzeranfrage: {e}")
    
    def _initialize_state(self):
        state_path = './api_state.txt'
        if os.path.exists(state_path) and os.path.getsize(state_path) > 0:
            with open(state_path, 'r') as file:
                self.state = file.read()
        else:
            with open(state_path, 'w') as file:
                file.write('State is empty')
            self.state = 'State is empty'

    def update_state_file(self):
        """
        Generates a new state based on events and updates the state file.
        """
        # Generate the new state
        new_internal_state = self.generate_state()

        # Write the new state to the file if it's valid
        if new_internal_state and not new_internal_state.raw.startswith("Fehler"):
            self.state = new_internal_state.raw
            with open('./api_state.txt', 'w') as file:
                file.write(self.state)
            logging.info("State updated successfully.")
        else:
            logging.error("Failed to update state.")

    def generate_state(self) -> InternalState:
        """
        Generates a new state based on the events that have been recorded.
        """
        system_message = """You are an intelligent system managing the internal state of an API. Your role is to maintain a 'thought dump' or a history of interactions and significant occurrences. This internal state is not meant for external consumption but serves as the API's memory, evolving with each interaction.

Consider the following:

- The state should evolve based on the interactions and events.
- Not all previous state information needs to be retained. Only carry forward what is deemed essential.
- The new state should be a reflection of the API's recent activities and any relevant changes.
"""
# - Use the provided documentation as a context to understand the types of interactions that occur.
        # Convert the events list into a single string
        events_str = '\n'.join(self.events)

        user_message = f"""Here is the previous state and the new events:
Previous state: #--{self.state}--#


New Events: #--{events_str}--#
    """
        try:
            internalState: InternalState = self.client.chat.completions.create(
                model="gpt-4-1106-preview",
                response_model=InternalState,
                max_retries=1,
                messages=[
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": user_message}
                ]
            )
            # After generating the new state, consider resetting or updating the events list
            logging.info(f"internalState: {internalState}")
            return internalState
        except Exception as e:
            logging.error(f"Fehler beim Generieren des States: {e}")
            return InternalState(raw=f"Fehler beim Generieren des States: {e}")

    