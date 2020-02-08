from typing import Union, Dict, Any, List

from .message import Message, MessageSegment

__all__ = [
    'Message_T',
]

Message_T = Union[str, Dict[str, Any], List[Dict[str, Any]],
                  MessageSegment, Message]
