from typing import List, Type

from abstract_cards import Card
from cards import Estate, Duchy, Province, Curse, Copper, Silver, Gold, Cellar, Market, Merchant, Militia, Mine, Moat, \
    Remodel, Smithy, Village, Workshop

COMMON = [
    # Victory cards and curses
    Estate,
    Duchy,
    Province,
    Curse,

    # Treasures
    Copper,
    Silver,
    Gold,
]

FIRST_GAME = COMMON + [Cellar, Market, Merchant, Militia, Mine, Moat, Remodel, Smithy, Village, Workshop]


def initialize_kingdom(kingdom: List[Type[Card]], num_players: int):
    return [card(num_players) for card in kingdom]