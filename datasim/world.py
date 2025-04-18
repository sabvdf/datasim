from abc import ABC
import codecs
from psutil import Process
from os import getpid
from sys import stdout
from threading import Thread
from time import sleep
from typing import Dict, Final, List, Optional, Self

from .entity import Entity
from .plot import Plot


class World(ABC):
    """Abstract base class for the simulation world.

    A simulation should run in a subclass of World.
    """

    ticks: int = 0
    tps: float = 10.0
    update_time: float | None = 1.0

    headless: bool
    current: Optional[Self] = None
    title: Final[str]
    entities: Final[List[Entity]]
    plots: Final[Dict[str, Plot]]
    stopped: bool = False

    def __init__(
        self,
        title: str = "Unnamed Simulation",
        tps: float = 10.0,
        headless: bool = False,
    ):
        """Create the simulation world.

        Args:
            title (str, optional): Descriptive name of the simulation (world). Defaults to "Unnamed Simulation".
            tps (float, optional): Ticks per second (only in simulation time,
                unless running :meth:`simulate()` with `realtime=True`). Defaults to 10.0.
        """
        if World.current:
            print("(Warning: Not launching another instance)")
            return
        World.current = self
        self.title = title
        self.entities = []
        self.plots = {}
        from datasim import Dashboard

        self.dashboard: Optional[Dashboard] = None
        self.ended: bool = False
        World.tps = tps
        print(f"tps: {World.tps}")

        stdout.reconfigure(encoding="utf-8")  # type: ignore
        print(codecs.open("header", "r", "utf-8").read())  # Draw terminal logo

        self.headless = headless
        if not headless and not self.dashboard:
            self.dashboard = Dashboard()

    @staticmethod
    def reset():
        """Reset the World so you can start a different simulation."""
        World.current = None

    @staticmethod
    def seconds() -> float:
        """Get the number of seconds elapsed in the simulation world."""
        return World.ticks / World.tps

    def _draw(self):
        if self.dashboard:
            self.dashboard._draw()

    def add_plot(self, plot: Plot):
        """Add a plot to the dashboard."""
        if self.dashboard:
            self.plots[plot.id] = plot

    def add(self, entity: Entity):
        """Add an entity to this :class:`World`.

        Args:
            entity (Entity): The entity to add.
        """
        self.entities.append(entity)

    def remove(self, entity: Entity) -> bool:
        """Remove an entity from this :class:`World`.

        Args:
            entity (Entity): The entity to remove.

        Returns:
            bool: `True` if the entity was succesfully removed.
        """
        try:
            self.entities.remove(entity)
        except ValueError:
            return False
        return True

    def simulate(
        self,
        tps: float = 0.0,
        end_tick: int = 0,
        restart: bool = False,
        realtime: bool = False,
        stop_server: bool = False,
    ) -> bool:
        """Run the simulation.

        Args:
            tps (float, optional): Ticks per second (only in simulation time, unless `realtime=True`).
                Defaults to :data:`World.tps`.
            end_tick (int, optional): Tick count to end, unless set to 0. Defaults to 0.
            restart (bool, optional): Set to `True` if this is a restart. Defaults to False.
            realtime (bool, optional): Run the simulation in real seconds. Defaults to False.
            stop_server (bool, optional): Terminate streamlit python process after the simulation is done.
                For now, use only for faster debugging workflow. Defaults to False.
        """
        if self.ended and not restart:
            return False

        if tps > 0.0:
            World.tps = tps
        World.ticks = 0
        World.tick_time = 1.0 / World.tps
        self.end_tick = end_tick
        self.realtime = realtime
        self.stop_server = stop_server
        self.sim_thread = Thread(target=self._simulation_thread)
        self.sim_thread.start()
        return True

    def stop(self):
        """Stop the simulation and wait for it to end."""
        self.stopped = True
        self.wait()

    def wait(self):
        """Wait for the simulation to end."""
        if self.sim_thread:
            self.sim_thread.join()

    def _update_plots(self):
        for plot in self.plots.values():
            plot._update()

    def pre_entities_tick(self):
        """Implement this function to run any code at the start of each tick, \
            before all entities are updated."""
        pass

    def post_entities_tick(self):
        """Implement this function to run any code at the end of each tick, \
            after all entities have been updated."""
        pass

    def _simulation_thread(self):
        print(
            f"\n{"#"*(36+len(self.title))}\n"
            + f"###  {self.title}  ###  Starting simulation  ###\n"
            + f"{"#"*(36+len(self.title))}\n"
        )

        if self.end_tick > 0:
            print(
                f"{self.title}: Run for {self.end_tick / World.tps} seconds"
                + f" ({self.end_tick} ticks at {World.tps} ticks/second)..."
            )

        self.last_update = 0

        while World.ticks < self.end_tick and not self.stopped:
            self.pre_entities_tick()
            for entity in self.entities:
                entity._tick()
            self.post_entities_tick()
            if self.dashboard:
                for plot in self.plots.values():
                    plot._tick()
            World.ticks += 1
            if self.realtime:
                sleep(World.tick_time)

        self.ended = True
        print(
            f"\n{"#"*(34+len(self.title))}\n"
            + f"###  {self.title}  ###  End of simulation  ###\n"
            + f"{"#"*(34+len(self.title))}\n"
        )

        World.update_time = 0.0

        if self.stop_server:
            sleep(3)
            pid = getpid()
            p = Process(pid)
            p.terminate()
