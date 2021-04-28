import sys
from typing import Union, Awaitable, Any, Callable, Optional, Dict, List

from aiocqhttp.typing import Message_T


if sys.version_info >= (3, 8, 0):
    from typing import TypedDict
    class _send_private_msg_ret(TypedDict):
        message_id: int

    class _send_group_msg_ret(TypedDict):
        message_id: int

    class _send_msg_ret(TypedDict):
        message_id: int

    class _get_msg_ret(TypedDict):
        time: int
        message_type: str
        message_id: int
        real_id: int
        sender: Dict[str, Any]
        message: Message_T

    class _get_forward_msg_ret(TypedDict):
        message: Message_T

    class _get_login_info_ret(TypedDict):
        user_id: int
        nickname: str

    class _get_stranger_info_ret(TypedDict):
        user_id: int
        nickname: str
        sex: str
        age: int

    class _get_friend_list_ret(TypedDict):
        user_id: int
        nickname: str
        remark: str

    class _get_group_info_ret(TypedDict):
        group_id: int
        group_name: str
        member_count: int
        max_member_count: int

    class _get_group_list_ret(_get_group_info_ret):
        ...

    class _get_group_member_info_ret(TypedDict):
        group_id: int
        user_id: int
        nickname: str
        card: str
        sex: str
        age: int
        area: str
        join_time: int
        last_sent_time: int
        level: str
        role: str
        unfriendly: bool
        title: str
        title_expire_time: int
        card_changeable: bool

    class _get_group_member_list_ret(_get_group_member_info_ret):
        ...

    class _get_group_honor_info_ret(TypedDict):
        group_id: int
        current_talkative: _get_group_honor_info_ret_current_talkative
        talkative_list: List[_get_group_honor_info_ret_wildcard_list]
        performer_list: List[_get_group_honor_info_ret_wildcard_list]
        legend_list: List[_get_group_honor_info_ret_wildcard_list]
        strong_newbie_list: List[_get_group_honor_info_ret_wildcard_list]
        emotion_list: List[_get_group_honor_info_ret_wildcard_list]

    class _get_group_honor_info_ret_current_talkative(TypedDict):
        user_id: int
        nickname: str
        avatar: str
        day_count: int

    class _get_group_honor_info_ret_wildcard_list(TypedDict):
        user_id: int
        nickname: str
        avatar: str
        description: str

    class _get_cookies_ret(TypedDict):
        cookies: str

    class _get_csrf_token_ret(TypedDict):
        token: int

    class _get_credentials_ret(TypedDict):
        cookies: str
        csrf_token: int

    class _get_record_ret(TypedDict):
        file: str

    class _get_image_ret(TypedDict):
        file: str

    class _can_send_image_ret(TypedDict):
        yes: bool

    class _can_send_record_ret(TypedDict):
        yes: bool

    class _get_status_ret(TypedDict):
        online: bool
        good: bool
        #__there_might_be_more_fields_below: Any

    class _get_version_info_ret(TypedDict):
        app_name: str
        app_version: str
        protocol_version: str
        #__there_might_be_more_fields_below: Any
else:
    _send_private_msg_ret = Dict[str, Any]
    _send_group_msg_ret = Dict[str, Any]
    _send_msg_ret = Dict[str, Any]
    _get_msg_ret = Dict[str, Any]
    _get_forward_msg_ret = Dict[str, Any]
    _get_login_info_ret = Dict[str, Any]
    _get_stranger_info_ret = Dict[str, Any]
    _get_friend_list_ret = Dict[str, Any]
    _get_group_info_ret = Dict[str, Any]
    _get_group_list_ret = Dict[str, Any]
    _get_group_member_info_ret = Dict[str, Any]
    _get_group_member_list_ret = Dict[str, Any]
    _get_group_honor_info_ret = Dict[str, Any]
    _get_cookies_ret = Dict[str, Any]
    _get_csrf_token_ret = Dict[str, Any]
    _get_credentials_ret = Dict[str, Any]
    _get_record_ret = Dict[str, Any]
    _get_image_ret = Dict[str, Any]
    _can_send_image_ret = Dict[str, Any]
    _can_send_record_ret = Dict[str, Any]
    _get_status_ret = Dict[str, Any]
    _get_version_info_ret = Dict[str, Any]


