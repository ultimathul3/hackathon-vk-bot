from enum import auto
from vkbottle import BaseStateGroup


class State(BaseStateGroup):
    EMPTY = auto()
    CATEGORY_SELECTION = auto()
    MENU_SELECTION = auto()
    FULL_NAME_INPUT = auto()
    PHONE_NUMBER_INPUT = auto()
    IMAGE_SELECTION = auto()
    ADDRESS_INPUT = auto()
    DESCRIPTION_INPUT = auto()