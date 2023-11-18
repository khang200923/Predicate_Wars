"""
Provides essential classes and methods for the game itself.
"""
from copy import deepcopy
from dataclasses import dataclass, field
from enum import Enum
import random
import types
from typing import Any, Callable, Dict, Iterable, List, Optional, Set, Tuple

from predicate import Proof, ProofBase, StateTag, Statement, baseRules, _doOperator, gameFuncNames, predGFuncNames

#REMINDER: Add features in order, in separate commits, one by one...
#REMINDER: When adding player action features, update:
#          - PlayerActionType variable
#          - PlayerAction.valid function
#          - PActInfoType variable
#          - PWars.nextGameState
#            (if changes in game based on player actions happens after game state & optional)
#          - PWars.advance (if changes in game based on player actions happens after game state)
#          - PWars.action (optional)
#          - PWars.actionValid
#REMINDER: When adding game state features, update:
#          - GameStateType variable
#          - GStateInfoType variable
#          - PWars.nextGameState
#          - PWars.advance (optional)


def _allUnique(iter: Iterable, key: Callable = lambda x: x) -> bool:
    seenKeys = list()
    return not any(key(i) in seenKeys or seenKeys.append(key(i)) for i in iter)

def _mergeItersWithDelimiter(iters: Iterable[Iterable], delimiter: Any):
    for i, itera in enumerate(iters):
        if i > 0: yield delimiter
        for elem in itera:
            yield elem

class CardTag(Enum):
    ROCK = 0
    PAPER = 1
    SCISSORS = 2
    def beat(self, oppoTag: 'CardTag'):
        if (self is CardTag.ROCK and oppoTag is CardTag.SCISSORS):
            return True
        if (self is CardTag.PAPER and oppoTag is CardTag.ROCK):
            return True
        if (self is CardTag.SCISSORS and oppoTag is CardTag.PAPER):
            return True
        return False

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
    pPower: int = 0
    subproofs: List[ProofBase] = field(default_factory=list)
    def editCard(self, cardID: int, toCard: Card) -> bool:
        if self.cards[cardID] == Card():
            self.cards[cardID] = toCard
            return True
        if self.power >= 2 * self.cards[cardID].powerCost:
            self.power -= 2 * self.cards[cardID].powerCost
            self.cards[cardID] = toCard
            return True
        return False
    def playInit(self):
        self.pPower = self.potency



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
    PROVE = 11
    EFFECT = 12

    RANDPLAYER = 10

GStateInfoType = {
    GameStateType.INITIAL: None,
    GameStateType.CREATION: None,
    GameStateType.EDITING: None,
    GameStateType.CLAIMING: None,
    GameStateType.MAIN: None,

    GameStateType.TURN: int,
    GameStateType.PROVE: None,
    GameStateType.EFFECT: None,

    GameStateType.RANDPLAYER: int,
}

@dataclass
class GameState:
    layer: int
    type: GameStateType
    info: Any = None
    @staticmethod
    def randPlayer(self: 'PWars', layer: int) -> 'GameState':
        """
        Generates RANDPLAYER game state.
        """
        return GameState(layer, GameStateType.RANDPLAYER, random.randint(0, len(self.players) - 1))
    @staticmethod
    def nextTurn(self: 'PWars', turn: 'GameState') -> 'GameState':
        """
        Return next state of TURN game state
        """
        if turn.type == GameStateType.TURN:
            return GameState(turn.layer, GameStateType.TURN, (turn.info + 1) % len(self.players))
        else: raise ValueError("Not a Turn")

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

    DEBUGACT = 11