class Api:
    def call_action(
            self,
            action: str,
            **params,
    ) -> Union[Awaitable[Any], Any]: ...

    def __getattr__(
            self,
            item: str,
    ) -> Callable[..., Union[Awaitable[Any], Any]]: ...

    def send_private_msg(
            self, *,
            user_id: int,
            message: Message_T,
            auto_escape: bool = False,
            self_id: Optional[int] = None,
    ) -> Union[Awaitable[_send_private_msg_ret], _send_private_msg_ret]:
        """
        发送私聊消息。

        Args:
            user_id: 对方 QQ 号
            message: 要发送的内容
            auto_escape: 消息内容是否作为纯文本发送（即不解析 CQ 码），只在 `message` 字段是字符串时有效
            self_id: 机器人 QQ 号
        """

    def send_group_msg(
            self, *,
            group_id: int,
            message: Message_T,
            auto_escape: bool = False,
            self_id: Optional[int] = None,
    ) -> Union[Awaitable[_send_group_msg_ret], _send_group_msg_ret]:
        """
        发送群消息。

        Args:
            group_id: 群号
            message: 要发送的内容
            auto_escape: 消息内容是否作为纯文本发送（即不解析 CQ 码），只在 `message` 字段是字符串时有效
            self_id: 机器人 QQ 号
        """

    def send_msg(
            self, *,
            message_type: Optional[str] = None,
            user_id: Optional[int] = None,
            group_id: Optional[int] = None,
            message: Message_T,
            auto_escape: bool = False,
            self_id: Optional[int] = None,
    ) -> Union[Awaitable[_send_msg_ret], _send_msg_ret]:
        """
        发送消息。

        Args:
            message_type: 消息类型，支持 `private`、`group`，分别对应私聊、群组，如不传入，则根据传入的 `*_id` 参数判断
            user_id: 对方 QQ 号（消息类型为 `private` 时需要）
            group_id: 群号（消息类型为 `group` 时需要）
            message: 要发送的内容
            auto_escape: 消息内容是否作为纯文本发送（即不解析 CQ 码），只在 `message` 字段是字符串时有效
            self_id: 机器人 QQ 号
        """

    def delete_msg(
            self, *,
            message_id: int,
            self_id: Optional[int] = None,
    ) -> Union[Awaitable[None], None]:
        """
        撤回消息。

        Args:
            message_id: 消息 ID
            self_id: 机器人 QQ 号
        """

    def get_msg(
            self, *,
            message_id: int,
            self_id: Optional[int] = None,
    ) -> Union[Awaitable[_get_msg_ret], _get_msg_ret]:
        """
        获取消息。

        Args:
            message_id: 消息 ID
            self_id: 机器人 QQ 号
        """

    def get_forward_msg(
            self, *,
            id: str,
            self_id: Optional[int] = None,
    ) -> Union[Awaitable[_get_forward_msg_ret], _get_forward_msg_ret]:
        """
        获取合并转发消息。

        Args:
            id: 合并转发 ID
            self_id: 机器人 QQ 号
        """

    def send_like(
            self, *,
            user_id: int,
            times: int = 1,
            self_id: Optional[int] = None,
    ) -> Union[Awaitable[None], None]:
        """
        发送好友赞。

        Args:
            user_id: 对方 QQ 号
            times: 赞的次数，每个好友每天最多 10 次
            self_id: 机器人 QQ 号
        """

    def set_group_kick(
            self, *,
            group_id: int,
            user_id: int,
            reject_add_request: bool = False,
            self_id: Optional[int] = None,
    ) -> Union[Awaitable[None], None]:
        """
        群组踢人。

        Args:
            group_id: 群号
            user_id: 要踢的 QQ 号
            reject_add_request: 拒绝此人的加群请求
            self_id: 机器人 QQ 号
        """

    def set_group_ban(
            self, *,
            group_id: int,
            user_id: int,
            duration: int = 30 * 60,
            self_id: Optional[int] = None,
    ) -> Union[Awaitable[None], None]:
        """
        群组单人禁言。

        Args:
            group_id: 群号
            user_id: 要禁言的 QQ 号
            duration: 禁言时长，单位秒，0 表示取消禁言
            self_id: 机器人 QQ 号
        """

    def set_group_anonymous_ban(
            self, *,
            group_id: int,
            anonymous: Optional[Dict[str, Any]] = None,
            anonymous_flag: Optional[str] = None,
            duration: int = 30 * 60,
            self_id: Optional[int] = None,
    ) -> Union[Awaitable[None], None]:
        """
        群组匿名用户禁言。

        Args:
            group_id: 群号
            anonymous: 可选，要禁言的匿名用户对象（群消息上报的 `anonymous` 字段）
            anonymous_flag: 可选，要禁言的匿名用户的 flag（需从群消息上报的数据中获得）
            duration: 禁言时长，单位秒，无法取消匿名用户禁言
            self_id: 机器人 QQ 号
        """

    def set_group_whole_ban(
            self, *,
            group_id: int,
            enable: bool = True,
            self_id: Optional[int] = None,
    ) -> Union[Awaitable[None], None]:
        """
        群组全员禁言。

        Args:
            group_id: 群号
            enable: 是否禁言
            self_id: 机器人 QQ 号
        """

    def set_group_admin(
            self, *,
            group_id: int,
            user_id: int,
            enable: bool = True,
            self_id: Optional[int] = None,
    ) -> Union[Awaitable[None], None]:
        """
        群组设置管理员。

        Args:
            group_id: 群号
            user_id: 要设置管理员的 QQ 号
            enable: True 为设置，False 为取消
            self_id: 机器人 QQ 号
        """

    def set_group_anonymous(
            self, *,
            group_id: int,
            enable: bool = True,
            self_id: Optional[int] = None,
    ) -> Union[Awaitable[None], None]:
        """
        群组匿名。

        Args:
            group_id: 群号
            enable: 是否允许匿名聊天
            self_id: 机器人 QQ 号
        """

    def set_group_card(
            self, *,
            group_id: int,
            user_id: int,
            card: str = '',
            self_id: Optional[int] = None,
    ) -> Union[Awaitable[None], None]:
        """
        设置群名片（群备注）。

        Args:
            group_id: 群号
            user_id: 要设置的 QQ 号
            card: 群名片内容，不填或空字符串表示删除群名片
            self_id: 机器人 QQ 号
        """

    def set_group_name(
            self, *,
            group_id: int,
            group_name: str,
            self_id: Optional[int] = None,
    ) -> Union[Awaitable[None], None]:
        """
        设置群名。

        Args:
            group_id: 群号
            group_name: 新群名
            self_id: 机器人 QQ 号
        """

    def set_group_leave(
            self, *,
            group_id: int,
            is_dismiss: bool = False,
            self_id: Optional[int] = None,
    ) -> Union[Awaitable[None], None]:
        """
        退出群组。

        Args:
            group_id: 群号
            is_dismiss: 是否解散，如果登录号是群主，则仅在此项为 True 时能够解散
            self_id: 机器人 QQ 号
        """

    def set_group_special_title(
            self, *,
            group_id: int,
            user_id: int,
            special_title: str = '',
            duration: int = -1,
            self_id: Optional[int] = None,
    ) -> Union[Awaitable[None], None]:
        """
        设置群组专属头衔。

        Args:
            group_id: 群号
            user_id: 要设置的 QQ 号
            special_title: 专属头衔，不填或空字符串表示删除专属头衔
            duration: 专属头衔有效期，单位秒，-1 表示永久，不过此项似乎没有效果，可能是只有某些特殊的时间长度有效，有待测试
            self_id: 机器人 QQ 号
        """

    def set_friend_add_request(
            self, *,
            flag: str,
            approve: bool = True,
            remark: str = '',
            self_id: Optional[int] = None,
    ) -> Union[Awaitable[None], None]:
        """
        处理加好友请求。

        Args:
            flag: 加好友请求的 flag（需从上报的数据中获得）
            approve: 是否同意请求
            remark: 添加后的好友备注（仅在同意时有效）
            self_id: 机器人 QQ 号
        """

    def set_group_add_request(
            self, *,
            flag: str,
            sub_type: str,
            approve: bool = True,
            reason: str = '',
            self_id: Optional[int] = None,
    ) -> Union[Awaitable[None], None]:
        """
        处理加群请求／邀请。

        Args:
            flag: 加群请求的 flag（需从上报的数据中获得）
            sub_type: `add` 或 `invite`，请求类型（需要和上报消息中的 `sub_type` 字段相符）
            approve: 是否同意请求／邀请
            reason: 拒绝理由（仅在拒绝时有效）
            self_id: 机器人 QQ 号
        """

    def get_login_info(
            self, *,
            self_id: Optional[int] = None,
    ) -> Union[Awaitable[_get_login_info_ret], _get_login_info_ret]:
        """
        获取登录号信息。

        Args:
            self_id: 机器人 QQ 号
        """

    def get_stranger_info(
            self, *,
            user_id: int,
            no_cache: bool = False,
            self_id: Optional[int] = None,
    ) -> Union[Awaitable[_get_stranger_info_ret], _get_stranger_info_ret]:
        """
        获取陌生人信息。

        Args:
            user_id: QQ 号
            no_cache: 是否不使用缓存（使用缓存可能更新不及时，但响应更快）
            self_id: 机器人 QQ 号
        """

    def get_friend_list(
            self, *,
            self_id: Optional[int] = None,
    ) -> Union[Awaitable[List[_get_friend_list_ret]], List[_get_friend_list_ret]]:
        """
        获取好友列表。

        Args:
            self_id: 机器人 QQ 号
        """

    def get_group_info(
            self, *,
            group_id: int,
            no_cache: bool = False,
            self_id: Optional[int] = None,
    ) -> Union[Awaitable[_get_group_info_ret], _get_group_info_ret]:
        """
        获取群信息。

        Args:
            group_id: 群号
            no_cache: 是否不使用缓存（使用缓存可能更新不及时，但响应更快）
            self_id: 机器人 QQ 号
        """

    def get_group_list(
            self, *,
            self_id: Optional[int] = None,
    ) -> Union[Awaitable[List[_get_group_list_ret]], List[_get_group_list_ret]]:
        """
        获取群列表。

        Args:
            self_id: 机器人 QQ 号
        """

    def get_group_member_info(
            self, *,
            group_id: int,
            user_id: int,
            no_cache: bool = False,
            self_id: Optional[int] = None,
    ) -> Union[Awaitable[_get_group_member_info_ret], _get_group_member_info_ret]:
        """
        获取群成员信息。

        Args:
            group_id: 群号
            user_id: QQ 号
            no_cache: 是否不使用缓存（使用缓存可能更新不及时，但响应更快）
            self_id: 机器人 QQ 号
        """

    def get_group_member_list(
            self, *,
            group_id: int,
            self_id: Optional[int] = None,
    ) -> Union[Awaitable[List[_get_group_member_list_ret]], List[_get_group_member_list_ret]]:
        """
        获取群成员列表。

        Args:
            group_id: 群号
            self_id: 机器人 QQ 号
        """

    def get_group_honor_info(
            self, *,
            group_id: int,
            type: str,
            self_id: Optional[int] = None,
    ) -> Union[Awaitable[_get_group_honor_info_ret], _get_group_honor_info_ret]:
        """
        获取群荣誉信息。

        Args:
            group_id: 群号
            type: 要获取的群荣誉类型，可传入 `talkative` `performer` `legend` `strong_newbie` `emotion` 以分别获取单个类型的群荣誉数据，或传入 `all` 获取所有数据
            self_id: 机器人 QQ 号
        """

    def get_cookies(
            self, *,
            domain: str = '',
            self_id: Optional[int] = None,
    ) -> Union[Awaitable[_get_cookies_ret], _get_cookies_ret]:
        """
        获取 Cookies。

        Args:
            domain: 需要获取 cookies 的域名
            self_id: 机器人 QQ 号
        """

    def get_csrf_token(
            self, *,
            self_id: Optional[int] = None,
    ) -> Union[Awaitable[_get_csrf_token_ret], _get_csrf_token_ret]:
        """
        获取 CSRF Token。

        Args:
            self_id: 机器人 QQ 号
        """

    def get_credentials(
            self, *,
            domain: str = '',
            self_id: Optional[int] = None,
    ) -> Union[Awaitable[_get_credentials_ret], _get_credentials_ret]:
        """
        获取 QQ 相关接口凭证。

        Args:
            domain: 需要获取 cookies 的域名
            self_id: 机器人 QQ 号
        """

    def get_record(
            self, *,
            file: str,
            out_format: str,
            self_id: Optional[int] = None,
    ) -> Union[Awaitable[_get_record_ret], _get_record_ret]:
        """
        获取语音。

        Args:
            file: 收到的语音文件名（消息段的 `file` 参数），如 `0B38145AA44505000B38145AA4450500.silk`
            out_format: 要转换到的格式，目前支持 `mp3`、`amr`、`wma`、`m4a`、`spx`、`ogg`、`wav`、`flac`
            self_id: 机器人 QQ 号
        """

    def get_image(
            self, *,
            file: str,
            self_id: Optional[int] = None,
    ) -> Union[Awaitable[_get_image_ret], _get_image_ret]:
        """
        获取图片。

        Args:
            file: 收到的图片文件名（消息段的 `file` 参数），如 `6B4DE3DFD1BD271E3297859D41C530F5.jpg`
            self_id: 机器人 QQ 号
        """

    def can_send_image(
            self, *,
            self_id: Optional[int] = None,
    ) -> Union[Awaitable[_can_send_image_ret], _can_send_image_ret]:
        """
        检查是否可以发送图片。

        Args:
            self_id: 机器人 QQ 号
        """

    def can_send_record(
            self, *,
            self_id: Optional[int] = None,
    ) -> Union[Awaitable[_can_send_record_ret], _can_send_record_ret]:
        """
        检查是否可以发送语音。

        Args:
            self_id: 机器人 QQ 号
        """

    def get_status(
            self, *,
            self_id: Optional[int] = None,
    ) -> Union[Awaitable[_get_status_ret], _get_status_ret]:
        """
        获取运行状态。

        Args:
            self_id: 机器人 QQ 号
        """

    def get_version_info(
            self, *,
            self_id: Optional[int] = None,
    ) -> Union[Awaitable[_get_version_info_ret], _get_version_info_ret]:
        """
        获取版本信息。

        Args:
            self_id: 机器人 QQ 号
        """

    def set_restart(
            self, *,
            delay: int = 0,
            self_id: Optional[int] = None,
    ) -> Union[Awaitable[None], None]:
        """
        重启 OneBot 实现。

        Args:
            delay: 要延迟的毫秒数，如果默认情况下无法重启，可以尝试设置延迟为 2000 左右
            self_id: 机器人 QQ 号
        """

    def clean_cache(
            self, *,
            self_id: Optional[int] = None,
    ) -> Union[Awaitable[None], None]:
        """
        清理缓存。

        Args:
            self_id: 机器人 QQ 号
        """


