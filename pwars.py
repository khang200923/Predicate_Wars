from copy import deepcopy
from dataclasses import dataclass, field
from enum import Enum
import random
from typing import Any, List, Literal, Tuple

from predicate import Statement

#TODO: Add features in order, in separate commits, one by one...

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
    def edit(self, tag: CardTag, powerCost: int, effect: Statement, creator: int):
        self.tag = tag
        self.powerCost = powerCost
        self.effect = effect
        self.creator = creator
        self.blank = False



@dataclass
class Player:
    health: int
    power: int = 100
    cards: List[Card] = field(default_factory=list)
    potency: int = 25
    def editCard(self, cardID: int, toCard: Card) -> bool:
        if self.cards[cardID] == Card():
            self.cards[cardID] = toCard
            return True
        if self.power >= 2 * self.cards[cardID].powerCost:
            self.power -= 2 * self.cards[cardID].powerCost
            self.cards[cardID] = toCard
            return True
        return False



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

    RANDPLAYER = 10

GStateInfoType = {
    GameStateType.INITIAL: None,
    GameStateType.CREATION: None,
}

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
    def valid(self, typeReq = None) -> bool:
        if not (typeReq == None or self.type == typeReq): return False
        #Specific checks
        if self.type == PlayerActionType.EDIT: return self.info[1] != Card()
        if self.type == PlayerActionType.TAKEBLANK: return isinstance(self.info, bool)
        ...

        return True

PActInfoType = {
    PlayerActionType.EDIT: Tuple[int, Card],
    PlayerActionType.TAKEBLANK: bool,
    PlayerActionType.CLAIM: List[Tuple[int, int]],
}

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
        #TODO: Test this method
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
        latestGameState = next((len(self.history) - index for index, element in enumerate(self.history[::-1]) if isinstance(element, GameState)), -1)
        return tuple(self.history[latestGameState:])

    #Main functions
    #REFACTOR: Argh-
    def nextGameState(self) -> List[GameState]:
        """
        Returns the next game state.
        """
        #TODO: Implement this method
        #TODO: Test this method

        #Initial gameplay
        if self.history == []: return [GameState(0, GameStateType.INITIAL)]

        gameStates = self.currentGameStates()
        playerActs = self.recentPlayerActions()

        if gameStates == (GameState(0, GameStateType.INITIAL),): return [GameState(0, GameStateType.CREATION)]
        if gameStates == (GameState(0, GameStateType.CREATION),):
            #On creation phase, handle player choices of taking blanks
            votes = {**{i: False for i in range(len(self.players))}, **{i: bl for i, bl in ((playerAct.player, playerAct.info) for playerAct in playerActs)}}
            count = len(tuple(0 for i in votes.values() if i))
            if count > len(tuple(0 for card in self.deck if Card() == card)): return [GameState(1, GameStateType.RANDPLAYER, random.randint(0, len(self.players) - 1)), GameState(0, GameStateType.EDITING)]
            else: return [GameState(0, GameStateType.EDITING)]

        raise GameException('W.I.P')
    def advance(self):
        """
        Advances to a new game state and returns self.
        """
        #TODO: Implement this method

        oldGameStates = self.currentGameStates()
        playerActs = self.recentPlayerActions()
        nextGameStates = self.nextGameState()
        self.history += nextGameStates
        newGameStates = self.currentGameStates()

        if oldGameStates == (GameState(0, GameStateType.CREATION),):
            if nextGameStates[0].type == GameStateType.RANDPLAYER:
                self.players[nextGameStates[0].info].cards.append(Card())
                assert Card() in self.deck, 'Undesired error'
                self.deck.remove(Card())
            else:
                votesInd = (i for i, bl in ((playerAct.player, playerAct.info) for playerAct in playerActs) if bl)
                for i in votesInd:
                    self.players[i].cards.append(Card())
                    self.deck.remove(Card())

        return self
    def action(self, playerAct: PlayerAction) -> bool:
        """
        Executes an action on this game instance, if it's valid.
        Returns whether the action is valid or not.
        """
        #TODO: Test this method
        valid = self.actionValid(playerAct)
        if valid:
            playerActs = self.recentPlayerActions()
            self.history.append(playerAct)
            gameStates = self.currentGameStates()

            #On initial gameplay, edit a card based on the player action
            if gameStates == (GameState(0, GameStateType.INITIAL),):
                self.players[playerAct.player].editCard(playerAct.info[0], playerAct.info[1])
            ...

        return valid
    def actionValid(self, playerAct: PlayerAction) -> bool:
        """
        Checks whether the given action is valid.
        """
        #TODO: Implement this method
        #TODO: Test this method.
        gameStates = self.currentGameStates()
        playerActs = self.recentPlayerActions()

        #Initial gameplay
        if gameStates == (GameState(0, GameStateType.INITIAL, None),) and \
        all(playerAct.valid(PlayerActionType.EDIT) for playerAct in playerActs + (playerAct,)): return True

        #Creation phase
        if gameStates == (GameState(0, GameStateType.CREATION, None),) and \
        all(playerAct.valid(PlayerActionType.TAKEBLANK) for playerAct in playerActs + (playerAct,)): return True
        ...
        return False
