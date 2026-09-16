"""
Execution Mode Enumeration for GEO-Scope Benchmark Engine.
Defines explicit execution boundaries between live API calls and simulated baselines.
"""

from enum import Enum


class ExecutionMode(str, Enum):
    LIVE = "live"
    SIMULATION = "simulation"

    @classmethod
    def from_string(cls, value: str) -> "ExecutionMode":
        """
        Parses a mode string into an ExecutionMode.
        Supports 'simulate' as a backward-compatible alias for 'simulation'.
        """
        if not isinstance(value, str):
            raise ValueError(f"Execution mode must be a string, got {type(value).__name__}")
        normalized = value.strip().lower()
        if normalized == "live":
            return cls.LIVE
        elif normalized in ("simulation", "simulate"):
            return cls.SIMULATION
        else:
            raise ValueError(
                f"Unknown execution mode: {value!r}. Supported modes are: '{cls.LIVE.value}', '{cls.SIMULATION.value}'."
            )

    def is_live(self) -> bool:
        return self == ExecutionMode.LIVE

    def is_simulation(self) -> bool:
        return self == ExecutionMode.SIMULATION
