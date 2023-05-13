# types.py
from typing import Any, Dict, List, Optional

# Definieren Sie einen Typ für die 'data', die in der Anforderung erhalten wird
Data = Dict[str, Any]

# Definieren Sie einen Typ für die 'message', die innerhalb der 'data' empfangen wird
Message = str

# Definieren Sie einen Typ für die 'message_json', das ist das Ergebnis der JSON-Analyse der 'message'
MessageJson = Dict[str, Any]

# Weitere Typendefinitionen basierend auf Ihrer OpenAPI-Spezifikation
Id = str
Time = int
Expires = Optional[int]
Event = str
Topic = str
Title = Optional[str]
Tags = Optional[List[str]]
Priority = Optional[int]
Click = Optional[str]
Actions = Optional[List[Dict[str, Any]]]
Attachment = Optional[Dict[str, Any]]