# definition to avoid union return types
class AsyncApi(Api):
    async def call_action(
            self,
            action: str,
            **params,
    ) -> Any: ...

    async def send_private_msg(
            self, *,
            user_id: int,
            message: Message_T,
            auto_escape: bool = False,
            self_id: Optional[int] = None,
    ) -> _send_private_msg_ret: ...

    async def send_group_msg(
            self, *,
            group_id: int,
            message: Message_T,
            auto_escape: bool = False,
            self_id: Optional[int] = None,
    ) -> _send_group_msg_ret: ...

    async def send_msg(
            self, *,
            message_type: Optional[str] = None,
            user_id: Optional[int] = None,
            group_id: Optional[int] = None,
            message: Message_T,
            auto_escape: bool = False,
            self_id: Optional[int] = None,
    ) -> _send_msg_ret: ...

    async def delete_msg(
            self, *,
            message_id: int,
            self_id: Optional[int] = None,
    ) -> None: ...

    async def get_msg(
            self, *,
            message_id: int,
            self_id: Optional[int] = None,
    ) -> _get_msg_ret: ...

    async def get_forward_msg(
            self, *,
            id: str,
            self_id: Optional[int] = None,
    ) -> _get_forward_msg_ret: ...

    async def send_like(
            self, *,
            user_id: int,
            times: int = 1,
            self_id: Optional[int] = None,
    ) -> None: ...

    async def set_group_kick(
            self, *,
            group_id: int,
            user_id: int,
            reject_add_request: bool = False,
            self_id: Optional[int] = None,
    ) -> None: ...

    async def set_group_ban(
            self, *,
            group_id: int,
            user_id: int,
            duration: int = 30 * 60,
            self_id: Optional[int] = None,
    ) -> None: ...

    async def set_group_anonymous_ban(
            self, *,
            group_id: int,
            anonymous: Optional[Dict[str, Any]] = None,
            anonymous_flag: Optional[str] = None,
            duration: int = 30 * 60,
            self_id: Optional[int] = None,
    ) -> None: ...

    async def set_group_whole_ban(
            self, *,
            group_id: int,
            enable: bool = True,
            self_id: Optional[int] = None,
    ) -> None: ...

    async def set_group_admin(
            self, *,
            group_id: int,
            user_id: int,
            enable: bool = True,
            self_id: Optional[int] = None,
    ) -> None: ...

    async def set_group_anonymous(
            self, *,
            group_id: int,
            enable: bool = True,
            self_id: Optional[int] = None,
    ) -> None: ...

    async def set_group_card(
            self, *,
            group_id: int,
            user_id: int,
            card: str = '',
            self_id: Optional[int] = None,
    ) -> None: ...

    async def set_group_name(
            self, *,
            group_id: int,
            group_name: str,
            self_id: Optional[int] = None,
    ) -> None: ...

    async def set_group_leave(
            self, *,
            group_id: int,
            is_dismiss: bool = False,
            self_id: Optional[int] = None,
    ) -> None: ...

    async def set_group_special_title(
            self, *,
            group_id: int,
            user_id: int,
            special_title: str = '',
            duration: int = -1,
            self_id: Optional[int] = None,
    ) -> None: ...

    async def set_friend_add_request(
            self, *,
            flag: str,
            approve: bool = True,
            remark: str = '',
            self_id: Optional[int] = None,
    ) -> None: ...

    async def set_group_add_request(
            self, *,
            flag: str,
            sub_type: str,
            approve: bool = True,
            reason: str = '',
            self_id: Optional[int] = None,
    ) -> None: ...

    async def get_login_info(
            self, *,
            self_id: Optional[int] = None,
    ) -> _get_login_info_ret: ...

    async def get_stranger_info(
            self, *,
            user_id: int,
            no_cache: bool = False,
            self_id: Optional[int] = None,
    ) -> _get_stranger_info_ret: ...

    async def get_friend_list(
            self, *,
            self_id: Optional[int] = None,
    ) -> List[_get_friend_list_ret]: ...

    async def get_group_info(
            self, *,
            group_id: int,
            no_cache: bool = False,
            self_id: Optional[int] = None,
    ) -> _get_group_info_ret: ...

    async def get_group_list(
            self, *,
            self_id: Optional[int] = None,
    ) -> List[_get_group_list_ret]: ...

    async def get_group_member_info(
            self, *,
            group_id: int,
            user_id: int,
            no_cache: bool = False,
            self_id: Optional[int] = None,
    ) -> _get_group_member_info_ret: ...

    async def get_group_member_list(
            self, *,
            group_id: int,
            self_id: Optional[int] = None,
    ) -> List[_get_group_member_list_ret]: ...

    async def get_group_honor_info(
            self, *,
            group_id: int,
            type: str,
            self_id: Optional[int] = None,
    ) -> _get_group_honor_info_ret: ...

    async def get_cookies(
            self, *,
            domain: str = '',
            self_id: Optional[int] = None,
    ) -> _get_cookies_ret: ...

    async def get_csrf_token(
            self, *,
            self_id: Optional[int] = None,
    ) -> _get_csrf_token_ret: ...

    async def get_credentials(
            self, *,
            domain: str = '',
            self_id: Optional[int] = None,
    ) -> _get_credentials_ret: ...

    async def get_record(
            self, *,
            file: str,
            out_format: str,
            self_id: Optional[int] = None,
    ) -> _get_record_ret: ...

    async def get_image(
            self, *,
            file: str,
            self_id: Optional[int] = None,
    ) -> _get_image_ret: ...

    async def can_send_image(
            self, *,
            self_id: Optional[int] = None,
    ) -> _can_send_image_ret: ...

    async def can_send_record(
            self, *,
            self_id: Optional[int] = None,
    ) -> _can_send_record_ret: ...

    async def get_status(
            self, *,
            self_id: Optional[int] = None,
    ) -> _get_status_ret: ...

    async def get_version_info(
            self, *,
            self_id: Optional[int] = None,
    ) -> _get_version_info_ret: ...

    async def set_restart(
            self, *,
            delay: int = 0,
            self_id: Optional[int] = None,
    ) -> None: ...

    async def clean_cache(
            self, *,
            self_id: Optional[int] = None,
    ) -> None: ...


