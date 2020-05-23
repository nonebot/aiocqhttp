"""
此模块提供了 CQHTTP 事件相关的类。
"""

from typing import Dict, Any, Optional


class Event(dict):
    """
    封装从 CQHTTP 收到的事件数据对象（字典），提供属性以获取其中的字段。

    除 `type` 和 `detail_type` 属性对于任何事件都有效外，其它属性存在与否（不存在则返回
    `None`）依事件不同而不同。
    """

    @staticmethod
    def from_payload(payload: Dict[str, Any]) -> 'Optional[Event]':
        """
        从 CQHTTP 事件数据构造 `Event` 对象。
        """
        try:
            e = Event(payload)
            _ = e.type, e.detail_type
            return e
        except KeyError:
            return None

    @property
    def type(self) -> str:
        """
        事件类型，有 ``message``、``notice``、``request``、``meta_event`` 等。
        """
        return self['post_type']

    @property
    def detail_type(self) -> str:
        """
        事件具体类型，依 `type` 的不同而不同，以 ``message`` 类型为例，有
        ``private``、``group``、``discuss`` 等。
        """
        return self[f'{self.type}_type']

    @property
    def sub_type(self) -> Optional[str]:
        """
        事件子类型，依 `detail_type` 不同而不同，以 ``message.private`` 为例，有
        ``friend``、``group``、``discuss``、``other`` 等。
        """
        return self.get('sub_type')

    @property
    def name(self):
        """
        事件名，对于有 `sub_type` 的事件，为 ``{type}.{detail_type}.{sub_type}``，否则为
        ``{type}.{detail_type}``。
        """
        n = self.type + '.' + self.detail_type
        if self.sub_type:
            n += '.' + self.sub_type
        return n

    self_id: int  # 机器人自身 ID
    user_id: Optional[int]  # 用户 ID
    operator_id: Optional[int]  # 操作者 ID
    group_id: Optional[int]  # 群 ID
    discuss_id: Optional[int]  # 讨论组 ID
    message_id: Optional[int]  # 消息 ID
    message: Optional[Any]  # 消息
    raw_message: Optional[str]  # 未经 CQHTTP 处理的原始消息
    sender: Optional[Dict[str, Any]]  # 消息发送者信息
    anonymous: Optional[Dict[str, Any]]  # 匿名信息
    file: Optional[Dict[str, Any]]  # 文件信息
    comment: Optional[str]  # 请求验证消息
    flag: Optional[str]  # 请求标识

    def __getattr__(self, key) -> Optional[Any]:
        return self.get(key)

    def __setattr__(self, key, value) -> None:
        self[key] = value

    def __repr__(self) -> str:
        return f'<Event, {super().__repr__()}>'
