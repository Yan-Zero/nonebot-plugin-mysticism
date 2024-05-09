import yaml
import pathlib
import random
from nonebot import get_plugin_config
from nonebot.adapters import Bot, Event
from nonebot.internal.permission import Permission
from nonebot.adapters.onebot.v11.event import GroupMessageEvent as V11G
from PIL import Image
from nonebot import on_command
from nonebot.params import CommandArg
from nonebot.params import ArgPlainText
from nonebot.adapters.onebot.v11.message import Message as V11Msg
from nonebot.adapters.onebot.v11.message import MessageSegment as V11Seg
from nonebot.internal.adapter import Bot
from nonebot.matcher import Matcher
from nonebot.typing import T_State
from .config import Config
from .utils import send_image_as_bytes
from . import tarot_uitls


FORMATIONS = None
FORMATIONS_ALIAS = None
with open(
    pathlib.Path(__file__).parent / "tarot_formations.yaml", encoding="utf-8"
) as f:
    data = yaml.load(f, yaml.FullLoader)
    FORMATIONS = data["formations"]
    FORMATIONS_ALIAS = data["alias"]

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

tarot = on_command("tarot", priority=5, block=True, force_whitespace=True)
# /tarot [formations]


@tarot.handle()
async def _(bot: Bot, matcher: Matcher, state: T_State, args=CommandArg()):
    result = ""
    if formations := args.extract_plain_text().strip():
        if formations in FORMATIONS_ALIAS:
            formations = FORMATIONS_ALIAS[formations]

    if formations not in FORMATIONS:
        formations = random.choice(list(FORMATIONS.keys()))
        result = "牌阵没有找到喵。\n"

    state["formations"] = FORMATIONS[formations]
    state["cards_num"] = state["formations"]["cards_num"]
    state["cnumber"] = []
    state["tarot_theme"] = random.choice(tarot_uitls.THEME)
    state["stack_card"] = tarot_uitls.TAROT_STACK.copy()
    random.shuffle(state["stack_card"])
    # 先洗牌更有仪式感（x）

    result += f"目前抽取到了：{formations}\n"
    result += f'共计需要选择 {state["cards_num"]} 张牌。\n'
    result += f'所以接下来请发送 {state["cards_num"]} 个 1-78 的数字。\n'
    result += f"(注：其实不是1-78也行，我取模了（？）)\n"
    result += f'(注：可以一次性发多个，例如"1 114514 3 8")\n'
    await tarot.send(result)


@tarot.got("nums", prompt="请输入数字")
async def _(bot: Bot, event, state: T_State, nums=ArgPlainText()):
    if nums.strip() == "cancel":
        tarot.finish("已取消占卜🔮")
    try:
        nums = list(
            filter(
                lambda x: x not in state["cnumber"],
                map(lambda x: (x - 1 % 78) + 1, map(int, nums.split())),
            )
        )
    except Exception as ex:
        await tarot.reject(
            f"似乎，这些不只是数字……\n你还得再输入 {state['cards_num']} 个数字"
        )
    state["cnumber"].extend(nums)
    state["cards_num"] -= len(nums)
    if state["cards_num"] > 0:
        await tarot.reject(f"你还得再输入 {state['cards_num']} 个数字")

    formation = state["formations"]
    random.seed(sum(state["cnumber"]) + random.random())
    representations = random.choice(formation.get("representations"))

    message = []
    for i in range(formation["cards_num"]):
        content = [V11Seg.text(f"第{i+1}张牌「{representations[i]}」\n")]
        _id = state["stack_card"][state["cnumber"][i]]
        img = Image.open(await send_image_as_bytes(state["tarot_theme"][_id].face_url))

        postfix = f"「{tarot_uitls.CN_Name[_id]} 正位」"
        if random.randint(0, 1) == 1:
            img.transpose(Image.ROTATE_180)
            postfix = f"「{tarot_uitls.CN_Name[_id]} 逆位」"
        content.append(V11Seg.image(img.tobytes()))
        content.append(V11Seg.text(postfix))

        message.append(
            {
                "type": "node",
                "data": {
                    "uin": str(event.get_user_id()),
                    "name": representations[i],
                    "content": content,
                },
            },
        )

    random.seed()
    res_id = await bot.call_api("send_forward_msg", messages=message)
    await tarot.finish(V11Seg.forward(res_id))
