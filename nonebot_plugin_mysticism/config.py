from pydantic import BaseModel


class Config(BaseModel):
    tarot_theme: str = ""
    # 留空表示随机
