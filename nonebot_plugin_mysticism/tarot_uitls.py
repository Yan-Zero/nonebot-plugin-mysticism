import urllib.parse
import yaml
import pathlib
import urllib


class Card:
    """
    Represents a generic card with a prefix, postfix, and optional name.

    Attributes:
        prefix (str): The prefix part of the card's URL.
        postfix (str): The postfix part of the card's URL.
        name (str, optional): The name of the card. Defaults to None.
    """

    prefix: str
    postfix: str
    name: str

    def __init__(self, prefix: str, postfix: str, name: str = None) -> None:
        """
        Initializes a Card instance with the provided prefix, postfix, and optional name.

        Parameters:
            prefix (str): The prefix part of the card's URL.
            postfix (str): The postfix part of the card's URL.
            name (str, optional): The name of the card. Defaults to None.
        """
        if name:
            self.name = name
        self.prefix = prefix
        self.postfix = postfix

    @property
    def face_url(self) -> str:
        """
        Generates the URL of the card's face image.

        Returns:
            str: The URL of the card's face image.
        """
        if self.prefix:
            return urllib.parse.urljoin(self.prefix, self.postfix)
        return self.postfix


class Tarot:
    """
    Represents a Tarot deck, consisting of Major Arcana and Minor Arcana.
    """

    class MinorArcana:
        """
        Represents a set of Minor Arcana cards belonging to a specific suit (e.g., CUPS, PENTACLES, SWORDS, WANDS).
        """

        c_type: str
        ace: Card
        two: Card
        three: Card
        four: Card
        five: Card
        six: Card
        seven: Card
        eight: Card
        nine: Card
        ten: Card
        page: Card
        knight: Card
        queen: Card
        king: Card

        def __init__(self, c_type: str, cards: list[Card] = None) -> None:
            """
            Initializes a MinorArcana instance.

            Parameters:
                c_type (str): The type of Minor Arcana (e.g., Cups, Pentacles, Swords, Wands).
                cards (list[Card], optional): A list of Card instances representing the cards of the Minor Arcana.
                    Defaults to None.
            """
            self.c_type = c_type
            if cards:
                self.ace = cards[0]
                self.two = cards[1]
                self.three = cards[2]
                self.four = cards[3]
                self.five = cards[4]
                self.six = cards[5]
                self.seven = cards[6]
                self.eight = cards[7]
                self.nine = cards[8]
                self.ten = cards[9]
                self.page = cards[10]
                self.knight = cards[11]
                self.queen = cards[12]
                self.king = cards[13]

    class MajorArcana:
        """
        Represents a set of Major Arcana cards.
        """

        fool: Card
        magician: Card
        high_priestess: Card
        empress: Card
        emperor: Card
        hierophant: Card
        lovers: Card
        chariot: Card
        strength: Card
        hermit: Card
        wheel_of_fortune: Card
        justice: Card
        hanged_man: Card
        death: Card
        temperance: Card
        devil: Card
        tower: Card
        star: Card
        moon: Card
        sun: Card
        judgement: Card
        world: Card

        def __init__(self, cards: list[Card]) -> None:
            """
            Initializes a MajorArcana instance.

            Parameters:
                cards (list[Card]): A list of Card instances representing the cards of the Major Arcana.
            """
            self.fool = cards[0]
            self.magician = cards[1]
            self.high_priestess = cards[2]
            self.empress = cards[3]
            self.emperor = cards[4]
            self.hierophant = cards[5]
            self.lovers = cards[6]
            self.chariot = cards[7]
            self.strength = cards[8]
            self.hermit = cards[9]
            self.wheel_of_fortune = cards[10]
            self.justice = cards[11]
            self.hanged_man = cards[12]
            self.death = cards[13]
            self.temperance = cards[14]
            self.devil = cards[15]
            self.tower = cards[16]
            self.star = cards[17]
            self.moon = cards[18]
            self.sun = cards[19]
            self.judgement = cards[20]
            self.world = cards[21]

    name: str
    cups: MinorArcana
    pentacles: MinorArcana
    swords: MinorArcana
    wands: MinorArcana
    major: MajorArcana

    def __init__(self, name: str) -> None:
        """
        Initializes a Tarot instance.

        Parameters:
            name (str): The name of the Tarot deck.
        """
        self.name = name

    def __getitem__(self, key: str):
        if "." in key:
            keys = key.split(".")
            return getattr(getattr(self, keys[0]), keys[1])
        else:
            return getattr(self, key)


DEFAULT = {}


def get_tarot(path: str | pathlib.Path) -> Tarot:
    """
    Loads a Tarot deck from a YAML file.

    Parameters:
        path (str): The path to the YAML file containing Tarot data.

    Returns:
        Tarot: An instance of the Tarot class representing the loaded deck.
    """
    with open(path, mode="r", encoding="utf-8") as f:
        data = yaml.load(f, Loader=yaml.FullLoader)
        prefix = data.get("prefix", None)
        result = Tarot(data["name"])
        result.major = Tarot.MajorArcana(
            [Card(prefix, i) for i in data["major_arcana"]]
        )

        def ma(name: str) -> str | None:
            """
            Loads Minor Arcana cards for a given suit.

            Parameters:
                name (str): The name of the suit.

            Returns:
                str | None: Returns None if loading is successful, otherwise returns the name of the suit.
            """
            if name not in data:
                return name
            setattr(
                result,
                name,
                Tarot.MinorArcana(name.upper(), [Card(prefix, i) for i in data[name]]),
            )
            return None

        for i in filter(lambda x: x, map(ma, ["cups", "pentacles", "swords", "wands"])):
            setattr(result, i, DEFAULT[i])  # type: ignore

        return result


