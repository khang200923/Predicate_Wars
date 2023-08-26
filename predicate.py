"""
Provides essential classes and methods for creating and proving predicate logic statements.
"""
from copy import deepcopy
from dataclasses import dataclass, field
from enum import Enum
import math
import random
import re
from typing import Any, Callable, List, Optional, Sequence, Set, Tuple

def _mappableDict(dct: dict) -> bool:
    """
    Returns if dict values don't overlap.
    """
    return len(set(dct.values())) == len(dct.values())

def _checkSubSeq(subseq: Sequence, seq: Sequence) -> bool: #From https://stackoverflow.com/questions/425604/best-way-to-determine-if-a-sequence-is-in-another-sequence
    """
    Return if the subsequence is in the sequence.
    """
    i, n, m = -1, len(seq), len(subseq)
    if len(subseq) == 0: return True
    try:
        while True:
            i = seq.index(subseq[0], i + 1, n - m + 1)
            if subseq == seq[i:i + m]:
                return True
    except ValueError:
        return False

def _subSeqIndexes(subseq: Sequence, seq: Sequence) -> Tuple[int]: #From https://stackoverflow.com/questions/425604/best-way-to-determine-if-a-sequence-is-in-another-sequence
    """
    Return starting indexes of the subsequence in the sequence.
    """
    i, n, m = -1, len(seq), len(subseq)
    matches = []
    try:
        while True:
            i = seq.index(subseq[0], i + 1, n - m + 1)
            if subseq == seq[i:i + m]:
                matches.append(i)
    except ValueError:
        return tuple(matches)

def _checkSeqForm(seq: Sequence, start: Sequence, end: Sequence, mid: Sequence=(), startEndMatch = lambda x, y: x == y) -> bool:
    """
    Check the sequence if it is the form of [start..., ?, mid..., ?, end...].
    """
    if not startEndMatch(seq[:len(start)], start): return False
    if not startEndMatch(seq[-len(end):], end): return False
    if not _checkSubSeq(mid, seq[len(start):-len(end)]): return False
    return True

def _seqFormOptionalsIndexes(seq: Sequence, start: Sequence, end: Sequence, mid: Sequence = (), midcond: Callable[[int], bool] = lambda x: True, startEndMatch = lambda x, y: x == y) -> Tuple[Tuple, ...] | None:
    """
    Return indexes of optional subsequences in the sequence of the seq form.
    ((subseq1start, subseq2end), ((subseq1end, subseq2start),...)?)
    Conditional function of mid filter is fed starting index to each mid
    """
    if _checkSeqForm(seq, start, end, mid, startEndMatch):
        if len(mid) == 0:
            return ((len(start), len(seq) - len(end)),)
        else:
            return ((len(start), len(seq) - len(end)),
                tuple((index + len(start), index + len(start) + len(mid)) for index in _subSeqIndexes(mid, seq[len(start):-len(end)]) if midcond(index + len(start)))
            )
    return None

def _smallestMissingInteger(sequence: Sequence[int], ground=0, default=0) -> int:
    if len(sequence) == 0:
        return default
    elements = sorted(set(sequence))
    if elements[0] - ground >= 1:
        return ground
    for element, change in ((elements[i], elements[i+1] - elements[i]) for i in range(len(elements)-1)):
        if change != 1:
            return element + 1
    return max(elements) + 1


#Export constants and functions
gameFuncNames = ['[randPlayer]', '[randCard]', '[chosenPlayer]', '[chosenCard]', '[playerOfChosenCard]', '[health]', '[power]', '[potency]', '[symbolPoint]', '[powerCost]']
predGFuncNames = ['[NUMBER]', '[PLAYER]', '[CARD]']
predAFuncNames = ['[CLAIM]', '[ATK]', '[HEAL]', '[ADDPOWER]', '[SUBPOWER]']

varDetector = r'([a-z](_[0-9]+)?)|([0-9]+)'

symbolsType = (
    ('gameFuncName', '|'.join([x.replace("[", r"\[").replace("]", r"\]") for x in gameFuncNames])),
    ('predGFuncName', '|'.join([x.replace("[", r"\[").replace("]", r"\]") for x in predGFuncNames])),
    ('predAFuncName', '|'.join([x.replace("[", r"\[").replace("]", r"\]") for x in predAFuncNames])),
    ('distVar', r'[a-z]_[0-9]+'),
    ('distPred', r'[A-Z]_[0-9]+'),
    ('truth', r't[TF]'),
    ('quanti', r'forall|exists'),
    ('connect', r'not\s|\sand\s|\sor\s|\simply\s'),
    ('oper', r'[+\-*/%]|f/|c/'),
    ('compare', r'[<>]'),
    ('var', r'[a-z]'),
    ('pred', r'[A-Z]'),
    ('equal', r'='),
    ('comma', r','),
    ('bracket', r'[\(\)]'),
    ('number', r'[0-9]+'),
    ('space', r'\s'),
)

varSymbols = ('distVar', 'var')
predSymbols = ('distPred', 'pred')

def symbolTypeCalc(symbol: str) -> str | None:
    return next((name for name, cond in symbolsType if re.match('^{}$'.format(cond), symbol)), None)

def symbolTrans(symbol: str) -> Tuple[str, ...] | None:
    symType = symbolTypeCalc(symbol)
    if symType is None:
        return None
    if symType == 'var':
        return (symType, str(ord(symbol.lower()) - ord('a') + 1))
    if symType == 'pred':
        return (symType, str(ord(symbol.lower()) - ord('a') + 1))
    if symType == 'distVar':
        return (symType, str(ord(symbol[0].lower()) - ord('a') + 1), symbol[2:])
    if symType == 'distPred':
        return (symType, str(ord(symbol[0].lower()) - ord('a') + 1), symbol[2:])
    if symType == 'connect':
        if 'not' in symbol:
            return (symType, 'not')
        return (symType, symbol[1:-1])
    if symType in ['gameFuncName', 'predGFuncName', 'predAFuncName', 'truth', 'quanti', 'bracket', 'number', 'oper', 'compare']:
        return (symType, symbol)
    return (symType,)

