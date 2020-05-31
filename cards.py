from abstract_cards import Action, Victory, Treasure, Attack, Reaction, Card
from typing import List
from effects import Effect
from player import Player
from constants import TREASURE, CURSE


# Victory cards
class Estate(Victory):
    price = 2
    victory_points = 1


class Duchy(Victory):
    price = 5
    victory_points = 3


class Province(Victory):
    price = 8
    victory_points = 6

    def get_starting_supply_pile_size(self, num_players: int) -> int:
        if num_players == 2:
            return 8
        elif num_players < 5:
            return 12
        elif num_players < 6:
            return 15
        else:
            return 18


class Curse(Card):
    tag = CURSE
    price = 0
    victory_points = -1

    @staticmethod
    def _is_playable(state: 'State') -> bool:
        return False

    def resolve(self, state: 'State'):
        pass

    def get_starting_supply_pile_size(self, num_players):
        return min(60, (num_players - 1) * 10)


# Treasures
class Copper(Treasure):
    price = 0
    worth = 1

    def get_starting_supply_pile_size(self, _) -> int:
        return 60


class Silver(Treasure):
    price = 3
    worth = 2

    def get_starting_supply_pile_size(self, _) -> int:
        return 40


class Gold(Treasure):
    price = 6
    worth = 3

    def get_starting_supply_pile_size(self, _) -> int:
        return 30


# Action cards
class Smithy(Action):
    price = 4

    def resolve(self, state: 'State'):
        state.current_player.draw(3)


class Village(Action):
    price = 3

    def resolve(self, state: 'State'):
        state.current_player.draw(1)
        state.current_player.actions += 2


class Militia(Action, Attack):
    price = 4

    # TODO: male the attack a method that targets one player at a time? How to check for reaction?
    def resolve(self, state: 'State'):
        state.current_player.money += 2

    def attack(self, attacked_players: List[Player]):
        for player in attacked_players:
            # If other players have more than 3 cards in hand force them to discard
            if len(player.hand) > 3:
                player.prompt_discard(len(player.hand) - 3)


class Workshop(Action):
    price = 3

    def resolve(self, state: 'State'):
        state.current_player.prompt_gain(4, state.supply)


class Cellar(Action):
    price = 2

    def resolve(self, state: 'State'):
        num_cards = int(input('How many cards do you wish to discard?'))
        num_cards_in_hand = sum(state.current_player.hand.values()) - 1  # Number of cards before discard
        state.current_player.prompt_discard(num_cards)
        num_discarded = num_cards_in_hand - sum(state.current_player.hand.values()) - 1
        state.current_player.draw(num_discarded)


class Merchant(Action):
    price = 3

    def resolve(self, state: 'State'):
        state.current_player.draw(1)
        state.current_player.actions += 1
        state.current_player.delayed_card_effects.append(Effect(BUY_PHASE, self.effect))

    @staticmethod
    def effect(state: 'State'):
        player = state.current_player
        # if there are any silver in the play area, add one to the players money count
        if any(isinstance(card, Silver) for card in player.play_area):
            player.money += 1


class Laboratory(Action):
    price = 5

    def resolve(self, state: 'State'):
        state.current_player.draw(2)
        state.current_player.actions += 1


class Market(Action):
    price = 5

    def resolve(self, state: 'State'):
        state.current_player.draw(1)
        state.current_player.actions += 1
        state.current_player.buys += 1
        state.current_player.money += 1


class Mine(Action):
    price = 5

    def resolve(self, state: 'State'):
        player = state.current_player
        # Can only trash treasures in hand
        trashable_cards = [card for card in player.hand if card.tag == TREASURE]
        if trashable_cards:
            # Prompt for card to be gained
            trashed_card = player.prompt_select_card(trashable_cards)

            # Move card from hand to trash
            state.add_to_trash(player.remove_from_hand(trashed_card))

            # Any treasure card that worth less than or equal to the price plus 3 of the trashed card can be gained
            gainable_cards = [
                card for card in state.supply if
                card.tag == TREASURE and card.price <= trashed_card.price + 3 and not card.is_supply_empty()
            ]

            # If there are any possible gainable cards, prompt player to select
            if gainable_cards:
                gained_card = player.prompt_select_card(gainable_cards)

                # Move card from supply to player hand
                player.add_to_hand(state.remove_from_supply(gained_card))


class Moat(Action, Reaction):
    price = 2

    def resolve(self, state: 'State'):
        state.current_player.draw(2)

    def react(self, reacting_players: Player, attacked_players: List[Player]):
        attacked_players.remove(reacting_players)


class Remodel(Action):
    price = 4

    def resolve(self, state: 'State'):
        player = state.current_player

        # May trash any card in hand
        trashable_cards = list(player.hand)
        if trashable_cards:
            # Prompt for card to be gained
            trashed_card = player.prompt_select_card(trashable_cards)

            # Move card from hand to trash
            state.add_to_trash(player.remove_from_hand(trashed_card))

            # Any card in supply worth less than or equal to the price plus 2 of the trashed card can be gained
            gainable_cards = [
                card for card in state.supply if card.price <= trashed_card.price + 2 and not card.is_supply_empty()
            ]

            # If there are any possible gainable cards, prompt player to select
            if gainable_cards:
                gained_card = player.prompt_select_card(gainable_cards)

                # Move card from supply to player hand
                player.add_to_hand(state.remove_from_supply(gained_card))