BILIBILI = get_tarot(pathlib.Path(__file__).parent / "tarot_theme" / "bilibili.yaml")
DEFAULT["cups"] = BILIBILI.cups
DEFAULT["pentacles"] = BILIBILI.pentacles
DEFAULT["swords"] = BILIBILI.swords
DEFAULT["wands"] = BILIBILI.wands

WAITE = get_tarot(pathlib.Path(__file__).parent / "tarot_theme" / "waite.yaml")
BULE_ARCHIVE = get_tarot(
    pathlib.Path(__file__).parent / "tarot_theme" / "blue_archive.yaml"
)


THEME = [BILIBILI, BULE_ARCHIVE, WAITE]

TAROT_STACK = [
    "cups.ace",
    "cups.two",
    "cups.three",
    "cups.four",
    "cups.five",
    "cups.six",
    "cups.seven",
    "cups.eight",
    "cups.nine",
    "cups.ten",
    "cups.page",
    "cups.knight",
    "cups.queen",
    "cups.king",
    "pentacles.ace",
    "pentacles.two",
    "pentacles.three",
    "pentacles.four",
    "pentacles.five",
    "pentacles.six",
    "pentacles.seven",
    "pentacles.eight",
    "pentacles.nine",
    "pentacles.ten",
    "pentacles.page",
    "pentacles.knight",
    "pentacles.queen",
    "pentacles.king",
    "swords.ace",
    "swords.two",
    "swords.three",
    "swords.four",
    "swords.five",
    "swords.six",
    "swords.seven",
    "swords.eight",
    "swords.nine",
    "swords.ten",
    "swords.page",
    "swords.knight",
    "swords.queen",
    "swords.king",
    "wands.ace",
    "wands.two",
    "wands.three",
    "wands.four",
    "wands.five",
    "wands.six",
    "wands.seven",
    "wands.eight",
    "wands.nine",
    "wands.ten",
    "wands.page",
    "wands.knight",
    "wands.queen",
    "wands.king",
    "major.fool",
    "major.magician",
    "major.high_priestess",
    "major.empress",
    "major.emperor",
    "major.hierophant",
    "major.lovers",
    "major.chariot",
    "major.strength",
    "major.hermit",
    "major.wheel_of_fortune",
    "major.justice",
    "major.hanged_man",
    "major.death",
    "major.temperance",
    "major.devil",
    "major.tower",
    "major.star",
    "major.moon",
    "major.sun",
    "major.judgement",
    "major.world",
]

CN_Name = {
    "cups.ace": "圣杯·一",
    "cups.two": "圣杯·二",
    "cups.three": "圣杯·三",
    "cups.four": "圣杯·四",
    "cups.five": "圣杯·五",
    "cups.six": "圣杯·六",
    "cups.seven": "圣杯·七",
    "cups.eight": "圣杯·八",
    "cups.nine": "圣杯·九",
    "cups.ten": "圣杯·十",
    "cups.page": "圣杯·侍从",
    "cups.knight": "圣杯·骑士",
    "cups.queen": "圣杯·皇后",
    "cups.king": "圣杯·国王",
    "pentacles.ace": "钱币·一",
    "pentacles.two": "钱币·二",
    "pentacles.three": "钱币·三",
    "pentacles.four": "钱币·四",
    "pentacles.five": "钱币·五",
    "pentacles.six": "钱币·六",
    "pentacles.seven": "钱币·七",
    "pentacles.eight": "钱币·八",
    "pentacles.nine": "钱币·九",
    "pentacles.ten": "钱币·十",
    "pentacles.page": "钱币·侍从",
    "pentacles.knight": "钱币·骑士",
    "pentacles.queen": "钱币·皇后",
    "pentacles.king": "钱币·国王",
    "swords.ace": "宝剑·一",
    "swords.two": "宝剑·二",
    "swords.three": "宝剑·三",
    "swords.four": "宝剑·四",
    "swords.five": "宝剑·五",
    "swords.six": "宝剑·六",
    "swords.seven": "宝剑·七",
    "swords.eight": "宝剑·八",
    "swords.nine": "宝剑·九",
    "swords.ten": "宝剑·十",
    "swords.page": "宝剑·侍从",
    "swords.knight": "宝剑·骑士",
    "swords.queen": "宝剑·皇后",
    "swords.king": "宝剑·国王",
    "wands.ace": "权杖·一",
    "wands.two": "权杖·二",
    "wands.three": "权杖·三",
    "wands.four": "权杖·四",
    "wands.five": "权杖·五",
    "wands.six": "权杖·六",
    "wands.seven": "权杖·七",
    "wands.eight": "权杖·八",
    "wands.nine": "权杖·九",
    "wands.ten": "权杖·十",
    "wands.page": "权杖·侍从",
    "wands.knight": "权杖·骑士",
    "wands.queen": "权杖·皇后",
    "wands.king": "权杖·国王",
    "major.fool": "愚者",
    "major.magician": "魔术师",
    "major.high_priestess": "女教皇",
    "major.empress": "皇后",
    "major.emperor": "皇帝",
    "major.hierophant": "教皇",
    "major.lovers": "恋人",
    "major.chariot": "战车",
    "major.strength": "力量",
    "major.hermit": "隐者",
    "major.wheel_of_fortune": "命运之轮",
    "major.justice": "正义",
    "major.hanged_man": "倒吊人",
    "major.death": "死神",
    "major.temperance": "节制",
    "major.devil": "恶魔",
    "major.tower": "塔",
    "major.star": "星星",
    "major.moon": "月亮",
    "major.sun": "太阳",
    "major.judgement": "审判",
    "major.world": "世界",
}

TAROT_KEYWORDS = {}
with open(pathlib.Path(__file__).parent / "tarot_keywords.yml", encoding="utf-8") as f:
    TAROT_KEYWORDS = yaml.load(f, yaml.FullLoader)