@dataclass
class Statement:
    """
    A statement in predicate logic
    """
    statement: Tuple[Tuple, ...]

    @staticmethod
    def lex(string: str) -> 'Statement':
        """
        Tokenize statement from string.
        """
        tokens = []
        unLexed = string
        while unLexed:
            typeDetect = tuple(re.match(regex, unLexed) for _, regex in symbolsType)
            if any(typeDetect):
                typeDetectIndex = tuple(re.match(regex, unLexed).start() if re.match(regex, unLexed) else float('inf') for _, regex in symbolsType)
                nextTokenMatch = typeDetect[typeDetectIndex.index(min(typeDetectIndex))]
                nextToken = symbolTrans(nextTokenMatch.group())
                if nextToken != ('space',):
                    tokens.append(nextToken)
                unLexed = unLexed[nextTokenMatch.end():]
            else:
                raise ValueError("Invalid string at '{}'".format(unLexed))
        return Statement(tuple(tokens))

    def __str__(self) -> str:
        res = ''
        for symType, *symVal in self:
            if symType is None:
                pass
            elif symType == 'var':
                res += chr(int(symVal[0]) - 1 + ord('a'))
            elif symType == 'pred':
                res += chr(int(symVal[0]) - 1 + ord('A'))
            elif symType == 'distVar':
                res += chr(int(symVal[0]) - 1 + ord('a')) + '_' + symVal[1]
            elif symType == 'distPred':
                res += chr(int(symVal[0]) - 1 + ord('A')) + '_' + symVal[1]
            elif symType == 'connect':
                if 'not' in symVal[0]:
                    res += 'not '
                else: res += ' {} '.format(symVal[0])
            elif symType in ['gameFuncName', 'predGFuncName', 'predAFuncName', 'truth', 'quanti', 'bracket', 'number', 'oper', 'compare']:
                res += symVal[0]
            elif symType == 'equal':
                res += '='
            elif symType == 'comma':
                res += ','
            else:
                res += '{?}'
        return res

    def __getitem__(self, key):
        return self.statement[key]

    def __setitem__(self, key, value):
        self.statement = list(self.statement)
        self.statement[key] = value
        self.statement = tuple(self.statement)

    def __len__(self):
        return len(self.statement)

    def eq(self, statement: 'Statement', startingMaps = None) -> Tuple[bool, dict[Tuple, Tuple]]:
        """
        Check if two statements are functionally equivalent
        """
        if startingMaps == None: startingMaps = {}
        assert isinstance(statement, Statement), 'must compare with a valid instance of class "Statement"'
        maps = deepcopy(startingMaps)
        for sym1, sym2 in zip(self, statement):
            if len(sym1) != len(sym2):
                return (False, maps)
            if (sym1[0] in varSymbols and sym2[0] in varSymbols) or \
            (sym1[0] in predSymbols and sym2[0] in predSymbols):
                if sym1 in maps:
                    if maps[sym1] != sym2:
                        return (False, maps)
                    else: continue
                else:
                    maps[sym1] = sym2
                    continue
            elif sym1 != sym2:
                return (False, maps)
        return (_mappableDict(maps), maps)

    def syms(self) -> Set[Tuple[str]]:
        """
        Returns vars and preds in the statement.
        """
        syms = set()
        for sym in self:
            if sym[0] in varSymbols or sym[0] in predSymbols:
                syms.add(sym)
        return syms

    def __eq__(self, statement: 'Statement', maps = None) -> bool:
        if maps is None: maps = {}
        return self.eq(statement, maps)[0]

    def __add__(self, statement: 'Statement') -> 'Statement':
        assert isinstance(statement, Statement), 'must add with a valid instance of class "Statement"'
        return Statement(self.statement + statement.statement)

    def form(self, start: Tuple[Tuple, ...]=(), end: Tuple[Tuple, ...]=(), mid: Tuple[Tuple, ...]=(), startingMaps: dict[Tuple, Tuple]={}, opt1obj: bool = False, opt2obj: bool = False) -> bool:
        """
        Checks if the statement form fits the statement.
        """

        #Check form first
        if not _checkSeqForm(self, start, end, mid, startEndMatch=lambda x, y: Statement(x) == Statement(y)): return False

        #Prepare maps
        maps = deepcopy(startingMaps)
        startEndIndexes = _seqFormOptionalsIndexes(self, start, end, mid, startEndMatch=lambda x, y: Statement(x) == Statement(y))[0]
        check = Statement(self[:startEndIndexes[0]]).eq(Statement(start), startingMaps=maps)
        if not check[0]: return False
        maps = check[1]
        check = Statement(self[startEndIndexes[1]:]).eq(Statement(end), startingMaps=maps)
        if not check[0]: return False
        maps = check[1]

        if opt1obj: opt1wellmethod = 'wellformedobj'
        else: opt1wellmethod = 'wellformed'

        #Check for special case mid
        if mid:
            if opt2obj: opt2wellmethod = 'wellformedobj'
            else: opt2wellmethod = 'wellformed'
            minIndexes = _seqFormOptionalsIndexes(self, start, end, mid, midcond=lambda index: \
                        getattr(Statement(self[startEndIndexes[0]:index]), opt1wellmethod)() and \
                        getattr(Statement(self[index+len(mid):startEndIndexes[1]]), opt2wellmethod)() \
            , startEndMatch=lambda x, y: Statement(x) == Statement(y))[1]
            for minIndex in minIndexes:
                if self[minIndex[0] : minIndex[1]] == mid:
                    return True
            return False
        if not getattr(Statement(self[startEndIndexes[0]:startEndIndexes[1]]), opt1wellmethod)():
            return False

        #All filters passed - great!
        return True

    def formulasInForm(self, start: Tuple[Tuple, ...]=(), end: Tuple[Tuple, ...]=(), mid: Tuple[Tuple, ...]=(), startingMaps: dict[Tuple, Tuple]={}, opt1obj: bool = False, opt2obj: bool = False) -> Tuple[Tuple['Statement', ...], ...] | None:
        """
        Returns all optional formulas (or objs) in statement if it fits with the statement form.
        """

        #Check form first
        if not _checkSeqForm(self, start, end, mid, startEndMatch=lambda x, y: Statement(x) == Statement(y)): return None

        #Prepare maps
        maps = deepcopy(startingMaps)
        startEndIndexes = _seqFormOptionalsIndexes(self, start, end, mid, startEndMatch=lambda x, y: Statement(x) == Statement(y))[0]
        check = Statement(self[:startEndIndexes[0]]).eq(Statement(start), startingMaps=maps)
        if not check[0]: return None
        maps = check[1]
        check = Statement(self[startEndIndexes[1]:]).eq(Statement(end), startingMaps=maps)
        if not check[0]: return None
        maps = check[1]

        if opt1obj: opt1wellmethod = 'wellformedobj'
        else: opt1wellmethod = 'wellformed'

        #Check for special case mid
        if mid:
            if opt1obj: opt1wellmethod = 'wellformedobj'
            else: opt1wellmethod = 'wellformed'
            if opt2obj: opt2wellmethod = 'wellformedobj'
            else: opt2wellmethod = 'wellformed'
            minIndexes = _seqFormOptionalsIndexes(self, start, end, mid, midcond=lambda index: \
                        getattr(Statement(self[startEndIndexes[0]:index]), opt1wellmethod)() and \
                        getattr(Statement(self[index+len(mid):startEndIndexes[1]]), opt2wellmethod)() \
            , startEndMatch=lambda x, y: Statement(x) == Statement(y))[1]
            for minIndex in minIndexes:
                if self[minIndex[0] : minIndex[1]] == mid:
                    return tuple( ( Statement(self[startEndIndexes[0]:minIndex[0]]), Statement(self[minIndex[1]:startEndIndexes[1]]) ) for minIndex in minIndexes)
            return None
        else:
            if not getattr(Statement(self[startEndIndexes[0]:startEndIndexes[1]]), opt1wellmethod)():
                return None
        return ( ( Statement(self[startEndIndexes[0]:startEndIndexes[1]],) ,) ,)

    def wellformedobj(self) -> bool:
        """
        Check whether the object is well-formed.
        """

        if len(self) == 0: return False
        if len(self) == 1:
            return self.statement[0][0] in ('distVar', 'var', 'number', 'gameFuncName')
        if len(self) > 2:
            #Function syntax
            if self[1] == ('bracket', '(') and self[-1] == ('bracket', ')') and \
            self[0][0] in ('distVar', 'var', 'number', 'gameFuncName'):
                paramsLeft = self[2:-1]
                while len(paramsLeft) > 0:
                    paramEndIndex = next((index for index in range(len(paramsLeft) + 1) if Statement(paramsLeft[:index]).wellformedobj() and not (index < len(paramsLeft) and not paramsLeft[index] == ('comma',))), None)
                    if paramEndIndex is None: return Statement(paramsLeft).wellformedobj()
                    paramsLeft = paramsLeft[paramEndIndex+1:]
                return True

            #Operator syntax
            elif self.form((
                ('bracket', '('),
            ), (
                ('bracket', ')'),
            ), (
                ('oper', '+'),
            ),
            opt1obj=True,
            opt2obj=True,
            ): return True
            elif self.form((
                ('bracket', '('),
            ), (
                ('bracket', ')'),
            ), (
                ('oper', '-'),
            ),
            opt1obj=True,
            opt2obj=True,
            ): return True
            elif self.form((
                ('bracket', '('),
            ), (
                ('bracket', ')'),
            ), (
                ('oper', '*'),
            ),
            opt1obj=True,
            opt2obj=True,
            ): return True
            elif self.form((
                ('bracket', '('),
            ), (
                ('bracket', ')'),
            ), (
                ('oper', '/'),
            ),
            opt1obj=True,
            opt2obj=True,
            ): return True
            elif self.form((
                ('bracket', '('),
            ), (
                ('bracket', ')'),
            ), (
                ('oper', 'f/'),
            ),
            opt1obj=True,
            opt2obj=True,
            ): return True
            elif self.form((
                ('bracket', '('),
            ), (
                ('bracket', ')'),
            ), (
                ('oper', 'c/'),
            ),
            opt1obj=True,
            opt2obj=True,
            ): return True
            elif self.form((
                ('bracket', '('),
            ), (
                ('bracket', ')'),
            ), (
                ('oper', '%'),
            ),
            opt1obj=True,
            opt2obj=True,
            ): return True
        return False


    def wellformed(self) -> bool:
        """
        Check whether the statement is well-formed.
        """

        if len(self) == 0: return False
        if len(self) == 1:
            return self[0][0] in ('distPred', 'truth', 'pred')

        #For All syntax
        if self.form(
            (
                ('bracket', '('),
                ('quanti', 'forall'),
                ('bracket', '('),
                ('var', '0'),
                ('bracket', ')'),
            ),
            (
                ('bracket', ')'),
            ),
        ): return True

        #Exists syntax
        if self.form(
            (
                ('bracket', '('),
                ('quanti', 'exists'),
                ('bracket', '('),
                ('var', '0'),
                ('bracket', ')'),
            ),
            (
                ('bracket', ')'),
            ),
        ): return True

        #Not syntax
        if self.form(
            (
                ('bracket', '('),
                ('connect', 'not'),
            ),
            (
                ('bracket', ')'),
            ),
        ): return True

        #And syntax
        if self.form(
            (
                ('bracket', '('),
            ),
            (
                ('bracket', ')'),
            ),
            (
                ('connect', 'and'),
            ),
        ): return True

        #Or syntax
        if self.form(
            (
                ('bracket', '('),
            ),
            (
                ('bracket', ')'),
            ),
            (
                ('connect', 'or'),
            ),
        ): return True

        #Imply syntax
        if self.form(
            (
                ('bracket', '('),
            ),
            (
                ('bracket', ')'),
            ),
            (
                ('connect', 'imply'),
            ),
        ): return True

        #Equal syntax
        if self.form(
            (
                ('bracket', '('),
            ),
            (
                ('bracket', ')'),
            ),
            (
                ('equal',),
            ),
            opt1obj=True,
            opt2obj=True,
        ): return True

        #Comparator syntax
        if self.form(
            (
                ('bracket', '('),
            ),
            (
                ('bracket', ')'),
            ),
            (
                ('compare', '<'),
            ),
            opt1obj=True,
            opt2obj=True,
        ): return True

        if self.form(
            (
                ('bracket', '('),
            ),
            (
                ('bracket', ')'),
            ),
            (
                ('compare', '>'),
            ),
            opt1obj=True,
            opt2obj=True,
        ): return True

        #Function syntax
        if self[1] == ('bracket', '(') and self[-1] == ('bracket', ')') and \
        self[0][0] in ('predGFuncName', 'predAFuncName', 'distPred', 'pred'):
            paramsLeft = self[2:-1]
            while len(paramsLeft) > 0:
                paramEndIndex = next((index for index in range(len(paramsLeft) + 1) if Statement(paramsLeft[:index]).wellformedobj() and not (index < len(paramsLeft) and not paramsLeft[index] == ('comma',))), None)
                if paramEndIndex is None: return Statement(paramsLeft).wellformedobj()
                paramsLeft = paramsLeft[paramEndIndex+1:]
            return True

        return False

    def substitute(self, startingMap: dict[Tuple, Tuple], obj: bool = False, mappableCheck: bool = True) -> 'Statement | None':
        """
        Maps each symbol in statement with a map, and return the resulting statement.
        When the result is not well-formed, return None
        Overlapping also returns None
        """
        map = {sym: sym for sym in self.syms()}
        map.update(startingMap)
        if mappableCheck and not _mappableDict(map): return None
        res = Statement(tuple(map.get(symbol, symbol) for symbol in self))
        if obj:
            if not res.wellformedobj(): return None
        else:
            if not res.wellformed(): return None
        return res

    def complexSubstitute(self, startingMap: dict[Tuple, Tuple[Tuple]], obj: bool = False) -> 'Statement | None':
        """
        Maps each symbol in statement with a map (replacing occurences with one or more elems), and return the resulting statement.
        When the result is not well-formed, return None
        """
        mapPlace = {}
        indexAdd = 0
        for fro, tos in startingMap.items(): #Each types of occurence
            for i, val in enumerate(self):
                if val == fro: #If found occurence, change it
                    mapPlace[i + indexAdd] = tos
                    indexAdd += len(tos) - 1
        listSymbols = list(deepcopy(self.statement))
        for ind, val in sorted(mapPlace.items(), key=lambda x: x[0]):
            listSymbols[ind:ind+1] = val
        res = deepcopy(self)
        res.statement = tuple(listSymbols)
        if obj:
            if not res.wellformedobj(): return None
        else:
            if not res.wellformed(): return None
        return res

    def symbolPoint(self) -> int:
        """
        Return symbol point of this statement.
        """
        res = 0
        for symType, *_ in self:
            if symType in ['truth', 'bracket', 'comma']: continue
            elif symType in ['quanti', 'distVar', 'distPred']: res += 2
            elif symType in ['gameFuncName', 'predGFuncName']: res += 4
            elif symType in ['predAFuncName']: res += 8
            else: res += 1
        return res

