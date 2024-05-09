from nonebot import get_plugin_config
from nonebot.internal.permission import Permission
from nonebot.adapters.onebot.v11.event import GroupMessageEvent as V11G
from nonebot.adapters import Bot, Event
from .config import Config

config = get_plugin_config(Config)


class BlackGroup(Permission):

    __slots__ = ()

    def __repr__(self) -> str:
        return "BlackGroup()"

    async def __call__(self, bot: Bot, event: Event) -> bool:
        if not isinstance(event, V11G):
            return True
        try:
            group_id = str(event.group_id)
        except Exception:
            return True
        return group_id not in config.black_group


BLACK_GROUP = Permission(BlackGroup())
