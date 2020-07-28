import random
from typing import List

from abstract_cards import Card
from cards import Militia
from constants import ACTION_PHASE, TREASURE_PHASE, BUY_PHASE
from player import Player


class ExpensiveBot(Player):
    def get_input(self, line: str, cards: List[Card], state: 'State') -> str:
        if state.phase == ACTION_PHASE:
            if cards:
                militia = [card for card in cards if isinstance(card, Militia)]
                if militia:
                    return militia[0].name
                return sorted(cards, key=lambda card: -card.price)[0].name
            else:
                return 'SKIP'
        elif state.phase == TREASURE_PHASE:
            c = [card for card in list(self.hand) if card.is_playable(state)][0].name
            return c
        elif state.phase == BUY_PHASE:
            card = sorted(state.affordable_cards(self.money), key=lambda card: -card.price)[0]
            print(f'RANDOM BOUGHT {card}')
            return card.name
