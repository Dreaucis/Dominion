from typing import List
from collections import Counter

from abstract_cards import Card
from player import Player

ACTION_PHASE = 'ACTION'
BUY_PHASE = 'BUY'


class State:
    phase = ...
    players: List[Player] = ...
    current_player: Player = ...
    supply: List[Card] = ...

    def __init__(self, num_players: int, supply: List[Card]):
        self.players = [Player() for _ in range(num_players)]
        self.supply = supply
        self.trash = Counter()

# TODO: in Game loop , resolve effects at start of and end of buy / action
