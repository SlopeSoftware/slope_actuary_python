from dataclasses import dataclass

@dataclass
class GuessIteration:
    prior_guess: float = None
    prior_result: float = None
    current_guess: float = None
    iteration: int = 0