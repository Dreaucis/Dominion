from typing import List
from collections import Counter

from abstract_cards import Card
from player import Player

ACTION_PHASE = 'ACTION'
BUY_PHASE = 'BUY'


class SupplyPileIsEmpty(Exception):
    """ Raised when trying to remove card from empty supply pile """


class CardNotInTrash(Exception):
    """ Raised when trying to remove card from trash that is not in the trash """


class State:
    phase = ...
    players: List[Player] = ...
    current_player: Player = ...
    supply: List[Card] = ...

    def __init__(self, num_players: int, supply: List[Card]):
        self.players = [Player() for _ in range(num_players)]
        self.supply = supply
        self.trash = Counter()
        self.attacked_players: List = None

    def add_to_trash(self, card: Card):
        self.trash[card] += 1

    def remove_from_trash(self, card: Card):
        if card not in self.trash:
            raise CardNotInTrash
        self.trash[card] -= 1
        self.trash += Counter()
        return card

    def remove_from_supply(self, card: Card):
        if card.is_supply_empty():
            raise SupplyPileIsEmpty
        card.supply_pile_size -= 1
        return card

# TODO: in Game loop , resolve effects at start of and end of buy / action
