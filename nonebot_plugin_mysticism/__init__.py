from nonebot import get_driver
from nonebot.plugin import PluginMetadata
from .tarot import tarot

__version__ = "0.1.1"
__plugin_meta__ = PluginMetadata(
    name="神秘学助手",
    description="虽然现在只有塔罗派相关的工具喵",
    usage="""相关指令：
/tarot [formations]
/s.tarot [type]
""",
    homepage="https://yan-zero.github.io/docs/coffee/mysticism",
    type="application",
    config=None,
    supported_adapters=["~onebot.v11"],
)
