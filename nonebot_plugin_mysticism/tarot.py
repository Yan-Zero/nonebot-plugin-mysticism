import yaml
import pathlib
import random
from nonebot.adapters import Bot
from PIL import Image
from nonebot import on_command
from nonebot.params import CommandArg
from nonebot.params import ArgPlainText
from nonebot.adapters.onebot.v11.message import Message as V11Msg
from nonebot.adapters.onebot.v11.event import GroupMessageEvent as V11G
from nonebot.adapters.onebot.v11.message import MessageSegment as V11Seg
from nonebot.internal.adapter import Bot
from nonebot.matcher import Matcher
from nonebot.typing import T_State
from io import BytesIO
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

s_tarot = on_command("s.tarot", priority=5, block=True, force_whitespace=True)
tarot = on_command("tarot", priority=5, block=True, force_whitespace=True)


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
    result += f'所以接下来请发送 {state["cards_num"]} 个 1-78 的数字。\n'
    result += f"(注：其实不是1-78也行，我取模了（？）)\n"
    result += f'(注：可以一次性发多个，例如"1 114514 3 8")'
    await tarot.send(result)


@tarot.got("nums", prompt="请输入数字")
async def _(bot: Bot, event, state: T_State, nums=ArgPlainText()):
    if nums.strip() == "cancel":
        tarot.finish("已取消占卜🔮")
    try:
        sep = None
        if "," in nums:
            sep = ","
        elif "." in nums:
            sep = "."
        for i in map(lambda x: x % 78, map(int, nums.split(sep=sep))):
            if i in state["cnumber"]:
                continue
            state["cnumber"].append(i)
    except:
        await tarot.reject(
            f"似乎，这些不只是数字……\n你还得再输入 {state['cards_num']} 个数字"
        )

    if state["formations"]["cards_num"] > len(state["cnumber"]):
        await tarot.reject(f"你还得再输入 {state['cards_num']} 个数字")

    formation = state["formations"]
    random.seed(sum(state["cnumber"]) + random.random())
    representations = random.choice(formation.get("representations"))
    meanings = []
    message = []
    for i in range(formation["cards_num"]):
        content = [V11Seg.text(f"第{i+1}张牌「{representations[i]}」\n")]
        _id = state["stack_card"][state["cnumber"][i]]
        img = Image.open(await send_image_as_bytes(state["tarot_theme"][_id].face_url))
        if random.randint(0, 1) == 1:
            img = img.transpose(Image.ROTATE_180)
            postfix = f"「{tarot_uitls.CN_Name[_id]} 逆位」"
            meanings.append(
                {
                    "type": "node",
                    "data": {
                        "uin": str(event.get_user_id()),
                        "name": postfix,
                        "content": postfix
                        + "\n"
                        + tarot_uitls.TAROT_KEYWORDS[_id]["rev"],
                    },
                },
            )
        else:
            postfix = f"「{tarot_uitls.CN_Name[_id]} 正位」"
            meanings.append(
                {
                    "type": "node",
                    "data": {
                        "uin": str(event.get_user_id()),
                        "name": postfix,
                        "content": postfix
                        + "\n"
                        + tarot_uitls.TAROT_KEYWORDS[_id]["up"],
                    },
                },
            )

        image = BytesIO()
        img.convert("RGB").save(image, "JPEG")
        content.append(V11Seg.image(image))
        content.append(V11Seg.text(postfix))

        message.append(
            {
                "type": "node",
                "data": {
                    "uin": str(event.get_user_id()),
                    "name": postfix,
                    "content": content,
                },
            },
        )

    random.seed()
    message.extend(meanings)
    # group
    if isinstance(event, V11G):
        await bot.call_api(
            "send_group_forward_msg", group_id=event.group_id, messages=message
        )
    else:
        await tarot.finish(
            V11Seg.forward(await bot.call_api("send_forward_msg", messages=message))
        )


NUM2ID = {
    "0": "major",
    "1": "cups",
    "2": "pentacles",
    "3": "swords",
    "4": "wands",
    "major": "major",
    "cups": "cups",
    "pentacles": "pentacles",
    "swords": "swords",
    "wands": "wands",
}


@s_tarot.handle()
async def _(bot: Bot, args=CommandArg()):
    args = args.extract_plain_text().strip()
    try:
        args = NUM2ID.get(args, "")
    except:
        args = ""

    _id = random.choice(
        list(filter(lambda x: x.startswith(args), tarot_uitls.TAROT_STACK))
    )

    theme = random.choice(tarot_uitls.THEME)
    img = Image.open(await send_image_as_bytes(theme[_id].face_url))
    postfix = f"「{tarot_uitls.CN_Name[_id]} 正位」"
    if random.randint(0, 1) == 1:
        img = img.transpose(Image.ROTATE_180)
        postfix = f"「{tarot_uitls.CN_Name[_id]} 逆位」"
    image = BytesIO()
    img.convert("RGB").save(image, "JPEG")

    await s_tarot.finish([V11Seg.image(image), V11Seg.text(postfix)])
