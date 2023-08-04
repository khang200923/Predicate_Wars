from copy import deepcopy
from dataclasses import dataclass, field
from enum import Enum
from typing import List

from predicate import Statement

class CardTag(Enum):
    ROCK = 0
    PAPER = 1
    SCISSORS = 2

@dataclass
class Card:
    blank: bool = True
    tag: CardTag | None = None
    powerCost: int | None = None
    effect: Statement | None = None
    creator: int | None = None

@dataclass
class Player:
    health: int
    power: int = 100
    cards: List[Card] = field(default_factory=list)
    potency: int = 25

@dataclass
class PWars:
    INITHEALTHMULT: int = 50
    INITCARDDECK: int = 256
    INITPOWER: int = 100
    INITPOTENCY: int = 25
    INITPLAYER: int = 4
    INITCARDPLAYER: int = 2
    players: List[Player] = None
    deck: List[Card] = None
    def __post_init__(self):
        self.players = [Player(self.INITHEALTHMULT * self.INITPLAYER, self.INITPOWER, [Card()] * self.INITCARDPLAYER, self.INITPOTENCY)] * self.INITPLAYER
        self.deck = [Card()] * self.INITCARDDECK
