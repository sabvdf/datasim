from abc import ABC
from typing import Final, Optional

import numpy as np

from .state import State


class Entity(ABC):
    """An entity in the simulation world.

    This can be anything that exhibits behavior.
    """

    registry: Final[dict[type, int]] = {}
    id: Final[int]
    name: Final[str]
    state: Optional[State]
    location: Optional[np.typing.NDArray[np.float64]]

    def __init__(self, name: Optional[str] = None, initial_state: Optional[State | type[State]] = None):
        """Create an entity.

        Args:
            name (Optional[str], optional): Descriptive name of the entity. Defaults to None.
            initial_state (Optional[State], optional): Initial state of the entity. If using a type,
                that type needs to have a constructor with only name as paramater. Defaults to None,
                meaning no behavior will be executed.
        """
        # Give the entity a serial number
        self.id = Entity.registry.get(type(self), 0) + 1
        Entity.registry[type(self)] = self.id
        # Use the serial number as name if no name is given
        if not name:
            name = f"{str(type(self))} {self.id:03}"
        self.name = name
        if isinstance(initial_state, State):
            self.state = initial_state
        elif isinstance(initial_state, type):
            self.state = initial_state(initial_state.__name__)

    def set_state(self, new_state: State | type):
        """Change the state of the entity.

        The new behavior will be executed starting at the next tick.

        Args:
            new_state (State | type): The new state of the entity.
                This can also be a State subtype, in which case a default object
                of that class will be created to execute update ticks.

        Raises:
            TypeError: If the provided type is not a subclass of :class:`State`.
        """
        if isinstance(new_state, type):
            new_state = new_state()
        if not isinstance(new_state, State):
            raise TypeError("Given type is not a subclass of State")

        if self.state:
            self.state.switch_to = new_state
        else:
            self.state = new_state

    def _tick(self):
        if self.state:
            self.state.tick()
            if self.state.switch_to:
                self.state = self.state.switch_to

    def __repr__(self):
        return "Unnamed Entity" if self.name is None else f"Entity {self.name}"
