from dataclasses import dataclass


@dataclass(frozen=True)
class Submission:
    topic: str
    thesis_received: bool
