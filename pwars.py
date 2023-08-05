from copy import deepcopy
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, List, Literal, Tuple

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



class GameStateType(Enum):
    INITIAL = 0
    CREATION = 1
    EDITING = 2
    CLAIMING = 3
    MAIN = 4

    FINAL = 5
    SUBPROOF = 6
    ADDRULE = 7
    REMOVERULE = 8

    TURN = 9

@dataclass
class GameState:
    layer: int
    type: GameStateType
    info: Any = None

class PlayerActionType(Enum):
    EDIT = 0
    TAKEBLANK = 1
    CLAIM = 2

    PLAY = 3
    DISCARD = 4
    CLAIMPLAY = 5
    UNREMAIN = 6
    PROVE = 7

    SUBPROOF = 8
    ADDRULE = 9
    REMOVERULE = 10

@dataclass
class PlayerAction:
    player: int
    type: PlayerActionType
    info: Any = None

class GameException(Exception): pass

@dataclass
class PWars:
    """
    A game of Predicate Wars.
    """
    INITHEALTHMULT: int = 50
    INITCARDDECK: int = 128
    INITPOWER: int = 100
    INITPOTENCY: int = 128
    INITPLAYER: int = 4
    INITCARDPLAYER: int = 2
    players: List[Player] = field(default_factory=list)
    deck: List[Card] = field(default_factory=list)
    history: List[Tuple[GameState | PlayerActionType]] = field(default_factory=list)
    def __post_init__(self):
        self.players = [Player(self.INITHEALTHMULT * self.INITPLAYER, self.INITPOWER, [Card()] * self.INITCARDPLAYER, self.INITPOTENCY)] * self.INITPLAYER
        self.deck = [Card()] * self.INITCARDDECK
    def currentGameStates(self) -> Tuple[GameState]:
        """
        Get current game states, with layers.
        """
        res = ()
        highestLayer = 100000
        state: GameState
        for state in reversed(tuple(filter(lambda x: isinstance(x, GameState), self.history))):
            if state.layer < highestLayer:
                highestLayer = state.layer
                res = (state, ) + res
        return res
    def recentPlayerActions(self) -> Tuple[PlayerAction]:
        """
        Return a list of actions taken by each player in order from most recently played action first, since the latest game state.
        """
        latestGameState = next((len(self.history) - index + 1 for index, element in enumerate(self.history[::-1]) if isinstance(element, GameState)), None)
    def nextGameState(self):
        """
        Returns the next game state.
        """
        if self.history == []: return [GameState(0, GameStateType.INITIAL)]
        raise GameException('W.I.P')
    def advance(self):
        """
        Advances to a new game state and returns self.
        """
        self.history += self.nextGameState()
        return self
