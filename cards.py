from abstract_cards import Action, Victory, Treasure, Attack
from effects import Effect
from tags import TREASURE
from state import State, ACTION_PHASE, BUY_PHASE


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


class Curse(Victory):
    price = 0
    victory_points = -1

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

    def resolve(self, state: State):
        state.current_player.draw(3)


class Village(Action):
    price = 3

    def resolve(self, state: State):
        state.current_player.draw(1)
        state.current_player.actions += 2


class Militia(Action, Attack):
    price = 4

    def resolve(self, state: State):
        state.current_player.money += 2
        for player in state.players:
            # If other players have more than 3 cards in hand force them to discard
            if len(player.hand) > 3:
                player.prompt_discard(len(player.hand) - 3)


class Workshop(Action):
    price = 3

    def resolve(self, state: State):
        state.current_player.prompt_gain(4, state.supply)


class Cellar(Action):
    price = 2

    def resolve(self, state: State):
        num_cards = int(input('How many cards do you wish to discard?'))
        num_cards_in_hand = sum(state.current_player.hand.values()) - 1  # Number of cards before discard
        state.current_player.prompt_discard(num_cards)
        num_discarded = num_cards_in_hand - sum(state.current_player.hand.values()) - 1
        state.current_player.draw(num_discarded)


class Merchant(Action):
    price = 3

    def resolve(self, state: State):
        state.current_player.draw(1)
        state.current_player.actions += 1
        state.current_player.delayed_card_effects.append(Effect(BUY_PHASE, self.effect))

    @staticmethod
    def effect(state: State):
        player = state.current_player
        # if there are any silver in the play area, add one to the players money count
        if any(isinstance(card, Silver) for card in player.play_area):
            player.money += 1


class Laboratory(Action):
    price = 5

    def resolve(self, state: State):
        state.current_player.draw(2)
        state.current_player.actions += 1


class Market(Action):
    price = 5

    def resolve(self, state: State):
        state.current_player.draw(1)
        state.current_player.actions += 1
        state.current_player.buys += 1
        state.current_player.money += 1


class Mine(Action):
    price = 5

    def resolve(self, state: State):
        player = state.current_player
        prior_trash = state.trash.copy()
        trashable_cards = set(card for card in player.hand if card.tag == TREASURE)
        state.current_player.prompt_trash(state, 1, trashable_cards)  # TODO: This should return the trashed cards
        trashed_card = list(state.trash - prior_trash)[0]
        # TODO: implement the more flexible gain prompt (from/to) before continuing
