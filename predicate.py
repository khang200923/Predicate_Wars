from copy import deepcopy
from dataclasses import dataclass, field
from enum import Enum
import random
import re
from typing import Any, Callable, List, Sequence, Set, Tuple

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


#Export constants and functions
gameFuncNames = ['[randPlayer]', '[randCard]', '[chosenPlayer]', '[chosenCard]', '[playerOfChosenCard]']
predGFuncNames = ['[PLAYER]', '[CARD]', '[HEALTHLOWER]', '[HEALTHHIGHER]', '[POWERLOWER]', '[POWERHIGHER]', '[PROVPOWERLOWER]', '[PROVPOWERHIGHER]', '[SYMBOLPOINTLOWER]', '[SYMBOLPOINTHIGHER]']
predAFuncNames = ['[CLAIM]', '[ATK]', '[HEAL]', '[ADDPOWER]', '[SUBPOWER]', '[ADDRULE]', '[DELETERULE]']

varDetector = r'([a-z](_[0-9]+)?)|([0-9]+)'

symbolsType = (
    ('gameFuncName', '|'.join([x.replace("[", "\[").replace("]", "\]") for x in gameFuncNames])),
    ('predGFuncName', '|'.join([x.replace("[", "\[").replace("]", "\]") for x in predGFuncNames])),
    ('predAFuncName', '|'.join([x.replace("[", "\[").replace("]", "\]") for x in predAFuncNames])),
    ('distVar', r'[a-z]_[0-9]+'),
    ('distPred', r'[A_Z]_[0-9]+'),
    ('truth', r't[TF]'),
    ('quanti', r'forall|exists'),
    ('connect', r'not\s|\sand\s|\sor\s|\simply\s'),
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

def symbolTypeCalc(symbol: str) -> str | None: return next((name for name, cond in symbolsType if re.match('^{}$'.format(cond), symbol)), None)

def symbolTrans(symbol: str) -> Tuple[str, ...] | None:
    symType = symbolTypeCalc(symbol)
    if symType == None:
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
    if symType in ['gameFuncName', 'predGFuncName', 'predAFuncName', 'truth', 'quanti', 'bracket', 'number']:
        return (symType, symbol)
    return (symType,)
@dataclass
class Statement:
    statement: Tuple[Tuple, ...]

    @staticmethod
    def lex(string: str) -> 'Statement':
        """
        Tokenize statement from string.
        """
        tokens = []
        unLexed = string
        while unLexed != '':
            typeDetect = tuple(re.match(regex, unLexed) for _, regex in symbolsType)
            if any(x != None for x in typeDetect):
                typeDetectIndex = tuple(re.match(regex, unLexed).start() if re.match(regex, unLexed) else float('inf') for _, regex in symbolsType)
                nextTokenMatch = typeDetect[typeDetectIndex.index(min(typeDetectIndex))]
                nextToken = symbolTrans(nextTokenMatch.group())
                if nextToken != ('space',):
                    tokens.append(nextToken)
                unLexed = unLexed[nextTokenMatch.end():]
            else:
                raise ValueError("Invalid string")
        return Statement(tuple(tokens))

    def __str__(self) -> str:
        res = ''
        for symType, *symVal in self:
            if symType == None:
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
            elif symType in ['gameFuncName', 'predGFuncName', 'predAFuncName', 'truth', 'quanti', 'bracket', 'number']:
                res += symVal[0]
            elif symType == 'equal':
                res += '='
            elif symType == 'comma':
                res += ','
        return res

    def __getitem__(self, key):
        return self.statement[key]

    def __len__(self):
        return len(self.statement)

    def eq(self, statement: 'Statement', startingMaps = {}) -> Tuple[bool, dict[Tuple, Tuple]]:
        """
        Check if two statements are functionally equivalent
        """
        assert isinstance(statement, Statement), 'must compare with a valid instance of class "Statement"'
        maps = deepcopy(startingMaps)
        for sym1, sym2 in zip(self, statement):
            if len(sym1) != len(sym2): return (False, maps)
            if (sym1[0] in varSymbols and sym2[0] in varSymbols) or \
            (sym1[0] in predSymbols and sym2[0] in predSymbols):
                if sym1 in maps:
                    if maps[sym1] != sym2: return (False, maps)
                    else: continue
                else:
                    maps[sym1] = sym2
                    continue
            elif sym1 != sym2: return (False, maps)
        return (_mappableDict(maps), maps)

    def syms(self) -> Set[Tuple]:
        """
        Returns vars and preds in the statement.
        """
        syms = set()
        for sym in self:
            if sym[0] in varSymbols or sym[0] in predSymbols:
                syms.add(sym)
        return syms

    def __eq__(self, statement: 'Statement', maps = {}) -> bool:
        return self.eq(statement, maps)[0]

    def __add__(self, statement: 'Statement') -> 'Statement':
        assert isinstance(statement, Statement), 'must add with a valid instance of class "Statement"'
        return Statement(self.statement + statement.statement)

    def form(self, start: Tuple[Tuple, ...]=(), end: Tuple[Tuple, ...]=(), mid: Tuple[Tuple, ...]=(), startingMaps: dict[Tuple, Tuple]={}) -> bool:
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

        #Check for special case mid
        if mid:
            minIndexes = _seqFormOptionalsIndexes(self, start, end, mid, midcond=lambda index: \
                        Statement(self[startEndIndexes[0]:index]).wellformed() and \
                        Statement(self[index+len(mid):startEndIndexes[1]]).wellformed() \
            , startEndMatch=lambda x, y: Statement(x) == Statement(y))[1]
            for minIndex in minIndexes:
                if self[minIndex[0] : minIndex[1]] == mid:
                    return True
            return False
        if not Statement(self[startEndIndexes[0]:startEndIndexes[1]]).wellformed():
            return False

        #All filters passed - great!
        return True

    def formulasInForm(self, start: Tuple[Tuple, ...]=(), end: Tuple[Tuple, ...]=(), mid: Tuple[Tuple, ...]=(), startingMaps: dict[Tuple, Tuple]={}) -> Tuple[Tuple['Statement', ...], ...] | None:
        """
        Returns all optional formulas in statement if it fits with the statement form.
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

        #Check for special case mid
        if mid:
            minIndexes = _seqFormOptionalsIndexes(self, start, end, mid, midcond=lambda index: \
                        Statement(self[startEndIndexes[0]:index]).wellformed() and \
                        Statement(self[index+len(mid):startEndIndexes[1]]).wellformed() \
            , startEndMatch=lambda x, y: Statement(x) == Statement(y))[1]
            for minIndex in minIndexes:
                if self[minIndex[0] : minIndex[1]] == mid:
                    return tuple( ( Statement(self[startEndIndexes[0]:minIndex[0]]), Statement(self[minIndex[1]:startEndIndexes[1]]) ) for minIndex in minIndexes)
            return None
        else:
            if not Statement(self[startEndIndexes[0]:startEndIndexes[1]]).wellformed():
                return None
        return ( ( Statement(self[startEndIndexes[0]:startEndIndexes[1]],) ,) ,)

    def wellformedobj(self) -> bool:
        """
        Check whether the object is well-formed.
        """

        if len(self) == 0: return False
        if len(self) == 1:
            return self.statement[0][0] in ('distVar', 'var', 'number')
        if len(self) > 2:
            if self[1] == ('bracket', '(') and self[-1] == ('bracket', ')') and \
            self[0][0] in ('gameFuncName', 'distVar', 'var'):
                paramsLeft = self[2:-1]
                while len(paramsLeft) > 0:
                    paramEndIndex = next((index for index in range(len(paramsLeft) + 1) if Statement(paramsLeft[:index]).wellformedobj() and not (index < len(paramsLeft) and not paramsLeft[index] == ('comma',))), None)
                    if paramEndIndex == None: return Statement(paramsLeft).wellformedobj()
                    paramsLeft = paramsLeft[paramEndIndex+1:]
                return True
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
        if len(self) == 5 and self[2] == ('equal',) and self[0] == ('bracket', '(') and self[4] == ('bracket', ')'):
            if self[1][0] in ('distVar', 'var', 'number') and self[3][0] in ['distVar', 'var', 'number']:
                return True

        #Function syntax
        if self[1] == ('bracket', '(') and self[-1] == ('bracket', ')') and \
        self[0][0] in ('predGFuncName', 'predAFuncName', 'distPred', 'pred'):
            paramsLeft = self[2:-1]
            while len(paramsLeft) > 0:
                paramEndIndex = next((index for index in range(len(paramsLeft) + 1) if Statement(paramsLeft[:index]).wellformedobj() and not (index < len(paramsLeft) and not paramsLeft[index] == ('comma',))), None)
                if paramEndIndex == None: return Statement(paramsLeft).wellformedobj()
                paramsLeft = paramsLeft[paramEndIndex+1:]
            return True

        return False

    def substitute(self, startingMap: dict[Tuple, Tuple], obj: bool = False) -> 'Statement | None':
        """
        Maps each symbol in statement with a map, and return the resulting statement.
        When the result is not well-formed, return None
        Overlapping also returns None
        """
        map = {sym: sym for sym in self.syms()}
        map.update(startingMap)
        if not _mappableDict(map): return None
        res = Statement(tuple(map.get(symbol, symbol) for symbol in self))
        if obj:
            if not res.wellformedobj(): return None
        else:
            if not res.wellformed(): return None
        return res

class StateTag(Enum):
    AXIOM = 0
    LEMMA = 1

class InferType(Enum):
    ImpliInst = 12
    ExpliInst = 11
    ModPonens = 0
    ModTollens = 1
    UniversalInst = 2
    UniversalGenr = 3
    ExistentialInst = 4
    ExistentialGenr = 5
    Conjunc = 6
    Simplific = 7
    Addition = 8
    UnivModPonens = 9
    ExistModPonens = 10
    Truth = 13
    Falsehood = 14

premiseUsesOfInferType = { #(p1, p2, z1, z2, z3)
    InferType.ImpliInst: (True, True, False, False, False),
    InferType.ExpliInst: (True, True, False, False, False),
    InferType.ModPonens: (True, True, False, False, False),
    InferType.ModTollens: (True, True, False, False, False),
    InferType.UniversalInst: (True, True, False, False, False),
}

class InferenceError(Exception): pass

@dataclass
class ProofBase:
    """
    Contains a list of Statements, with no subproof, and a list of inference.
    """
    statements: List[Statement] = field(default_factory=list)
    stateTags: List[StateTag] = field(default_factory=list)
    inferences: List[Tuple[InferType, int, int, Tuple[Tuple[int, int], Tuple[int, int]], Tuple[Tuple[int, int], Tuple[int, int]]]] = field(default_factory=list)

    def __getitem__(self, index: int) -> dict[str, Any]:
        try:
            return {'state': self.statements[index], 'tag': self.stateTags[index], 'infer': self.inferences[index]}
        except IndexError:
            return {'state': self.statements[index], 'tag': self.stateTags[index], 'infer': None}

    def syms(self) -> Set[Tuple]:
        """
        Returns vars and preds used in proof.
        """
        #TODO: Test this method
        return {sym for state in self.statements for sym in state.syms()}

    def symsWithout(self, stateIndex) -> Set[Tuple]:
        """
        Returns vars and preds used in proof, without the statement on specified index.
        """
        #TODO: Test this method
        return {sym for state in (state for index, state in enumerate(self.statements) if index != stateIndex) for sym in state.syms()}

    def unusedVarSuggester(self):
        """
        Suggests an unused variable name based on existing syms in random.
        """
        #TODO: Test this method
        char = random.randint(1, 26)
        syms = self.syms()
        syms = {sym for sym in syms if sym[0] in ['var', 'distVar'] and sym[1] == str(char)}
        height = min((0 if sym[0] == 'var' else int(sym[2]) for sym in syms), default=-1) + 1
        if height == 0: return ('var', str(char))
        return ('distVar', str(char), str(height))

    def inferConclusions(self, inferType: InferType, premise1Index: int, premise2Index: int) -> Tuple[Statement]:
        """
        Infers the proof and yields conclusions.
        """
        #TODO: Implement this method (the hardest part yet)
        #TODO: Test this method (oh no)
        #TODO: Try to avoid creating a spaghetti code...
        premiseUses = premiseUsesOfInferType[inferType]
        if premiseUses[0]:
            premise1: Statement = self[premise1Index]['state']
            if not premise1.wellformed(): raise InferenceError('Premise 1 is ill-formed')
        if premiseUses[1]:
            premise2: Statement = self[premise2Index]['state']
            if not premise2.wellformed(): raise InferenceError('Premise 2 is ill-formed')

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
            case InferType.ModTollens: #TODO: Test this case
                try: B = premise2.formulasInForm(
                    (
                        ('bracket', '('),
                        ('connect', 'not'),
                    ),
                    (
                        ('bracket', ')'),
                    ),
                )[0][0]
                except TypeError: B = None
                if B:
                    try: Aa = premise1.formulasInForm(
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
                    except TypeError: Aa = None
                    if Aa and tuple(Aa[1]) == tuple(B):
                        conclusions.append(Statement.lex('(not ') + Aa[0] + Statement.lex(')'))
            case InferType.UniversalInst: #TODO: Test this method
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
                except TypeError: A = None
                if A:
                    _, maps = A.eq(
                        Statement( (('var', '0'),) )
                    )
                    thatVar = maps[('var', '0')]
                    for sym in self.syms():
                        conclusions.append({thatVar: sym})
                    conclusions.append({thatVar: self.unusedVarSuggester()})
            case InferType.UniversalGenr: #TODO: Test this method
                uniqueVars1 = self.syms() - self.symsWithout(premise1Index)
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

        return tuple(conclusions)
