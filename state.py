from typing import List, Type
from collections import Counter
import random

from bots import RandomBot, ExpensiveBot, BigMoneyBot
from abstract_cards import Card
from bot import bot_state
from cards import Estate, Copper, Province
from constants import ACTION_PHASE, BUY_PHASE, TREASURE_PHASE
from player import Player
from recommended_kingdoms import FIRST_GAME, initialize_kingdom

MAXIMUM_NUMBER_OF_ROUNDS = 20


class SupplyPileIsEmpty(Exception):
    """ Raised when trying to remove card from empty supply pile """


class CardNotInTrash(Exception):
    """ Raised when trying to remove card from trash that is not in the trash """


class CardNotInSupply(Exception):
    """ Raised when trying to get a card reference that is not in the supply """


class State:
    def __init__(self, players: List[Player], supply: List[Card], max_turn_number=25, seed=None):
        if seed:
            random.seed(seed)
        self.current_player = None
        self.phase = None
        self.players = players
        self.supply = supply
        starting_card = 3 * [self.get_card(Estate)] + 7 * [self.get_card(Copper)]
        for player in self.players:
            player.draw_pile = random.sample(starting_card, len(starting_card))
            player.draw(5)
        self.trash = Counter()

        self.turn_number = 0
        self.max_turn_number = max_turn_number

    def add_to_trash(self, card: Card):
        self.trash[card] += 1

    def remove_from_trash(self, card: Card):
        if card not in self.trash:
            raise CardNotInTrash
        self.trash[card] -= 1
        self.trash += Counter()
        return card

    @staticmethod
    def remove_from_supply(card: Card):
        if card.is_supply_empty():
            raise SupplyPileIsEmpty
        card.supply_pile_size -= 1
        return card

    def get_card(self, card_class: Type[Card]) -> Card:
        card = [card for card in self.supply if isinstance(card, card_class)][0]
        if not card:
            raise CardNotInSupply
        return card

    def affordable_cards(self, money):
        return [card for card in self.supply if card.price <= money and not card.is_supply_empty()]

    def has_game_ended(self):
        empty_supply_piles = [card for card in self.supply if card.is_supply_empty()]
        max_empty = 3 if len(self.players) <= 3 else 4
        return any(isinstance(card, Province) for card in empty_supply_piles) or len(
            empty_supply_piles) >= max_empty or self.turn_number > self.max_turn_number


# TODO: in Game loop , resolve effects at start of and end of buy / action
def main():
    players = [RandomBot('bot1'), ExpensiveBot('bot2')]
    num_players = len(players)
    supply = initialize_kingdom(FIRST_GAME, num_players)
    state = State(players, supply, 42)
    while not state.has_game_ended():
        print(f'TURN {state.turn_number}')  # TODO: Use textwrap for nice printouts
        for player in state.players:
            print(f"PLAYER {player.name}'S TURN")
            print(player.hand)
            state.current_player = player

            # Play actions
            state.phase = ACTION_PHASE
            print(f"PLAYER {player.name}'S ACTION PHASE")
            print(f"PLAY ACTIONS")
            print(bot_state(player, state))
            while player.has_playable_cards_in_hand(state) and player.actions > 0:
                selected_card = player.prompt_select_card(player.playable_cards(state), state)
                if not selected_card:
                    break
                player.play(selected_card, state)
                print(player.hand)
                print(player.play_area)

            # Play treasures
            print(f"PLAYER {player.name}'S TREASURE PHASE")
            print(f"PLAY TREASURES")
            state.phase = TREASURE_PHASE
            print(player.buys)
            print(player.has_playable_cards_in_hand(state))
            print('HANd ' + str(list(player.hand)))
            while player.has_playable_cards_in_hand(state) and player.buys > 0:
                selected_card = player.prompt_select_card(player.playable_cards(state), state)
                # If no card is selected, end treasure playing
                if not selected_card:
                    break
                player.play(selected_card, state)
                print(player.hand)
                print(player.play_area)

            # Buy cards
            print(f"PLAYER {player.name}'S BUY PHASE")
            print(f"BUY CARDS")
            state.phase = BUY_PHASE
            while player.buys > 0:
                selected_card = player.prompt_select_card(state.affordable_cards(player.money), state)
                if not selected_card:
                    break
                player.buy(selected_card, State)
                print(selected_card)

            # Cleanup
            player.reset_turn_attributes()
            player.cleanup()
            print(player.hand)
            player.draw(5)

        state.turn_number += 1

    # Print final results
    for player in state.players:
        print(f'TURN NUMBER: {state.turn_number}')
        print(f'Player: {player.name}, VP: {player.victory_points}')
        print(player.deck)


if __name__ == '__main__':
    for i in range(100):
        main()
