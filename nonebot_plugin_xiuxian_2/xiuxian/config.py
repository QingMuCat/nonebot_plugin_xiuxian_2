from typing import Set

from nonebot import get_driver
from pydantic.v1 import Field, BaseModel


class Config(BaseModel):
    disabled_plugins: Set[str] = Field(
        default_factory=set, alias="xiuxian_disabled_plugins"
    )
    priority: int = Field(2, alias="xiuxian_priority")


config = Config.parse_obj(get_driver().config)
priority = config.priority