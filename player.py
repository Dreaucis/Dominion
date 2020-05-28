from random import shuffle
import typing
from collections import Counter
from abstract_cards import Card, Victory, Attack, Reaction

# TODO: Try making list of cards into deques
from effects import Effect
from state import State


class CardNotInHand(Exception):
    """ Raised when trying to remove card from hand that is not in the hand """


class Player:
    def __init__(self):
        # Card areas
        self.draw_pile: typing.List[Card] = []
        self.hand: typing.Counter[Card, int] = Counter()
        self.discard_pile: typing.List[Card] = []
        self.play_area: typing.List[Card] = []

        # Turn attributes
        self.money: int = 0
        self.buys: int = 1
        self.actions: int = 1

        # Effects
        self.delayed_card_effects: typing.List[Effect] = []

    @property
    def deck(self) -> typing.List[Card]:
        return self.draw_pile + list(self.hand.elements()) + self.discard_pile

    @property
    def victory_points(self) -> int:
        return sum(card.victory_points for card in self.deck if isinstance(card, Victory))

    def play(self, card: Card, state: State):
        if card.is_playable(state):
            # Remove card from hand
            self.remove_from_hand(card)

            # Add card to play area
            self.play_area.append(card)

            # Resolve card effect
            card.resolve(state)

            # Resolve attack and reacts
            if isinstance(card, Attack):
                # Get targeted players
                attacked_players = [player for player in state.players if player != self]

                # Resolve any reactions to the attack
                for player in attacked_players:
                    reaction_cards = [card for card in list(player.hand) if isinstance(card, Reaction)]
                    for reaction_card in reaction_cards:
                        has_reacted = player.prompt_reaction(reaction_card)
                        if has_reacted:
                            reaction_card.react(player, attacked_players)

                # Resolve attack
                card.attack(attacked_players)

    def add_to_hand(self, card: Card):
        self.hand[card] += 1

    def remove_from_hand(self, card: Card):
        if card not in self.hand:
            raise CardNotInHand
        self.hand[card] -= 1
        self.hand += Counter()
        return card

    def remove_card_effect(self, effect: Effect):
        self.delayed_card_effects.remove(effect)

    def resolve_card_effects(self, state: State):
        for effect in self.delayed_card_effects:
            effect.resolve(state)

    def draw(self, num_cards: int):
        for i in range(num_cards):
            # If the draw pile is empty
            if not self.draw_pile:
                # If the discard pile is empty stop drawing
                if not self.discard_pile:
                    break
                # Shuffle the discard pile under the draw pile and set the discard pile as empty
                self.draw_pile = shuffle(self.discard_pile) + self.draw_pile
                self.discard_pile = []

            # Draw card from draw pile to hand
            self.hand.update([self.draw_pile.pop()])

    @staticmethod
    def prompt_reaction(card: Card) -> bool:
        react = input(f'React with {str(card)}? Y or N')
        return react == 'Y'

    def prompt_discard(self, num_discards: int = 0):
        # TODO: Refactor to allow for flexible discarding (see Cellar). Meybe a force discard and a prompt discard?
        """
        Prompts the player to discard. Returns the number of cards discarded.
        :param num_discards: Number of cards to be discarded
        :return: Number of cards discarded
        """
        while self.hand and num_discards > 0:
            sorted_hand = sorted(list(self.hand), key=card_sort)
            card_name = input(
                f'Discard {num_discards} cards'
                f'Hand: {sorted_hand}'
            )
            # If the prompted card is in hand, discard it
            card = next((card for card in self.hand if card.name == card_name), None)
            if card:
                self.hand[card] -= 1
                self.hand += Counter()  # Remove 0 and negative counts
                self.discard_pile.append(card)
                num_discards -= 1
                print(f'Discarded {card.name}')
            else:
                print(f'{card.name} is not in hand')

    def prompt_trash(self, state: State, num_trashes: int = 0, trashable_cards: typing.Set[Card] = None):
        # TODO: Do a "prompt_select_card" that takes in a set of cards. High priority.

        trashable_cards_in_hand = trashable_cards & set(self.hand.elements())
        while trashable_cards_in_hand and num_trashes > 0:
            sorted_hand = sorted(list(self.hand), key=card_sort)
            card_name = input(
                f'Trash {num_trashes} cards'
                f'Hand: {sorted_hand}'
            )
            # If the prompted card is in hand, trash it
            card = next((card for card in self.hand if card.name == card_name), None)
            if card:
                # Remove card from hand
                self.hand[card] -= 1
                self.hand += Counter()  # Remove 0 and negative counts

                # Add card to trash
                state.trash.update([card])

                num_trashes -= 1
                print(f'Trashed {card.name}')
                trashable_cards_in_hand = trashable_cards & set(self.hand.elements())
            else:
                print(f'{card.name} is not in hand')

    def prompt_select_card(self, cards: typing.List[Card]):
        if cards:
            cards = sorted(cards, key=card_sort)
            card_name = input(
                f'Select a card from {cards}'
            )
            return next((card for card in self.hand if card.name == card_name), None)

    def prompt_gain(self, worth: int, supply: typing.List[Card]):
        # TODO: Maybe prompt_gain should wrap prompt_buy?
        # Can only gain cards if the corresponding supply pile is not empty and the worth is higher than the price
        available_cards = [card for card in supply if not card.is_supply_empty() and card.price <= worth]
        # If there are available cards, prompt for gain
        if available_cards:
            has_gained = False
            while not has_gained:
                sorted_available = sorted(available_cards, key=lambda x: x.price)
                card_name = input(
                    f'Gain a card from'
                    f'Supply: {sorted_available}'
                )
                card = next((card for card in available_cards if card.name == card_name), None)
                # If the typed card was available, add it to the players discard
                if card:
                    self.discard_pile.append(card.gain())
                    has_gained = True


def card_sort(cards: Card) -> typing.List[str]:
    return [cards.tag, cards.name]
