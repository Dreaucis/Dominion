from abc import abstractmethod
from typing import Callable

from state import State


class Effect:

    def __init__(self, trigger_phase: str, resolve: Callable[[State], None]):
        self.trigger_phase = trigger_phase
        self._resolve = resolve
        self.has_triggered = False

    def resolve(self, state: State):
        if state.phase == self.trigger_phase:
            self._resolve(state)
            self.has_triggered = True