class StateTag(Enum):
    AXIOM = 0
    LEMMA = 1

class InferType(Enum):
    ImpliInst = 12
    ExpliInst = 11
    ModPonens = 0
    UniversalInst = 2
    UniversalGenr = 3
    UniversalGenrWRef = 25
    ExistentialInst = 4
    ExistentialGenr = 5
    Conjunc = 6
    Simplific = 7
    FalsyAND = 15
    Addition = 8
    FalsyOR = 16
    UnivModPonens = 9
    ExistModPonens = 10
    Truth = 13
    Falsehood = 14
    SubsProp = 17
    Identity = 18
    SymmProp = 19
    TransProp = 20
    SubsPropEq = 26
    OpSimplify = 21
    Comparison = 22

    CondProof = 23
    IndProof = 24

premiseUsesOfInferType = { #(p1, p2, x, z1, z2, z3)
    InferType.ImpliInst: (True, True, False, False, False, False),
    InferType.ExpliInst: (True, True, False, False, False, False),
    InferType.ModPonens: (True, True, False, False, False, False),
    InferType.UniversalInst: (True, False, True, False, False, False),
    InferType.UniversalGenr: (True, False, True, False, False, False),
    InferType.UniversalGenrWRef: (True, True, False, False, False, False),
    InferType.ExistentialInst: (True, False, False, False, False, False),
    InferType.ExistentialGenr: (True, False, False, False, False, False),
    InferType.Conjunc: (True, True, False, False, False, False),
    InferType.Simplific: (True, False, False, False, False, False),
    InferType.FalsyAND: (True, False, False, False, False, False),
    InferType.Addition: (True, False, False, False, False, False),
    InferType.FalsyOR: (True, True, False, False, False, False),
    InferType.UnivModPonens: (True, True, False, False, False, False),
    InferType.ExistModPonens: (True, True, False, False, False, False),
    InferType.Truth: (False, False, False, False, False, False),
    InferType.Falsehood: (False, False, False, False, False, False),
    InferType.SubsProp: (True, False, True, False, False, False),
    InferType.Identity: (False, False, True, False, False, False),
    InferType.SymmProp: (True, False, False, False, False, False),
    InferType.TransProp: (True, True, False, False, False, False),
    InferType.SubsPropEq: (True, False, True, False, False, False),
    InferType.OpSimplify: (True, False, False, False, False, False),
    InferType.Comparison: (True, False, False, False, False, False),

    InferType.CondProof: (True, False, False, True, True, False),
    InferType.IndProof: (False, False, True, True, True, True),
}

