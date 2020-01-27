from typing import Dict, Any, Optional


class Event(dict):
    @staticmethod
    def from_payload(payload: Dict[str, Any]) -> 'Optional[Event]':
        try:
            e = Event(payload)
            _ = e.type, e.detail_type
            return e
        except KeyError:
            return None

    @property
    def type(self) -> str:
        return self['post_type']

    @property
    def detail_type(self) -> str:
        return self[f'{self.type}_type']

    @property
    def sub_type(self) -> Optional[str]:
        return self.get('sub_type')

    @property
    def name(self):
        n = self.type + '.' + self.detail_type
        if self.sub_type:
            n += '.' + self.sub_type
        return n

    @property
    def self_id(self) -> int:
        return self['self_id']

    @property
    def user_id(self) -> Optional[int]:
        return self.get('user_id')

    @property
    def operator_id(self) -> Optional[int]:
        return self.get('operator_id')

    @property
    def group_id(self) -> Optional[int]:
        return self.get('group_id')

    @property
    def discuss_id(self) -> Optional[int]:
        return self.get('discuss_id')

    @property
    def message_id(self) -> Optional[int]:
        return self.get('message_id')

    @property
    def message(self) -> Optional[Any]:
        return self.get('message')

    @property
    def raw_message(self) -> Optional[str]:
        return self.get('raw_message')

    @property
    def sender(self) -> Optional[Dict[str, Any]]:
        return self.get('sender')

    @property
    def anonymous(self) -> Optional[Dict[str, Any]]:
        return self.get('anonymous')

    @property
    def file(self) -> Optional[Dict[str, Any]]:
        return self.get('file')

    @property
    def comment(self) -> Optional[str]:
        return self.get('comment')

    @property
    def flag(self) -> Optional[str]:
        return self.get('flag')

    def __repr__(self) -> str:
        return f'<Event, {super().__repr__()}>'
