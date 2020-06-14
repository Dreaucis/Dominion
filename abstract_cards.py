from typing import List

from constants import ACTION, TREASURE, VICTORY, ATTACK, REACTION, ACTION_PHASE, BUY_PHASE
from abc import ABC, abstractmethod


class Card(ABC):
    """
    Base class for all cards
    """

    def __init__(self, num_players):
        self.supply_pile_size = self.get_starting_supply_pile_size(num_players)

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.name

    @property
    def name(self) -> str:
        return self.__class__.__name__

    @property
    def tags(self) -> tuple:
        return tuple(getattr(x, 'tag') for x in self.__class__.__mro__)

    @property
    @abstractmethod
    def price(self) -> int:
        pass

    @property
    @abstractmethod
    def tag(self):
        pass

    @abstractmethod
    def get_starting_supply_pile_size(self, num_players: int) -> int:
        # TODO: I don't like this since not all children use num_players.
        pass

    @abstractmethod
    def resolve(self, state: 'State'):
        pass

    def is_playable(self, state: 'State') -> bool:
        return any(getattr(x, '_is_playable')(state) for x in self.__class__.__mro__ if hasattr(x, '_is_playable'))

    def is_supply_empty(self) -> bool:
        return not bool(self.supply_pile_size)

    def gain(self):
        self.supply_pile_size = self.supply_pile_size - 1
        return self

    @staticmethod
    @abstractmethod
    def _is_playable(state: 'State') -> bool:
        pass


class Victory(Card):
    """
    Abstract class for Victory cards
    """
    tag = VICTORY

    @property
    @abstractmethod
    def victory_points(self):
        pass

    @staticmethod
    def _is_playable(state: 'State') -> bool:
        return False

    def get_starting_supply_pile_size(self, num_players: int) -> int:
        return 8 if num_players == 2 else 12

    def resolve(self, state: 'State'):
        pass


class Treasure(Card):
    """
    Abstract class for Treasure cards
    """
    tag = TREASURE

    @property
    @abstractmethod
    def worth(self):
        pass

    @staticmethod
    def _is_playable(state: 'State') -> bool:
        return state.phase == BUY_PHASE

    def resolve(self, state: 'State'):
        state.current_player.money += self.worth


class Action(Card):
    """
    Abstract class for Action cards
    """
    tag = ACTION

    @staticmethod
    def _is_playable(state: 'State') -> bool:
        return state.phase == ACTION_PHASE and state.current_player.actions > 0

    @abstractmethod
    def resolve(self, state: 'State'):
        pass

    def get_starting_supply_pile_size(self, _) -> int:
        return 10


class Attack(Card, ABC):
    """
    Abstract class for Attack cards
    """
    tag = ATTACK

    @abstractmethod
    def attack(self, attacked_players: List['Player']):
        pass


class Reaction(Card):
    # TODO: Implement better...
    """
    Abstract class for Reaction cards
    """
    tag = REACTION

    @abstractmethod
    def react(self, reacting_player: 'Player', targeted_players: List['Player']):
        pass