class InferenceError(Exception): pass

@dataclass
class ProofBase:
    """
    Contains a list of Statements, with no subproof, and a list of inference.
    """
    statements: List[Statement] = field(default_factory=list)
    stateTags: List[StateTag] = field(default_factory=list)
                #[(inferType, premise1index, premise2index, object, conclusionIndex)...]
    inferences: List[Tuple[InferType, int, int, Statement, int] | None] = field(default_factory=list)

    @staticmethod
    def convert(strAxioms: Tuple[str], inferences: Optional[List[Tuple[InferType | None, int, int | None, Statement, int | str]]] = None) -> 'ProofBase':
                                                   #[(inferType, premise1index, premise2index, object, conclusionIndex | conclusion)...]
        """
        Convert from strings of axioms to proof.
        """
        if inferences is None:
            inferences = []
        states = [Statement.lex(state) for state in strAxioms]
        proof = ProofBase(states, [StateTag.AXIOM for _ in states], [None for _ in states])
        for index, (_, premise1Index, premise2Index, object, conclusionI) in enumerate(inferences):
            if isinstance(conclusionI, int):
                proof = proof.infer(premise1Index, premise2Index, Statement.lex(object), conclusionI)
            elif isinstance(conclusionI, str):
                proof = proof.infer(premise1Index, premise2Index, Statement.lex(object), Statement.lex(conclusionI))
            else:
                raise TypeError('ProofBase.convert only supports conclusionI param types of int and str, your type is: ' + str(type(conclusionI)) + 'at index ' + str(index))
        return proof

    def __getitem__(self, index: int) -> dict[str, Any]:
        try:
            return {'state': self.statements[index], 'tag': self.stateTags[index], 'infer': self.inferences[index]}
        except IndexError:
            return {'state': self.statements[index], 'tag': self.stateTags[index], 'infer': None}

    def syms(self) -> Set[Tuple]:
        """
        Returns vars and preds used in proof.
        """
        return {sym for state in self.statements for sym in state.syms()}

    def subProof(self) -> Set[Tuple]:
        """
        Check if this ProofBase can be a subproof.
        """

        if isinstance(self, Proof): return False
        return self.stateTags[0] == StateTag.AXIOM and all(tag == StateTag.LEMMA for tag in self.stateTags[1:])

    def symsWithout(self, stateIndex) -> Set[Tuple]:
        """
        Returns vars and preds used in proof, without the statement on specified index.
        """
        return {sym for state in (state for index, state in enumerate(self.statements) if index != stateIndex) for sym in state.syms()}

    def unusedVarSuggester(self, randomClass = random):
        """
        Suggests an unused variable name based on existing syms in random.
        """
        char = randomClass.randint(1, 26)
        syms = self.syms()
        syms = {sym for sym in syms if sym[0] in ['var', 'distVar'] and sym[1] == str(char)}
        height = _smallestMissingInteger(tuple(-1 if sym[0] == 'var' else int(sym[2]) for sym in syms), default=-1, ground=-1)
        if height == -1: return ('var', str(char))
        return ('distVar', str(char), str(height))

    def inferConclusions(self, inferType: InferType, premise1Index: int, premise2Index: int = None, object: Statement = Statement(())) -> Tuple[Statement]:
        """
        Infers the proof and yields conclusions.
        """

        premiseUses = premiseUsesOfInferType[inferType]
        if premiseUses[0]:
            premise1: Statement = self[premise1Index]['state']
            if not premise1.wellformed(): raise InferenceError('Premise 1 is ill-formed')
        if premiseUses[1]:
            premise2: Statement = self[premise2Index]['state']
            if not premise2.wellformed(): raise InferenceError('Premise 2 is ill-formed')
        if premiseUses[2]:
            if not object.wellformedobj(): raise InferenceError('Object is ill-formed')

        conclusions = []

        match inferType:
            case InferType.ImpliInst:
                A = premise1
                try: notA = premise1.formulasInForm(
                    (
                        ('bracket', '('),
                        ('connect', 'not'),
                    ),
                    (
                        ('bracket', ')'),
                    ),
                )[0][0]
                except TypeError: notA = None
                B = premise2
                try: notB = premise2.formulasInForm(
                    (
                        ('bracket', '('),
                        ('connect', 'not'),
                    ),
                    (
                        ('bracket', ')'),
                    ),
                )[0][0]
                except TypeError: notB = None
                if notA:
                    if notB:
                        conclusions.append(
                            Statement( (('bracket', '('),) ) + \
                            notA + \
                            Statement( (('connect', 'imply'),) ) + \
                            notB + \
                            Statement( (('bracket', ')'),) )
                        )
                    conclusions.append(
                        Statement( (('bracket', '('),) ) + \
                        notA + \
                        Statement( (('connect', 'imply'),) ) + \
                        B + \
                        Statement( (('bracket', ')'),) )
                    )
                conclusions.append(
                    Statement( (('bracket', '('),) ) + \
                    A + \
                    Statement( (('connect', 'imply'),) ) + \
                    B + \
                    Statement( (('bracket', ')'),) )
                )
            case InferType.ExpliInst:
                A = premise1
                try: notB = premise2.formulasInForm(
                    (
                        ('bracket', '('),
                        ('connect', 'not'),
                    ),
                    (
                        ('bracket', ')'),
                    ),
                )[0][0]
                except TypeError: notB = None
                if notB:
                    conclusions.append(
                        Statement( (('bracket', '('), ('connect', 'not'), ('bracket', '(')) ) + \
                        A + \
                        Statement( (('connect', 'imply'),) ) + \
                        notB + \
                        Statement( (('bracket', ')'), ('bracket', ')')) )
                    )
            case InferType.ModPonens:
                A = premise2
                try: Bb = premise1.formulasInForm(
                    (
                        ('bracket', '('),
                    ),
                    (
                        ('bracket', ')'),
                    ),
                    (
                        ('connect', 'imply'),
                    ),
                )[0]
                except TypeError: Bb = None
                if Bb and tuple(Bb[0]) == tuple(A): conclusions.append(Bb[1])
            case InferType.UniversalInst:
                try: A = premise1.formulasInForm(
                    (
                        ('bracket', '('),
                        ('quanti', 'forall'),
                        ('bracket', '('),
                        ('var', '0'),
                        ('bracket', ')'),
                    ),
                    (
                        ('bracket', ')'),
                    ),
                )[0][0]
                except TypeError: pass
                else:
                    if len(object) == 1 and object[0][0] in ('var', 'distVar'):
                        eq, maps = Statement( (
                            ('bracket', '('),
                            ('quanti', 'forall'),
                            ('bracket', '('),
                            ('var', '0'),
                            ('bracket', ')'),
                        ) ).eq(Statement(premise1[:5]))
                        assert eq, 'brah'
                        thatVar = maps[('var', '0')]
                        conclusions.append(A.substitute({thatVar: object[0]}))
                        conclusions.append(A.substitute({thatVar: self.unusedVarSuggester()}))
                    else:
                        raise InferenceError('Object must be a single-letter variable')
            case InferType.UniversalGenr:
                if (len(object) == 1 and object[0][0] in ('var', 'distVar')) and not object[0] in self.symsWithout(premise1Index):
                    uniqueVars1 = (object[0], self.unusedVarSuggester())
                    for uniqueVar in uniqueVars1:
                        conclusions.append(Statement( (
                            ('bracket', '('),
                            ('quanti', 'forall'),
                            ('bracket', '('),
                            uniqueVar,
                            ('bracket', ')'),
                        ) ) + premise1 + Statement( (
                            ('bracket', ')'),
                        ) ))
            case InferType.UniversalGenrWRef:
                if premise2.form(
                        (
                            ('bracket', '('),
                            ('quanti', 'forall'),
                            ('bracket', '('),
                            ('var', '0'),
                            ('bracket', ')'),
                        ), (
                            ('bracket', ')'),
                        )
                    ):
                    x = premise2[3]
                    conclusions.append(Statement( (
                        ('bracket', '('),
                        ('quanti', 'forall'),
                        ('bracket', '('),
                        x,
                        ('bracket', ')'),
                    ) ) + premise1 + Statement( (
                        ('bracket', ')'),
                    ) ))
            case InferType.ExistentialInst:
                try: A = premise1.formulasInForm(
                    (
                        ('bracket', '('),
                        ('quanti', 'exists'),
                        ('bracket', '('),
                        ('var', '0'),
                        ('bracket', ')'),
                    ),
                    (
                        ('bracket', ')'),
                    ),
                )[0][0]
                except TypeError: A = None
                if A:
                    conclusions.append(A)
            case InferType.ExistentialGenr:
                for var in (sym for sym in premise1.syms() if 'ar' in sym[0]):
                    conclusions.append(
                        Statement((
                            ('bracket', '('),
                            ('quanti', 'exists'),
                            ('bracket', '('),
                            var,
                            ('bracket', ')'),
                        )) + premise1 + Statement((
                            ('bracket', ')'),
                        ))
                    )
            case InferType.Conjunc:
                conclusions.append(
                    Statement((
                        ('bracket', '('),
                    )) + premise1 + Statement((
                        ('connect', 'and'),
                    )) + premise2 + Statement((
                        ('bracket', ')'),
                    ))
                )
            case InferType.Simplific:
                try: A, B = premise1.formulasInForm(
                    (('bracket', '('),),
                    (('bracket', ')'),),
                    (('connect', 'and'),),
                )[0]
                except TypeError: A, B = (None, None)
                if A and B:
                    conclusions.append(A)
                    conclusions.append(B)
            case InferType.FalsyAND:
                try: A = premise1.formulasInForm(
                    (('bracket', '('),
                     ('connect', 'not')),
                    (('bracket', ')'),),
                )[0][0]
                except TypeError: A = None
                if A:
                    for B in self.statements:
                        conclusions.append(
                            Statement((
                                ('bracket', '('),
                                ('connect', 'not'),
                                ('bracket', '(')
                            )) +
                            A +
                            Statement((
                                ('connect', 'and'),
                            )) +
                            B +
                            Statement((
                                ('bracket', ')'),
                                ('bracket', ')'),
                            ))
                        )
                        conclusions.append(
                            Statement((
                                ('bracket', '('),
                                ('connect', 'not'),
                                ('bracket', '(')
                            )) +
                            A +
                            Statement((
                                ('connect', 'and'),
                                ('bracket', '('),
                                ('connect', 'not'),
                            )) +
                            B +
                            Statement((
                                ('bracket', ')'),
                                ('bracket', ')'),
                                ('bracket', ')'),
                            ))
                        )
            case InferType.Addition:
                for premise2 in self.statements:
                    conclusions.append(
                        Statement((
                            ('bracket', '('),
                        )) +
                        premise1 +
                        Statement((
                            ('connect', 'or'),
                        )) +
                        premise2 +
                        Statement((
                            ('bracket', ')'),
                        ))
                    )
                    conclusions.append(
                        Statement((
                            ('bracket', '('),
                        )) +
                        premise1 +
                        Statement((
                            ('connect', 'or'),
                            ('bracket', '('),
                            ('connect', 'not'),
                        )) +
                        premise2 +
                        Statement((
                            ('bracket', ')'),
                            ('bracket', ')'),
                        ))
                    )
            case InferType.FalsyOR:
                try: A = premise1.formulasInForm(
                    (('bracket', '('),
                     ('connect', 'not')),
                    (('bracket', ')'),),
                )[0][0]
                except TypeError: A = None
                try: B = premise2.formulasInForm(
                    (('bracket', '('),
                     ('connect', 'not')),
                    (('bracket', ')'),),
                )[0][0]
                except TypeError: B = None
                if A and B:
                    conclusions.append(
                        Statement((
                            ('bracket', '('),
                            ('connect', 'not'),
                            ('bracket', '(')
                        )) +
                        A +
                        Statement((
                            ('connect', 'or'),
                        )) +
                        B +
                        Statement((
                            ('bracket', ')'),
                            ('bracket', ')'),
                        ))
                    )
            case InferType.UnivModPonens:
                try: Ax, Bx = premise1.formulasInForm((
                    ('bracket', '('),
                    ('quanti', 'forall'),
                    ('bracket', '('),
                    ('var', '0'),
                    ('bracket', ')'),
                    ('bracket', '('),
                ), (
                    ('bracket', ')'),
                    ('bracket', ')'),
                ), (
                    ('connect', 'imply'),
                ),)[0]
                except TypeError: Ax, Bx = (None, None)
                if Ax and Bx:
                    assert premise1[3][0] in ['var', 'distVar'], 'brah'
                    bol, maps = Ax.eq(premise2)
                    x = premise1[3]
                    if bol and x in Ax.syms():
                        y = maps[x]
                        conclusions.append(Bx.substitute({x: y}))
            case InferType.ExistModPonens:
                try: Ax = premise1.formulasInForm((
                    ('bracket', '('),
                    ('quanti', 'exists'),
                    ('bracket', '('),
                    ('var', '0'),
                    ('bracket', ')'),
                ), (
                    ('bracket', ')'),
                ),)[0][0]
                except TypeError: Ax = None
                else:
                    x = premise1[3]
                    try: Ay, By = premise2.formulasInForm((
                        ('bracket', '('),
                    ), (
                        ('bracket', ')'),
                    ), (
                        ('connect', 'imply'),
                    ),)[0]
                    except TypeError: Ay, By = (None, None)
                    else:
                        bol, maps = Ax.eq(Ay)
                        if bol:
                            y = maps[x]
                            for z in (sym for sym in self.syms() - By.syms() if sym[0] in ['var', 'distVar']):
                                conclusions.append(
                                    Statement.lex('(exists(') +
                                    Statement((z,)) +
                                    Statement.lex(')') +
                                    By.substitute({y: z}) +
                                    Statement.lex(')')
                                )
                            conclusions.append(
                                Statement.lex('(exists(') +
                                Statement((y,)) +
                                Statement.lex(')') +
                                By +
                                Statement.lex(')')
                            )
            case InferType.Truth:
                conclusions.append(Statement.lex('tT'))
            case InferType.Falsehood:
                conclusions.append(Statement.lex('(not tF)'))
            case InferType.SubsProp:
                try: A = premise1.formulasInForm((
                    ('bracket', '('),
                    ('quanti', 'forall'),
                    ('bracket', '('),
                    ('var', '0'),
                    ('bracket', ')'),
                ), (
                    ('bracket', ')'),
                ))[0][0]
                except TypeError: pass
                else:
                    x = premise1[3]
                    res = A.complexSubstitute({x: tuple(object)})
                    if res: conclusions.append(res)
            case InferType.Identity:
                conclusions.append(Statement.lex('(') + object + Statement.lex('=') + object + Statement.lex(')'))
            case InferType.SymmProp:
                try: X, Y = premise1.formulasInForm((
                    ('bracket', '('),
                ), (
                    ('bracket', ')'),
                ), (
                    ('equal',),
                ),
                opt1obj=True,
                opt2obj=True,
                )[0]
                except TypeError: pass
                else:
                    conclusions.append(Statement.lex('(') + Y + Statement.lex('=') + X + Statement.lex(')'))
            case InferType.TransProp:
                try: X, Y = premise1.formulasInForm((
                    ('bracket', '('),
                ), (
                    ('bracket', ')'),
                ), (
                    ('equal',),
                ),
                opt1obj=True,
                opt2obj=True,
                )[0]
                except TypeError: pass
                else:
                    try: Y2, Z = premise2.formulasInForm((
                        ('bracket', '('),
                    ), (
                        ('bracket', ')'),
                    ), (
                        ('equal',),
                    ),
                    opt1obj=True,
                    opt2obj=True,
                    )[0]
                    except TypeError: pass
                    else:
                        if tuple(Y2) == tuple(Y):
                            conclusions.append(Statement.lex('(') + X + Statement.lex('=') + Z + Statement.lex(')'))
            case InferType.SubsPropEq:
                try: x, y = premise1.formulasInForm((('bracket', '('),), (('bracket', ')'),), (('equal',),),
                    opt1obj=True,
                    opt2obj=True,
                )[0]
                except TypeError: pass
                else:
                    if len(object) == 1:
                        conclusions.append(
                            Statement.lex('(') +
                            object +
                            Statement.lex('(') +
                            x +
                            Statement.lex(') = ') +
                            object +
                            Statement.lex('(') +
                            y +
                            Statement.lex('))')
                        )
            case InferType.OpSimplify: #Holy complexity
                occurences = (( premise1[i+1][1 % len(premise1[i+1])], premise1[i+3][1 % len(premise1[i+3])], premise1[i+2][1 % len(premise1[i+2])], i, i+5 ) for i in range(len(premise1) - 4) if \
                              premise1[i] == ('bracket', '(') and premise1[i+4] == ('bracket', ')') and premise1[i+2][0] == 'oper')
                for num1, num2, connect, start, end in occurences:
                    if connect == '+':
                        res = list(premise1.statement)
                        res[start:end] = (('number', str(int(num1) + int(num2))),)
                        conclusions.append(Statement(tuple(res)))
                        continue
                    if connect == '-':
                        res = list(premise1.statement)
                        res[start:end] = (('number', str(int(num1) - int(num2))),)
                        conclusions.append(Statement(tuple(res)))
                        continue
                    if connect == '*':
                        res = list(premise1.statement)
                        res[start:end] = (('number', str(int(num1) * int(num2))),)
                        conclusions.append(Statement(tuple(res)))
                        continue
                    if connect == '/':
                        res = list(premise1.statement)
                        res[start:end] = (('number', str( round(int(num1) / int(num2)) )),)
                        conclusions.append(Statement(tuple(res)))
                        continue
                    if connect == 'f/':
                        res = list(premise1.statement)
                        res[start:end] = (('number', str( math.floor(int(num1) / int(num2)) )),)
                        conclusions.append(Statement(tuple(res)))
                        continue
                    if connect == 'c/':
                        res = list(premise1.statement)
                        res[start:end] = (('number', str( math.ceil(int(num1) / int(num2)) )),)
                        conclusions.append(Statement(tuple(res)))
                        continue
                    if connect == '%':
                        res = list(premise1.statement)
                        res[start:end] = (('number', str(int(num1) % int(num2))),)
                        conclusions.append(Statement(tuple(res)))
                        continue
                    raise InferenceError('Wrong operator; impossible.')
            case InferType.Comparison: #Holy complexity
                occurences = \
                    (
                        (premise1[i+1][1 % len(premise1[i+1])], premise1[i+3][1 % len(premise1[i+3])], premise1[i+2][1 % len(premise1[i+2])], i, i+5)
                        for i in range(len(premise1) - 4) if \
                            premise1[i] == ('bracket', '(') and premise1[i+4] == ('bracket', ')') and premise1[i+2][0] == 'compare'
                    )
                mapper = {True: 'tT', False: 'tF'}
                for num1, num2, connect, start, end in occurences:
                    if connect == '>':
                        res = list(premise1.statement)
                        res[start:end] = (('truth', mapper[int(num1) > int(num2)],),)
                        conclusions.append(Statement(tuple(res)))
                        continue
                    elif connect == '<':
                        res = list(premise1.statement)
                        res[start:end] = (('truth', mapper[int(num1) < int(num2)],),)
                        conclusions.append(Statement(tuple(res)))
                        continue
            case _: raise InferenceError('Unsupported infer type: {}'.format(inferType))

        return tuple(conclusions)
    def inferAllConclusions(self, premise1Index: int, premise2Index: int = None, object: Statement = Statement(())) -> Tuple[Tuple[Statement, InferType]]:
        """
        Infers the proof and yields all possilble conclusions.
        """

        premise1Use = premise1Index != None
        premise2Use = premise2Index != None
        objectUse = tuple(object) != ()

        if premise1Use:
            premise1: Statement = self[premise1Index]['state']
            if not premise1.wellformed(): raise InferenceError('Premise 1 is ill-formed')
        if premise2Use:
            premise2: Statement = self[premise2Index]['state']
            if not premise2.wellformed(): raise InferenceError('Premise 2 is ill-formed')
        if objectUse:
            if not object.wellformedobj(): raise InferenceError('Object is ill-formed')
        checkableInferTypes = tuple(iType for iType in InferType if premiseUsesOfInferType[iType] == (premise1Use, premise2Use, objectUse, False, False, False))
        conclusion = ()
        for inferType in checkableInferTypes:
            for conclusionState in self.inferConclusions(inferType, premise1Index, premise2Index, object):
                conclusion += ((conclusionState, inferType),)
        return conclusion
    def infer(self, premise1Index: int, premise2Index: int = None, object: Statement = Statement(()), conclusionI: int | Statement = 0) -> 'ProofBase':
        """
        Infers the proof and returns the result.
        """

        res = deepcopy(self)
        state = 0
        conclusions = res.inferAllConclusions(premise1Index, premise2Index, object)
        if isinstance(conclusionI, int):
            state, inferType = conclusions[conclusionI]
            res.inferences += [(inferType, premise1Index, premise2Index, object, conclusionI)]
        elif isinstance(conclusionI, Statement):
            if not tuple(conclusionI) in tuple(tuple(state) for state, _ in conclusions): raise InferenceError('Invalid conclusion')
            conclusionIndex = tuple(tuple(state) for state, _ in conclusions).index(tuple(conclusionI))
            state, inferType = conclusions[conclusionIndex]
            res.inferences += [(inferType, premise1Index, premise2Index, object, conclusionIndex)]
        else:
            raise TypeError('ProofBase.infer only supports conclusionI param types of int and Statement, your type is: ' + str(type(conclusionI)))
        assert not isinstance(state, int), 'brah'
        res.statements += [state]
        res.stateTags += [StateTag.LEMMA]
        return res
    def symbolPoint(self) -> int:
        """
        Returns the symbol point of this ProofBase
        """
        return sum(statement.symbolPoint() if stateTag == StateTag.LEMMA else 0 for statement, stateTag in zip(self.statements, self.stateTags))

