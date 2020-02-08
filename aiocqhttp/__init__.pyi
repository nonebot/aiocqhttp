# Stubs for api of aiocqhttp

from typing import (Any, Dict, List, Optional, Union)

Message_T = Union[str, Dict[str, Any], List[Dict[str, Any]]]
Context_T = Dict[str, Any]


class CQHttp:
    async def send_private_msg(
        self,
        user_id: int,
        message: Message_T,
        auto_escape: Optional[bool] = False,
        self_id: Optional[int] = None
    ) -> int: ...

    async def send_group_msg(
        self,
        group_id: int,
        message: Message_T,
        auto_escape: Optional[bool] = False,
        self_id: Optional[int] = None
    ) -> int: ...

    async def send_discuss_msg(
        self,
        discuss_id: int,
        message: Message_T,
        auto_escape: Optional[bool] = False,
        self_id: Optional[int] = None
    ) -> int: ...

    async def send_msg(
        self,
        message_type: Optional[str],
        user_id: Optional[int],
        group_id: Optional[int],
        discuss_id: Optional[int],
        message: Message_T,
        auto_escape: Optional[bool] = False,
        self_id: Optional[int] = None
    ) -> int: ...

    async def delete_msg(
        self,
        message_id: int,
        self_id: Optional[int] = None
    ) -> None: ...

    async def send_like(
        self,
        user_id: int,
        times: Optional[int] = 1,
        self_id: Optional[int] = None
    ) -> None: ...

    async def set_group_kick(
        self,
        group_id: int,
        user_id: int,
        reject_add_request: Optional[bool] = False,
        self_id: Optional[int] = None
    ) -> None: ...

    async def set_group_ban(
        self,
        group_id: int,
        user_id: int,
        duration: Optional[int] = 1800,
        self_id: Optional[int] = None
    ) -> None: ...

    async def set_group_anonymous_ban(
        self,
        group_id: int,
        anonymous: Optional[Context_T] = None,
        anonymous_flag: Optional[str] = None,
        flag: Optional[str] = None,
        self_id: Optional[int] = None
    ) -> None: ...

    async def set_group_whole_ban(
        self,
        group_id: int,
        enable: Optional[bool] = True,
        self_id: Optional[int] = None
    ) -> None: ...

    async def set_group_admin(
        self,
        group_id: int,
        user_id: int,
        enable: Optional[bool] = True,
        self_id: Optional[int] = None
    ) -> None: ...

    async def set_group_anonymous(
        self,
        group_id: int,
        enable: Optional[bool] = True,
        self_id: Optional[int] = None
    ) -> None: ...

    async def set_group_card(
        self,
        group_id: int,
        user_id: int,
        card: Optional[str] = None,
        self_id: Optional[int] = None
    ) -> None: ...

    async def set_group_leave(
        self,
        group_id: int,
        is_dismiss: Optional[bool] = False,
        self_id: Optional[int] = None
    ) -> None: ...

    async def set_group_special_title(
        self,
        group_id: int,
        user_id: int,
        special_title: Optional[str] = None,
        duration: Optional[int] = -1,
        self_id: Optional[int] = None
    ) -> None: ...

    async def set_discuss_leave(
        self,
        discuss_id: int,
        self_id: Optional[int] = None
    ) -> None: ...

    async def set_friend_add_request(
        self,
        flag: str,
        approve: Optional[bool] = True,
        remark: Optional[str] = None,
        self_id: Optional[int] = None
    ) -> None: ...

    async def set_group_add_request(
        self,
        flag: str,
        sub_type: Optional[str] = None,
        type: Optional[str] = None,
        approve: Optional[bool] = True,
        reason: Optional[str] = None,
        self_id: Optional[int] = None
    ) -> None: ...

    async def get_login_info(
        self,
        self_id: Optional[int] = None
    ) -> Dict[str, Any]: ...

    async def get_stranger_info(
        self,
        user_id: int,
        no_cache: Optional[bool] = False,
        self_id: Optional[int] = None
    ) -> Dict[str, Any]: ...

    async def get_friend_list(
        self,
        self_id: Optional[int] = None
    ) -> List[Dict[str, Any]]: ...

    async def get_group_list(
        self,
        self_id: Optional[int] = None
    ) -> List[Dict[str, Any]]: ...

    async def get_group_info(
        self,
        group_id: int,
        no_cache: Optional[bool] = False,
        self_id: Optional[int] = None
    ) -> Dict[str, Any]: ...

    async def get_group_member_info(
        self,
        group_id: int,
        user_id: int,
        no_cache: Optional[bool] = False,
        self_id: Optional[int] = None
    ) -> Dict[str, Any]: ...

    async def get_group_member_list(
        self,
        group_id: int,
        self_id: Optional[int] = None
    ) -> List[Dict[str, Any]]: ...

    async def get_cookies(
        self,
        domain: str,
        self_id: Optional[int] = None
    ) -> str: ...

    async def get_csrf_token(
        self,
        self_id: Optional[int] = None
    ) -> int: ...

    async def get_credentials(
        self,
        domain: str,
        self_id: Optional[int] = None
    ) -> Dict[str, Any]: ...

    async def get_record(
        self,
        file: str,
        out_format: str,
        full_path: Optional[bool] = False,
        self_id: Optional[int] = None
    ) -> Dict[str, str]: ...

    async def get_image(
        self,
        file: str,
        self_id: Optional[int] = None
    ) -> Dict[str, str]: ...

    async def can_send_image(
        self,
        self_id: Optional[int] = None
    ) -> Dict[str, bool]: ...

    async def can_send_record(
        self,
        self_id: Optional[int] = None
    ) -> Dict[str, bool]: ...

    async def get_status(
        self,
        self_id: Optional[int] = None
    ) -> Dict[str, Any]: ...

    async def get_version_info(
        self,
        self_id: Optional[int] = None
    ) -> Dict[str, Any]: ...

    async def set_restart_plugin(
        self,
        delay: Optional[int] = 0,
        self_id: Optional[int] = None
    ) -> None: ...

    async def clean_data_dir(
        self,
        data_dir: str,
        self_id: Optional[int] = None
    ) -> None: ...

    async def clean_plugin_log(
        self,
        self_id: Optional[int] = None
    ) -> None: ...

    async def _get_friend_list(
        self,
        flat: Optional[bool] = False,
        self_id: Optional[int] = None
    ) -> Union[List[Dict[str, Any]], Dict[str, Any]]: ...

    async def _get_group_info(
        self,
        group_id: int,
        self_id: Optional[int] = None
    ) -> Dict[str, Any]: ...

    async def _get_vip_info(
        self,
        user_id: int,
        self_id: Optional[int] = None
    ) -> Dict[str, Any]: ...

    async def _get_group_notice(
        self,
        group_id: int,
        self_id: Optional[int] = None
    ) -> List[Dict[str, Any]]: ...

    async def _send_group_notice(
        self,
        group_id: int,
        title: str,
        content: str,
        self_id: Optional[int] = None
    ) -> None: ...

    async def _set_restart(
        self,
        clean_log: Optional[bool] = False,
        clean_cache: Optional[bool] = False,
        clean_event: Optional[bool] = False,
        self_id: Optional[int] = None
    ) -> None: ...
