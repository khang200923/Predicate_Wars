from copy import deepcopy
from dataclasses import dataclass
import re
from typing import Callable, Sequence, Tuple

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
    ((subseq1start, subseq2end), ((subseq2end, subseq1start),...)?)
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
gameFuncNames = [x.replace("[", "\[").replace("]", "\]") for x in ['[randPlayer]', '[randCard]', '[chosenPlayer]', '[chosenCard]', '[playerOfChosenCard]']]
predGFuncNames = [x.replace("[", "\[").replace("]", "\]") for x in ['[PLAYER]', '[CARD]', '[HEALTHLOWER]', '[HEALTHHIGHER]', '[POWERLOWER]', '[POWERHIGHER]', '[PROVPOWERLOWER]', '[PROVPOWERHIGHER]', '[SYMBOLPOINTLOWER]', '[SYMBOLPOINTHIGHER]']]
predAFuncNames = [x.replace("[", "\[").replace("]", "\]") for x in ['[CLAIM]', '[ATK]', '[HEAL]', '[ADDPOWER]', '[SUBPOWER]', '[ADDRULE]', '[DELETERULE]', '[ADDSUBPROOF]']]

varDetector = r'([a-z](_[0-9]+)?)|([0-9]+)'

symbolsType = (
    ('gameFuncName', '|'.join(gameFuncNames)),
    ('predGFuncName', '|'.join(predGFuncNames)),
    ('predAFuncName', '|'.join(predAFuncNames)),
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

    def __getitem__(self, key):
        return self.statement[key]

    def __len__(self):
        return len(self.statement)

    def eq(self, statement: 'Statement', startingMaps = {}) -> Tuple[bool, dict[Tuple, Tuple]]:
        """
        Check if two statements are functionally equivalent
        """
        #TODO: Test this method
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
        return (True, maps)

    def __eq__(self, statement: 'Statement', maps = {}) -> bool:
        return self.eq(statement, maps)[0]

    def form(self, start: Tuple[Tuple, ...], end: Tuple[Tuple, ...], mid: Tuple[Tuple, ...]=(), startingMaps: dict[Tuple, Tuple]={}) -> bool:
        #TODO: Test this method

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
        else:
            if not Statement(self[startEndIndexes[0]:startEndIndexes[1]]).wellformed():
                return False

        #All filters passed - great!
        return True

    def wellformed(self) -> bool:
        """
        Check whether the given token sequence is well-formed.
        """
        #TODO: Test this method
        if len(self.statement) == 0: return False
        if len(self.statement) == 1:
            return self.statement[0][0] in ('distPred', 'truth', 'pred')

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
        if self[0] == ('bracket', '(') and self[2] == ('bracket', '(') and self[-2:] == (('bracket', ')'), ('bracket', ')')) and \
        self[1][0] in ('gameFuncName', 'predGFuncName', 'predAFuncName', 'distVar', 'var', 'distPred', 'pred') and \
        all(comma  == ('comma',) for comma in self[4:-2:2]) and \
        all(var[0] in ('distVar', 'var', 'number') for var in self[3:-2:2]): return True

        return False