@dataclass
class PlayerAction:
    player: int
    type: PlayerActionType
    info: Any = None
    def valid(self, typeReq: None | PlayerActionType | Tuple[PlayerActionType] = None) -> bool:
        if isinstance(typeReq, PlayerActionType):
            if not self.type == typeReq: return False
        elif (isinstance(typeReq, tuple)):
            if not self.type in typeReq: return False
        #Specific checks
        if self.type == PlayerActionType.EDIT:
            return self.info[1] != Card()
        elif self.type == PlayerActionType.TAKEBLANK:
            return isinstance(self.info, bool)
        elif self.type == PlayerActionType.CLAIM:
            return isinstance(self.info, list) and \
            all(isinstance(claim, tuple) and len(claim) == 2 and \
            all(isinstance(num, int) for num in claim) for claim in self.info)
        elif self.type == PlayerActionType.PLAY:
            return isinstance(self.info, tuple) and len(self.info) == 2 and \
            all(isinstance(x, int) for x in self.info)
        elif self.type == PlayerActionType.DISCARD:
            return isinstance(self.info, int)
        elif self.type == PlayerActionType.UNREMAIN:
            return self.info is None
        elif self.type == PlayerActionType.CLAIMPLAY:
            return isinstance(self.info, list) and \
            all(
                isinstance(claim, tuple) and len(claim) == 2 and \
                all(isinstance(num, int) for num in claim)
                for claim in self.info
            )
        elif self.type == PlayerActionType.PROVE:
            return isinstance(self.info, tuple) and len(self.info) == 3 and \
                isinstance(self.info[0], (int, types.NoneType)) and \
                isinstance(self.info[1], Proof) and \
                isinstance(self.info[2], int)

        elif self.type == PlayerActionType.DEBUGACT: return True
        else: raise ValueError('Invalid type')

PActInfoType = {
    PlayerActionType.EDIT: Tuple[int, Card],
    PlayerActionType.TAKEBLANK: bool,
    PlayerActionType.CLAIM: List[Tuple[int, int]], #[playerID, cardID]

    PlayerActionType.PLAY: Tuple[int, int], #(main, secondary)
    PlayerActionType.DISCARD: int,
    PlayerActionType.CLAIMPLAY: List[Tuple[int, int]], #[playerID, cardID]
    PlayerActionType.UNREMAIN: None,
    PlayerActionType.PROVE: Tuple[int | None, Proof, int], #(opposingProofIndex, proof, deriveIndex)

    PlayerActionType.DEBUGACT: Any
}

class GameException(Exception):
    pass