# definition to avoid union return types
class SyncApi(Api):
    def call_action(
            self,
            action: str,
            **params,
    ) -> Any: ...

    def send_private_msg(
            self, *,
            user_id: int,
            message: Message_T,
            auto_escape: bool = False,
            self_id: Optional[int] = None,
    ) -> _send_private_msg_ret: ...

    def send_group_msg(
            self, *,
            group_id: int,
            message: Message_T,
            auto_escape: bool = False,
            self_id: Optional[int] = None,
    ) -> _send_group_msg_ret: ...

    def send_msg(
            self, *,
            message_type: Optional[str] = None,
            user_id: Optional[int] = None,
            group_id: Optional[int] = None,
            message: Message_T,
            auto_escape: bool = False,
            self_id: Optional[int] = None,
    ) -> _send_msg_ret: ...

    def delete_msg(
            self, *,
            message_id: int,
            self_id: Optional[int] = None,
    ) -> None: ...

    def get_msg(
            self, *,
            message_id: int,
            self_id: Optional[int] = None,
    ) -> _get_msg_ret: ...

    def get_forward_msg(
            self, *,
            id: str,
            self_id: Optional[int] = None,
    ) -> _get_forward_msg_ret: ...

    def send_like(
            self, *,
            user_id: int,
            times: int = 1,
            self_id: Optional[int] = None,
    ) -> None: ...

    def set_group_kick(
            self, *,
            group_id: int,
            user_id: int,
            reject_add_request: bool = False,
            self_id: Optional[int] = None,
    ) -> None: ...

    def set_group_ban(
            self, *,
            group_id: int,
            user_id: int,
            duration: int = 30 * 60,
            self_id: Optional[int] = None,
    ) -> None: ...

    def set_group_anonymous_ban(
            self, *,
            group_id: int,
            anonymous: Optional[Dict[str, Any]] = None,
            anonymous_flag: Optional[str] = None,
            duration: int = 30 * 60,
            self_id: Optional[int] = None,
    ) -> None: ...

    def set_group_whole_ban(
            self, *,
            group_id: int,
            enable: bool = True,
            self_id: Optional[int] = None,
    ) -> None: ...

    def set_group_admin(
            self, *,
            group_id: int,
            user_id: int,
            enable: bool = True,
            self_id: Optional[int] = None,
    ) -> None: ...

    def set_group_anonymous(
            self, *,
            group_id: int,
            enable: bool = True,
            self_id: Optional[int] = None,
    ) -> None: ...

    def set_group_card(
            self, *,
            group_id: int,
            user_id: int,
            card: str = '',
            self_id: Optional[int] = None,
    ) -> None: ...

    def set_group_name(
            self, *,
            group_id: int,
            group_name: str,
            self_id: Optional[int] = None,
    ) -> None: ...

    def set_group_leave(
            self, *,
            group_id: int,
            is_dismiss: bool = False,
            self_id: Optional[int] = None,
    ) -> None: ...

    def set_group_special_title(
            self, *,
            group_id: int,
            user_id: int,
            special_title: str = '',
            duration: int = -1,
            self_id: Optional[int] = None,
    ) -> None: ...

    def set_friend_add_request(
            self, *,
            flag: str,
            approve: bool = True,
            remark: str = '',
            self_id: Optional[int] = None,
    ) -> None: ...

    def set_group_add_request(
            self, *,
            flag: str,
            sub_type: str,
            approve: bool = True,
            reason: str = '',
            self_id: Optional[int] = None,
    ) -> None: ...

    def get_login_info(
            self, *,
            self_id: Optional[int] = None,
    ) -> _get_login_info_ret: ...

    def get_stranger_info(
            self, *,
            user_id: int,
            no_cache: bool = False,
            self_id: Optional[int] = None,
    ) -> _get_stranger_info_ret: ...

    def get_friend_list(
            self, *,
            self_id: Optional[int] = None,
    ) -> List[_get_friend_list_ret]: ...

    def get_group_info(
            self, *,
            group_id: int,
            no_cache: bool = False,
            self_id: Optional[int] = None,
    ) -> _get_group_info_ret: ...

    def get_group_list(
            self, *,
            self_id: Optional[int] = None,
    ) -> List[_get_group_list_ret]: ...

    def get_group_member_info(
            self, *,
            group_id: int,
            user_id: int,
            no_cache: bool = False,
            self_id: Optional[int] = None,
    ) -> _get_group_member_info_ret: ...

    def get_group_member_list(
            self, *,
            group_id: int,
            self_id: Optional[int] = None,
    ) -> List[_get_group_member_list_ret]: ...

    def get_group_honor_info(
            self, *,
            group_id: int,
            type: str,
            self_id: Optional[int] = None,
    ) -> _get_group_honor_info_ret: ...

    def get_cookies(
            self, *,
            domain: str = '',
            self_id: Optional[int] = None,
    ) -> _get_cookies_ret: ...

    def get_csrf_token(
            self, *,
            self_id: Optional[int] = None,
    ) -> _get_csrf_token_ret: ...

    def get_credentials(
            self, *,
            domain: str = '',
            self_id: Optional[int] = None,
    ) -> _get_credentials_ret: ...

    def get_record(
            self, *,
            file: str,
            out_format: str,
            self_id: Optional[int] = None,
    ) -> _get_record_ret: ...

    def get_image(
            self, *,
            file: str,
            self_id: Optional[int] = None,
    ) -> _get_image_ret: ...

    def can_send_image(
            self, *,
            self_id: Optional[int] = None,
    ) -> _can_send_image_ret: ...

    def can_send_record(
            self, *,
            self_id: Optional[int] = None,
    ) -> _can_send_record_ret: ...

    def get_status(
            self, *,
            self_id: Optional[int] = None,
    ) -> _get_status_ret: ...

    def get_version_info(
            self, *,
            self_id: Optional[int] = None,
    ) -> _get_version_info_ret: ...

    def set_restart(
            self, *,
            delay: int = 0,
            self_id: Optional[int] = None,
    ) -> None: ...

    def clean_cache(
            self, *,
            self_id: Optional[int] = None,
    ) -> None: ...