@dataclass
class Proof(ProofBase):
    """
    Contains a list of Statements, with subproofs, and a list of inference.
    """
    subproofs: List[ProofBase] = field(default_factory=list)

    def convert(
            strAxioms: Tuple[str],
            subProofs:
                      Tuple[Tuple[ str, Tuple[Tuple[int, int | None, str, int | Statement], ...] ]]
                      = ()
                ) -> 'Proof':
        states = [Statement.lex(state) for state in strAxioms]
        proof = Proof(states, [StateTag.AXIOM for _ in states], [None for _ in states], subproofs=list(
            ProofBase.convert((axiom,),
                tuple( (None, p1index, p2index, object, concI) for p1index, p2index, object, concI in inference)
            ) for axiom, inference in subProofs
        ))
        return proof

    def inferConclusions(
                         self,
                         inferType: InferType,
                         premise1Index: int,
                         premise2Index: int = None,
                         subProofIndex: int = None,
                         premise4Index: int = None,
                         premise5Index: int = None,
                         object: Statement = Statement(())
                         ) -> Tuple[Statement]:
        premiseUses = premiseUsesOfInferType[inferType]
        if premiseUses[0]:
            premise1: Statement = self[premise1Index]['state']
            if not premise1.wellformed():
                raise InferenceError('Premise 1 is ill-formed')
        if premiseUses[1]:
            premise2: Statement = self[premise2Index]['state']
            if not premise2.wellformed():
                raise InferenceError('Premise 2 is ill-formed')
        if premiseUses[2]:
            if not object.wellformedobj():
                raise InferenceError('Object is ill-formed')
        if premiseUses[3:] == (False, False, False):
            return super().inferConclusions(inferType, premise1Index, premise2Index, object)
        subproof = self.subproofs[subProofIndex]
        if premiseUses[3]:
            premise3: Statement = subproof[0]['state']
            if not premise3.wellformed():
                raise InferenceError('Premise 3 is ill-formed')
        if premiseUses[4]:
            premise4: Statement = subproof[premise4Index]['state']
            if not premise4.wellformed():
                raise InferenceError('Premise 4 is ill-formed')
        if premiseUses[5]:
            premise5: Statement = subproof[premise5Index]['state']
            if not premise5.wellformed():
                raise InferenceError('Premise 5 is ill-formed')

        conclusions = []

        match inferType:
            case InferType.CondProof:
                try:
                    Ax = premise3.formulasInForm(
                        (
                            ('bracket', '('),
                            ('quanti', 'forall'),
                            ('bracket', '('),
                            ('var', '0'),
                            ('bracket', ')'),
                        ),
                        (
                            ('bracket', ')'),
                        ),
                    )[0][0]
                    Bx = premise4.formulasInForm(
                        (
                            ('bracket', '('),
                            ('quanti', 'forall'),
                            ('bracket', '('),
                            ('var', '0'),
                            ('bracket', ')'),
                        ),
                        (
                            ('bracket', ')'),
                        ),
                    )[0][0]
                    Ay = premise1.formulasInForm(
                        (
                            ('bracket', '('),
                            ('quanti', 'forall'),
                            ('bracket', '('),
                            ('var', '0'),
                            ('bracket', ')'),
                        ),
                        (
                            ('bracket', ')'),
                        ),
                    )[0][0]
                except TypeError: pass
                else:
                    bol, _ = Ax.eq(Ay)
                    if bol:
                        x = premise3[3]
                        y = premise1[3]
                        conclusions.append(premise4.substitute({x: y}))
            case InferType.IndProof:
                try:
                    Ax = premise3.formulasInForm(
                        (
                            ('bracket', '('),
                            ('quanti', 'forall'),
                            ('bracket', '('),
                            ('var', '0'),
                            ('bracket', ')'),
                        ),
                        (
                            ('bracket', ')'),
                        ),
                    )[0][0]
                    Bx = premise4.formulasInForm(
                        (
                            ('bracket', '('),
                            ('quanti', 'forall'),
                            ('bracket', '('),
                            ('var', '0'),
                            ('bracket', ')'),
                        ),
                        (
                            ('bracket', ')'),
                        ),
                    )[0][0]
                    Bx2 = premise5.formulasInForm(
                        (
                            ('bracket', '('),
                            ('quanti', 'forall'),
                            ('bracket', '('),
                            ('var', '0'),
                            ('bracket', ')'),
                            ('bracket', '('),
                            ('connect', 'not'),
                        ),
                        (
                            ('bracket', ')'),
                            ('bracket', ')'),
                        ),
                    )[0][0]
                except TypeError: pass
                else:
                    if Bx == Bx2 and len(tuple(object)) == 1:
                        x = premise4[3]
                        y = object[0]
                        conclusions.append(
                            Statement.lex('(forall(')
                            +
                            Statement((y,))
                            +
                            Statement.lex(')(not ')
                            +
                            Ax.substitute({x: y})
                            +
                            Statement.lex('))')
                        )
        return conclusions
