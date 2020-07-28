import random
from typing import List

from abstract_cards import Card
from constants import ACTION_PHASE, TREASURE_PHASE, BUY_PHASE
from player import Player


class RandomBot(Player):
    def get_input(self, line: str, cards: List[Card], state: 'State') -> str:
        if state.phase == ACTION_PHASE:
            if cards:
                return random.choice(cards).name
            else:
                return 'SKIP'
        elif state.phase == TREASURE_PHASE:
            c = [card for card in list(self.hand) if card.is_playable(state)][0].name
            return c
        elif state.phase == BUY_PHASE:
            card = random.choice(state.affordable_cards(self.money))
            print(f'RANDOM BOUGHT {card}')
            return card.name
