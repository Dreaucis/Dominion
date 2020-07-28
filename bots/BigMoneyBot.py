from abstract_cards import Card
from cards import Province, Gold, Silver
from constants import ACTION_PHASE, TREASURE_PHASE, BUY_PHASE
from player import Player
from typing import List


class BigMoneyBot(Player):
    def get_input(self, line: str, cards: List[Card], state: 'State') -> str:
        if state.phase == ACTION_PHASE:
            return list(self.hand)[0].name
        elif state.phase == TREASURE_PHASE:
            c = [card for card in list(self.hand) if card.is_playable(state)][0].name
            return c
        elif state.phase == BUY_PHASE:
            if self.money > 8:
                return Province.__name__
            elif self.money > 5:
                return Gold.__name__
            elif self.money > 2:
                return Silver.__name__
            else:
                return 'Skip'