@dataclass
class CalcInstance:
    chosenPlayer: dict[int, int] = field(default_factory=dict)
    chosenCard: dict[int, Tuple[int, int]] = field(default_factory=dict)
    randomPlayer: dict[int, int] = field(default_factory=dict)
    randomCard: dict[int, Tuple[int, int]] = field(default_factory=dict)
    cardsOfPlayers: dict[int, Set[int]] = field(default_factory=dict)
    playerObjs: dict[int, Player] = field(default_factory=dict)
    cardObjs: dict[int, Card] = field(default_factory=dict)

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
    remaining: List[bool] = field(default_factory=list)
    discardPile: List[Card] = field(default_factory=list)
    dropPile: List[Card] = field(default_factory=list)
    recentPlay: Optional[Tuple[Card, Card]] = None
    rules: Dict[int, Statement] = field(default_factory=dict)

    def __post_init__(self):
        self.players = [Player(
            self.INITHEALTHMULT * self.INITPLAYER,
            self.INITPOWER, [Card() for _ in range(self.INITCARDPLAYER)],
            self.INITPOTENCY)
            for _ in range(self.INITPLAYER)
        ]
        self.deck = [Card() for _ in range(self.INITCARDDECK)]
        self.remaining = [False for _ in self.players]

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
        Return a list of actions taken by each player in order from most recently played action first,
        since the latest game state.
        """
        latestGameState = next((len(self.history) - index
                                for index, element in enumerate(self.history[::-1])
                                if isinstance(element, GameState)), -1)
        return tuple(self.history[latestGameState:])

    def startAxioms(self, opposingProofIndex: int | None) -> Tuple[Statement, ...]:
        """
        Return axioms to start infering the proofs in proving game state.
        Raises error if not in proving game state.
        """
        gameStates = self.currentGameStates()
        playerActs = self.recentPlayerActions()
        if len(gameStates) == 4 and gameStates[0].type == GameStateType.MAIN and \
        gameStates[3].type == GameStateType.PROVE:
            if opposingProofIndex is None:
                res = (self.recentPlay[0].effect, self.recentPlay[1].effect)
            else: res = tuple(playerActs[opposingProofIndex].info[1].statements)
        else:
            raise GameException("Not in proving game state")
        res += tuple(self.rules.values()) + baseRules
        return res

    def formatActionFunctionParam(self, state: Statement) -> Tuple:
        """
        Format statement as if it is a param of the action function.
        Return None if not deterministic.
        """
        #TODO: Implement this method
        #TODO: Test this method
        if not state.deterministic(): return None
        if not state.simple():
            return self.formatActionFunctionParam(self.calcStatement(state))

        if len(state) == 1 and state[0][0] == 'number':
            return ('number', state[0][1])
        if len(state) == 4:
            if state[0][0] == '[randPlayer]' and state[2][0] == 'number':
                return ('randPlayer', state[2][1])
            if state[0][0] == '[randCard]' and state[2][0] == 'number':
                return ('randCard', state[2][1])
            if state[0][0] == '[chosenPlayer]' and state[2][0] == 'number':
                return ('chosenPlayer', state[2][1])
            if state[0][0] == '[chosenCard]' and state[2][0] == 'number':
                return ('chosenCard', state[2][1])

    def applyEffect(
            self,
            statement: Statement,
            chosenPlayer: dict[int, int],
            chosenCard: dict[int, Tuple[int, int]]
        ) -> 'PWars':
        """
        Apply game effects, then return self.
        """
        #TODO: Implement this method
        #TODO: Test this method
        if statement[0][0] == 'gameFuncName':
            params = statement.functionArgs()
            paramFormatted = tuple(
                self.formatActionFunctionParam(param)
                for param in params
            )
            self.applySpecificEffect(paramFormatted, chosenPlayer, chosenCard)
        else:
            if statement.deterministic(): ...  #TODO: W.I.P
            else:
                raise GameException(
                    'Invalid statement for game effect'
                )

    def applySpecificEffect(
            self,
            params: Tuple[Tuple],
            chosenPlayer: dict[int, int] = dict(),
            chosenCard: dict[int, Tuple[int, int]] = dict(),
            randomPlayer: dict[int, int] = dict(),
            randomCard: dict[int, Tuple[int, int]] = dict()
        ) -> 'PWars':
        """
        Apply a game effect to a specific player/card, then return self.
        """
        #TODO: Implement this method
        #TODO: Test this method
        ...

        return self

    @staticmethod
    def calcStatement(
        state: Statement, obj: bool | None = False,
        calcInstance: CalcInstance = CalcInstance(),
        conversion: bool = True,
    ):
        """
        Calculate deterministic WFF/WFO.
        Throw error if not WFF/WFO.
        Return None if not deterministic or is an action function.
        """
        #TODO: Test this method
        if obj is None:
            if not (state.wellformedobj() or state.wellformed()): raise ValueError('Not a well-formed object/formula')
        else:
            if obj and not state.wellformedobj(): raise ValueError('Not a well-formed object')
            if (not obj) and not state.wellformed(): raise ValueError('Not a well-formed formula')

        if not state.deterministic(obj):
            return None

        if state[0][0] == 'predAFuncName': return None

        if state.simple(obj):
            return PWars.convert(PWars.calcSimple(state, obj, calcInstance), calcInstance, conversion)
        else:
            res = state.functionArgs()
            if res is not None:
                return PWars.convert(
                    Statement(Statement(state[0]) + Statement.lex('(') + \
                    Statement(
                        _mergeItersWithDelimiter(
                            (PWars.calcStatement(
                                arg, obj,
                                calcInstance,
                                conversion=False
                            ) for arg in res),
                            Statement.lex(',')
                        )
                    ) + \
                    Statement.lex(')')), calcInstance, conversion)
            res = state.operatorArgs()
            if res is not None:
                return PWars.convert(Statement(
                    Statement.lex('(') + \
                    PWars.calcStatement(res[0], obj, calcInstance, conversion=False) + \
                    state.operatorSymbol() + \
                    PWars.calcStatement(res[1], obj, calcInstance, conversion=False) + \
                    Statement.lex(')')), calcInstance, conversion)
            raise ValueError('Impossible error.')

    @staticmethod
    def calcSimple(
        state: Statement, obj: bool | None = False,
        calcInstance: CalcInstance = CalcInstance(),
        conversion: bool = True,
    ):
        """
        Calculate simple WFF/WFO.
        Throw error if not WFF/WFO.
        Return None if not simple or is an action function.
        """
        #TODO: Test this method
        if obj is None:
            if not (state.wellformedobj() or state.wellformed()): raise ValueError('Not a well-formed object/formula')
        else:
            if obj and not state.wellformedobj(): raise ValueError('Not a well-formed object')
            if (not obj) and not state.wellformed(): raise ValueError('Not a well-formed formula')

        if state[0][0] == 'predAFuncName': return None

        res = state.operatorArgs()
        if res is not None:
            num1, num2, oper = res[0][0][1], res[1][0][1], state.operatorSymbol()
            return Statement((('number', _doOperator(num1, num2, oper)),))
        res = state.functionArgs()
        if res is not None:
            return PWars.calcFunction(
                state[0], tuple(state[0] for state in res), calcInstance
            )

    @staticmethod
    def calcFunction(
        name: Tuple, args: Tuple[Tuple, ...],
        calcInstance: CalcInstance = CalcInstance(),
    ):
        """
        Calculates simple function based on name and arguments.
        """
        #TODO: Implement this method
        #TODO: Test this method
        cI = calcInstance #Reduces pain

        match name:
            case '[randPlayer]':
                if args[0][0] == 'number':
                    num = int(args[0][1])
                    return Statement(('player', cI.randomPlayer[num]))
            case '[randCard]':
                if args[0][0] == 'number':
                    num = int(args[0][1])
                    return Statement(('card', cI.randomCard[num]))
            case '[chosenPlayer]':
                if args[0][0] == 'number':
                    num = int(args[0][1])
                    return Statement(('player', cI.chosenPlayer[num]))
            case '[chosenCard]':
                if args[0][0] == 'number':
                    num = int(args[0][1])
                    return Statement(('card', cI.chosenCard[num]))
            case '[playerOfChosenCard]':
                if args[0][0] == 'number':
                    num = int(args[0][1])
                    return Statement(('player', next(player for player, cards in cI.cardsOfPlayers.values() if num in cards)))
            case '[health]':
                if args[0][0] == 'number':
                    num = int(args[0][1])
                    return Statement(('number', cI.playerObjs[num].health))
            case '[power]':
                if args[0][0] == 'number':
                    num = int(args[0][1])
                    return Statement(('number', cI.playerObjs[num].power))
            case '[potency]':
                if args[0][0] == 'number':
                    num = int(args[0][1])
                    return Statement(('number', cI.playerObjs[num].potency))
            case '[symbolPoint]':
                if args[0][0] == 'number':
                    num = int(args[0][1])
                    if cI.cardObjs[num].effect is None: return 0
                    else: return Statement(('number', cI.cardObjs[num].effect.symbolPoint()))
            case '[powerCost]':
                if args[0][0] == 'number':
                    num = int(args[0][1])
                    if cI.cardObjs[num].effect is None: return 0
                    else: return Statement(('number', cI.cardObjs[num].powerCost))
            case '[NUMBER]':
                if args[0][0] == 'number':
                    return Statement.lex('tT')
                else:
                    return Statement.lex('tF')
            case '[PLAYER]':
                if args[0][0] == 'player':
                    return Statement.lex('tT')
                else:
                    return Statement.lex('tF')
            case '[CARD]':
                if args[0][0] == 'card':
                    return Statement.lex('tT')
                else:
                    return Statement.lex('tF')

    @staticmethod
    def convert(state, calcInstance: CalcInstance = CalcInstance(), convert: bool = True) -> 'Statement':
        """
        Expand special symbols of the statement to normal ones.
        """
        #TODO: Implement this method
        #TODO: Test this method
        res = deepcopy(state)

        i = 0
        while i < len(res):
            sym = res[i]
#           match sym[0]:
#               ...

        return res


    #Main functions
    def nextGameState(self) -> List[GameState]:
        """
        Returns the next game state.
        """
        #Initial gameplay
        if self.history == []:
            return [GameState(0, GameStateType.INITIAL)]

        gameStates = self.currentGameStates()
        playerActs = self.recentPlayerActions()

        if gameStates == (GameState(0, GameStateType.INITIAL),):
            return [GameState(0, GameStateType.CREATION)]
        elif gameStates == (GameState(0, GameStateType.CREATION),):
            #On creation phase, handle player choices of taking blanks
            votes = {
                **{i: False for i in range(len(self.players))},
                **{i: bl for i, bl in
                   ((playerAct.player, playerAct.info) for playerAct in playerActs)
                   }
            }
            count = len(tuple(0 for i in votes.values() if i))
            if count > len(tuple(0 for card in self.deck if Card() == card)):
                return [GameState.randPlayer(self, 1), GameState(0, GameStateType.EDITING)]
            else: return [GameState(0, GameStateType.EDITING)]
        elif gameStates[0] == GameState(0, GameStateType.EDITING):
            return [GameState(0, GameStateType.CLAIMING), GameState.randPlayer(self, 1)]
        elif gameStates[0] == GameState(0, GameStateType.CLAIMING) \
            and len(gameStates) == 2 and gameStates[1].type == GameStateType.RANDPLAYER:
            return [GameState(2, GameStateType.TURN, gameStates[1].info)]
        elif gameStates[0] == GameState(0, GameStateType.CLAIMING) \
            and len(gameStates) == 3 and gameStates[1].type == GameStateType.RANDPLAYER and \
                gameStates[2].type == GameStateType.TURN:
            if GameState.nextTurn(self, gameStates[2]) \
            != GameState(2, GameStateType.TURN, gameStates[1].info):
                return [GameState.nextTurn(self, gameStates[2])]
            else:
                return [GameState(0, GameStateType.MAIN), GameState.randPlayer(self, 1)]
        elif gameStates[0] == GameState(0, GameStateType.MAIN) and \
        gameStates[1].type == GameStateType.RANDPLAYER:
            if len(gameStates) == 2:
                return [GameState(2, GameStateType.TURN, gameStates[1].info)]
            elif len(gameStates) == 3 and len(playerActs) == 1:
                if playerActs[0].type == PlayerActionType.PLAY:
                    return [GameState(3, GameStateType.PROVE)]
                else:
                    return [GameState.nextTurn(self, gameStates[2])]
            elif len(gameStates) == 4:
                if gameStates[3].type == GameStateType.PROVE:
                    return [GameState(3, GameStateType.EFFECT)]
                elif gameStates[3].type == GameStateType.EFFECT:
                    return [GameState.nextTurn(self, gameStates[2])]
        raise GameException('Conditions not applied')

    def advance(self):
        """
        Advances to a new game state and returns self.
        """
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
                votesInd = (i for i, bl in ((playerAct.player, playerAct.info)
                                            for playerAct in playerActs) if bl)
                for i in votesInd:
                    self.players[i].cards.append(Card())
                    self.deck.remove(Card())
        if newGameStates[0] == GameState(0, GameStateType.MAIN):
            if newGameStates[1].type == GameStateType.RANDPLAYER and len(newGameStates) == 2:
                self.remaining = [True for _ in self.players]
                self.discardPile = []
                for player in self.players: player.playInit()
            if len(newGameStates) == 4 and newGameStates[3].type == GameStateType.PROVE:
                ... #TODO: Implement game effects here

        return self

    def action(self, playerAct: PlayerAction) -> bool:
        """
        Executes an action on this game instance, if it's valid.
        Returns whether the action is valid or not.
        """
        valid = self.actionValid(playerAct)
        if valid:
            playerActs = self.recentPlayerActions()
            self.history.append(playerAct)
            gameStates = self.currentGameStates()
            player = self.players[playerAct.player]

            #On initial gameplay, edit a card based on the player action
            if gameStates == (GameState(0, GameStateType.INITIAL),):
                player.editCard(playerAct.info[0], playerAct.info[1])

            #On editing phase, edit a card based on the player action
            if gameStates == (GameState(0, GameStateType.EDITING, None),):
                player.editCard(playerAct.info[0], playerAct.info[1])

            #On claiming phase, claim any card (not blank) from any player hand and buy it
            if gameStates[0] == GameState(0, GameStateType.CLAIMING, None):
                powerSpent = sum(self.players[playerId].cards[cardId].powerCost
                                 for playerId, cardId in playerAct.info)
                if powerSpent <= player.power:
                    for playerId, cardId in sorted(playerAct.info, key=lambda x: x[1], reverse=True):
                    #sorted function prevents deleting elements affecting indexes
                        player.cards.append(self.players[playerId].cards[cardId])
                        del self.players[playerId].cards[cardId]
                    player.power -= powerSpent

            #On main phase, ...
            if gameStates[0] == GameState(0, GameStateType.MAIN):
                #if PLAY, play the pair of cards
                if playerAct.type == PlayerActionType.PLAY:
                    self.dropPile += tuple(player.cards[x] for x in playerAct.info)
                    self.recentPlay = tuple(player.cards[x] for x in playerAct.info)
                    #Ensure deleting the right indexes
                    del player.cards[max(playerAct.info)]
                    del player.cards[min(playerAct.info)]
                #if DISCARD, discard card while raising its power cost by 2
                elif playerAct.type == PlayerActionType.DISCARD:
                    player.cards[playerAct.info].powerCost += 2
                    self.discardPile.append(player.cards[playerAct.info])
                    #Delete the card from their hand
                    del player.cards[playerAct.info]
                #if UNREMAIN, leave the main phase
                elif playerAct.type == PlayerActionType.UNREMAIN:
                    self.remaining[playerAct.player] = False
                #if CLAIMPLAY, claim the card to player for twice the power cost
                if playerAct.type == PlayerActionType.CLAIMPLAY:
                    powerSpent = sum(self.players[playerId].cards[cardId].powerCost
                                     for playerId, cardId in playerAct.info) * 2
                    if powerSpent <= player.power:
                        for playerId, cardId in sorted(playerAct.info, key=lambda x: x[1], reverse=True):
                        #sorted function prevents deleting elements affecting indexes
                            player.cards.append(self.players[playerId].cards[cardId])
                            del self.players[playerId].cards[cardId]
                        player.power -= powerSpent

        return valid

    def actionValid(self, playerAct: PlayerAction) -> bool:
        """
        Checks whether the given action is valid.
        """
        gameStates = self.currentGameStates()
        playerActs = self.recentPlayerActions()
        player = self.players[playerAct.player]

        if len(gameStates) == 0: return False
        if playerAct.valid(PlayerActionType.DEBUGACT): return True

        #Initial gameplay
        if gameStates == (GameState(0, GameStateType.INITIAL, None),) and \
        all(playerAct.valid(PlayerActionType.EDIT) for playerAct in playerActs + (playerAct,)):
            return True

        #Creation phase
        if gameStates == (GameState(0, GameStateType.CREATION, None),) and \
        all(playerAct.valid(PlayerActionType.TAKEBLANK)
            for playerAct in playerActs + (playerAct,)) and \
        _allUnique(playerActs + (playerAct,), key=lambda x: x.player):
            return True

        #Editing phase
        if gameStates == (GameState(0, GameStateType.EDITING, None),) and \
        all(playerAct.valid(PlayerActionType.EDIT) for playerAct in playerActs + (playerAct,)) and \
        _allUnique(playerActs + (playerAct,), key=lambda x: x.player):
            return True

        #Claiming phase
        if gameStates[0] == GameState(0, GameStateType.CLAIMING, None) and \
        len(gameStates) == 3 and gameStates[2].type == GameStateType.TURN and \
        all(playerAct.valid(PlayerActionType.CLAIM)
            for playerAct in playerActs + (playerAct,)) and \
        len(playerActs) == 0 and playerAct.player == gameStates[2].info and \
        len(playerAct.info) <= 8 and not \
        any(self.players[playerId].cards[cardId] == Card() for playerId, cardId in playerAct.info):
            return True

        #Main phase
        if gameStates[0] == GameState(0, GameStateType.MAIN) and self.remaining[playerAct.player]:
            #Before proving game state
            if len(gameStates) == 3 and gameStates[2].type == GameStateType.TURN and \
            len(playerActs) == 0 and \
            playerAct.valid(
                (PlayerActionType.PLAY,
                 PlayerActionType.DISCARD,
                 PlayerActionType.CLAIMPLAY,
                 PlayerActionType.UNREMAIN
                )):
                #Playing action
                if playerAct.type == PlayerActionType.PLAY:
                    mainCard: Card = player.cards[playerAct.info[0]]

                    #Make sure not to play blank cards
                    if Card() in (mainCard, player.cards[playerAct.info[1]]): return False
                    if mainCard.effect.symbolPoint() > player.cards[playerAct.info[1]].effect.symbolPoint():
                        return False
                    if self.recentPlay is not None:
                        oppoMainCard: Card = self.recentPlay[0]
                        if mainCard.powerCost > oppoMainCard.powerCost: return False
                        if (not oppoMainCard.tag.beat(mainCard.tag)) or \
                        (mainCard.effect.symbolPoint() < oppoMainCard.effect.symbolPoint()):
                            return True
                    else: return True
                #Discard and unremain action
                elif playerAct.type in [PlayerActionType.DISCARD, PlayerActionType.UNREMAIN]:
                    return True
                #Claim action in main phase
                if playerAct.type == PlayerActionType.CLAIMPLAY:
                    return len(playerAct.info) <= 8 and \
                    not any(
                        self.players[playerId].cards[cardId] == Card()
                        for playerId, cardId in playerAct.info
                    )
            #Proving game state
            if len(gameStates) == 4 and gameStates[3].type == GameStateType.PROVE and \
            playerAct.valid(PlayerActionType.PROVE):
                proof: Proof = playerAct.info[1]

                if isinstance(playerAct.info[0], int):
                    #No reference to nonexistent/contradicting opposing proofs or to itself
                    if playerAct.info[0] > len(playerActs) and \
                    isinstance(playerActs[playerAct.info[0]].info[0], int):
                        return False
                    #Must be contradictory in itself
                    if not proof.contradictory():
                        return False

                #Must have subproofs equal to player
                if playerAct.info[1].subproofs != player.subproofs:
                    return False

                axioms = self.startAxioms(playerAct.info[0])
                proofAxioms = tuple(
                    state for state, tag in
                    zip(proof.statements, proof.stateTags) if tag == StateTag.AXIOM
                )
                return axioms == proofAxioms
        ...
        return False
