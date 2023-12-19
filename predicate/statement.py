"""
Provides essential classes and methods for creating predicate logic statements.
"""
from copy import deepcopy
from dataclasses import dataclass
import re
from typing import Set, Tuple

from baserules import getBaseRules
from predicate.utils import checkSeqForm, mappableDict, seqFormOptionalsIndexes

#Export constants and functions
gameFuncNames = ['[randPlayer]', '[randCard]', '[chosenPlayer]', '[chosenCard]', '[playerOfCard]', '[health]', '[power]', '[potency]', '[symbolPoint]', '[powerCost]']
predGFuncNames = ['[NUMBER]', '[PLAYER]', '[CARD]']
predAFuncNames = ['[CLAIM]', '[ATK]', '[HEAL]', '[ADDPOWER]', '[SUBPOWER]']
truths = ['tT', 'tF']
quantis = ['forall', 'exists']
connects = ['not', 'and', 'or', 'imply']
opers = ['+', '-', '*', '/', '%', 'f/', 'c/']
compares = ['<', '>']

varDetector = r'([a-z](_[0-9]+)?)|([0-9]+)'

symbolsType = (
    ('gameFuncName', '|'.join([x.replace("[", r"\[").replace("]", r"\]") for x in gameFuncNames])), #pure var
    ('predGFuncName', '|'.join([x.replace("[", r"\[").replace("]", r"\]") for x in predGFuncNames])), #pure pred
    ('predAFuncName', '|'.join([x.replace("[", r"\[").replace("]", r"\]") for x in predAFuncNames])), #pure pred
    ('distVar', r'[a-z]_[0-9]+'), #pure var
    ('distPred', r'[A-Z]_[0-9]+'), #pure pred
    ('truth', r't[TF]'), #pred
    ('quanti', r'forall|exists'),
    ('connect', r'not\s|\sand\s|\sor\s|\simply\s'),
    ('oper', r'[+\-*/%]|f/|c/'),
    ('compare', r'[<>]'),
    ('var', r'[a-z]'), #pure var
    ('pred', r'[A-Z]'), #pure pred
    ('equal', r'='),
    ('comma', r','),
    ('bracket', r'[\(\)]'),
    ('number', r'[0-9]+'), #var
    ('space', r'\s'),
)

specialSymbolsType = (
    ('player', r'\$player:[^$]*\$'),
    ('card', r'\$card:[^$]*\$')
)

varSymbols = ('distVar', 'var', 'gameFuncName')
predSymbols = ('distPred', 'truth', 'pred', 'predGFuncName', 'predAFuncName')
varFuncSymbols = ('distVar', 'var', 'number', 'gameFuncName', 'player', 'card')
predFuncSymbols = ('distPred', 'pred', 'predGFuncName', 'predAFuncName')
unPureVar = ('number', 'player', 'card')
unPurePred = ('truth',)
specialSymbols = ('player', 'card')

#Special symbol types: 'player', 'card'

def symbolTypeCalc(symbol: str) -> str | None:
    return next(
        (
            name for name, cond in symbolsType + specialSymbolsType
            if re.match('^{}$'.format(cond), symbol)
        ),
        None
    )

def symbolTrans(symbol: str, special: bool = False) -> Tuple[str, ...] | None:
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
    if symType in [
        'gameFuncName',
        'predGFuncName',
        'predAFuncName',
        'truth',
        'quanti',
        'bracket',
        'number',
        'oper',
        'compare'
    ]:
        return (symType, symbol)
    if symType in specialSymbols and special:
        assert re.search(r'\$[^$:]*:([^$]*)\$', symbol) is not None, 'Impossible error.'
        return (symType, re.search(r'\$[^$:]*:([^$]*)\$', symbol).group(1))
    return (symType,)

@dataclass
class Statement:
    """
    A statement in predicate logic
    """
    statement: Tuple[Tuple, ...]

    @staticmethod
    def lex(string: str, special: bool = False) -> 'Statement':
        """
        Tokenize statement from string.
        """
        tokens = []
        unLexed = string
        while unLexed:
            if special:
                typeDetect = tuple(re.match(regex, unLexed) for _, regex in specialSymbolsType)
                if any(typeDetect):
                    typeDetectIndex = tuple(
                        re.match(regex, unLexed).start()
                        if re.match(regex, unLexed)
                        else float('inf')
                        for _, regex in specialSymbolsType
                    )
                    nextTokenMatch = typeDetect[typeDetectIndex.index(min(typeDetectIndex))]
                    nextToken = symbolTrans(nextTokenMatch.group(), special=True)
                    tokens.append(nextToken)
                    unLexed = unLexed[nextTokenMatch.end():]
                    continue

            typeDetect = tuple(re.match(regex, unLexed) for _, regex in symbolsType)
            if any(typeDetect):
                typeDetectIndex = tuple(
                    re.match(regex, unLexed).start()
                    if re.match(regex, unLexed)
                    else float('inf')
                    for _, regex in symbolsType
                )
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
            elif symType in [
                'gameFuncName',
                'predGFuncName',
                'predAFuncName',
                'truth',
                'quanti',
                'bracket',
                'number',
                'oper',
                'compare'
            ]:
                res += symVal[0]
            elif symType == 'equal':
                res += '='
            elif symType == 'comma':
                res += ','
            elif symType in specialSymbols:
                res += f'${symType}:{symVal}$'
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

    def eq(self, statement: 'Statement', startingMaps = None) -> Tuple[bool, dict[Tuple, Tuple] | None]:
        """
        Check if two statements are functionally equivalent
        """
        if startingMaps == None: startingMaps = {}
        if not isinstance(statement, Statement): return (False, None)
        maps = deepcopy(startingMaps)
        if len(self) != len(statement):
            return (False, maps)
        for sym1, sym2 in zip(self, statement):
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
        return (mappableDict(maps), maps)

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

    def form(
            self,
            start: Tuple[Tuple, ...]=(),
            end: Tuple[Tuple, ...]=(),
            mid: Tuple[Tuple, ...]=(),
            startingMaps: dict[Tuple, Tuple]={},
            opt1obj: bool = False,
            opt2obj: bool = False
        ) -> bool:
        """
        Checks if the statement form fits the statement.
        """

        #Check form first
        if not checkSeqForm(
            self,
            start,
            end,
            mid,
            startEndMatch=lambda x, y: Statement(x) == Statement(y)
        ): return False

        #Prepare maps
        maps = deepcopy(startingMaps)
        startEndIndexes = seqFormOptionalsIndexes(
            self,
            start,
            end,
            mid,
            startEndMatch=lambda x, y: Statement(x) == Statement(y)
        )[0]
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
            minIndexes = seqFormOptionalsIndexes(self, start, end, mid, midcond=lambda index: \
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

    def formulasInForm(
            self,
            start: Tuple[Tuple, ...]=(),
            end: Tuple[Tuple, ...]=(),
            mid: Tuple[Tuple, ...]=(),
            startingMaps: dict[Tuple, Tuple]={},
            opt1obj: bool = False,
            opt2obj: bool = False
        ) -> Tuple[Tuple['Statement', ...], ...] | None:
        """
        Returns all optional formulas (or objs) in statement if it fits with the statement form.
        """

        #Check form first
        if not checkSeqForm(
            self,
            start,
            end,
            mid,
            startEndMatch=lambda x, y: Statement(x) == Statement(y)
        ): return None

        #Prepare maps
        maps = deepcopy(startingMaps)
        startEndIndexes = seqFormOptionalsIndexes(
            self,
            start,
            end,
            mid,
            startEndMatch=lambda x, y: Statement(x) == Statement(y)
        )[0]
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
            minIndexes = seqFormOptionalsIndexes(self, start, end, mid, midcond=lambda index: \
                        getattr(Statement(self[startEndIndexes[0]:index]), opt1wellmethod)() and \
                        getattr(Statement(self[index+len(mid):startEndIndexes[1]]), opt2wellmethod)() \
            , startEndMatch=lambda x, y: Statement(x) == Statement(y))[1]
            for minIndex in minIndexes:
                if self[minIndex[0] : minIndex[1]] == mid:
                    return tuple(
                        (
                            Statement(self[startEndIndexes[0]:minIndex[0]]),
                            Statement(self[minIndex[1]:startEndIndexes[1]])
                        )
                        for minIndex in minIndexes
                    )
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
            return self.statement[0][0] in varFuncSymbols
        if len(self) > 2:
            #Function syntax
            if self[1] == ('bracket', '(') and self[-1] == ('bracket', ')') and \
            self[0][0] in varFuncSymbols:
                paramsLeft = self[2:-1]
                while len(paramsLeft) > 0:
                    paramEndIndex = next(
                        (
                            index for index in range(len(paramsLeft) + 1)
                            if Statement(paramsLeft[:index]).wellformedobj() and \
                            not (index < len(paramsLeft) and not paramsLeft[index] == ('comma',))
                        ),
                        None
                    )
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
            return self[0][0] in predSymbols

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
                paramEndIndex = next(
                    (
                        index for index in range(len(paramsLeft) + 1)
                        if Statement(paramsLeft[:index]).wellformedobj() and \
                        not (index < len(paramsLeft) and not paramsLeft[index] == ('comma',))
                    ),
                    None
                )
                if paramEndIndex is None: return Statement(paramsLeft).wellformedobj()
                paramsLeft = paramsLeft[paramEndIndex+1:]
            return True

        return False
    def functionArgs(self) -> Tuple['Statement', ...] | None:
        """
        Returns all arguments of a well-formed function.
        Throws error if not a well-formed function.
        """
        if not (self.wellformed() or self.wellformedobj()):
            return None
        if not (len(self) >= 3 and self[0][0] in \
                 (x for x in varSymbols + predSymbols if x not in (unPureVar + unPurePred)) \
                 and self[1] == ('bracket', '(')):
            return None
        paramsLeft = self[2:-1]
        params = []
        while len(paramsLeft) > 0:
            #Function param getter
            paramEndIndex = next(
                (
                    index for index in range(len(paramsLeft) + 1)
                    if Statement(paramsLeft[:index]).wellformedobj() and \
                    not (index < len(paramsLeft) and not paramsLeft[index] == ('comma',))
                ),
                None
            )
            if paramEndIndex is None: return Statement(paramsLeft).wellformedobj()
            params.append(paramsLeft[:paramEndIndex])
            paramsLeft = paramsLeft[paramEndIndex+1:]
        return tuple((Statement(param) for param in params))

    def substitute(
            self,
            startingMap: dict[Tuple, Tuple],
            obj: bool = False,
            mappableCheck: bool = True
        ) -> 'Statement | None':
        """
        Maps each symbol in statement with a map, and return the resulting statement.
        When the result is not well-formed, return None
        Overlapping also returns None
        """
        map = {sym: sym for sym in self.syms()}
        map.update(startingMap)
        if mappableCheck and not mappableDict(map): return None
        res = Statement(tuple(map.get(symbol, symbol) for symbol in self))
        if obj:
            if not res.wellformedobj(): return None
        else:
            if not res.wellformed(): return None
        return res

    def complexSubstitute(
            self,
            startingMap: dict[Tuple, Tuple[Tuple]],
            obj: bool = False
        ) -> 'Statement | None':
        """
        Maps each symbol in statement with a map (replacing occurences with one or more elems),
        and return the resulting statement.
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

    def deterministic(self, obj: bool | None = False) -> bool:
        """
        Checks if the statement is deterministic or not.
        Needs to be WFF/WFO else this will raise an error.
        """
        if obj is None:
            if not (self.wellformedobj() or self.wellformed()): raise ValueError('Not a well-formed object/formula')
        else:
            if obj and not self.wellformedobj(): raise ValueError('Not a well-formed object')
            if (not obj) and not self.wellformed(): raise ValueError('Not a well-formed formula')
        if self.simple(obj): return True
        if self.functionArgs():
            if obj and not self[0][0] == 'gameFuncName': return False
            if (not obj) and not self[0][0] in ('predGFuncName', 'predAFuncName'): return False
            if all(param.deterministic(True) for param in self.functionArgs()):
                return True
        if self.operatorArgs() and \
        all(param.deterministic(None) for param in self.operatorArgs()):
            return True
        return False

    def simple(self, obj: bool | None = False) -> bool:
        """
        Checks if the statement is simple or not.
        Needs to be WFF/WFO else this will raise an error.
        """
        if obj is None:
            if not (self.wellformedobj() or self.wellformed()): raise ValueError('Not a well-formed object/formula')
        else:
            if obj and not self.wellformedobj(): raise ValueError('Not a well-formed object')
            if (not obj) and not self.wellformed(): raise ValueError('Not a well-formed formula')

        if obj or obj is None:
            if len(self) == 1 and self[0][0] in unPureVar: return True
            if len(self) >= 3 and self[0][0] == 'gameFuncName' and self[1] == ('bracket', '(') and \
            all(sym[0] in unPureVar for sym in self[2::2]):
                return True
            if len(self) == 5 and self[1][0] in unPureVar and self[2][0] == 'oper' and self[3][0] in unPureVar:
                return True
        if (not obj) or obj is None:
            if len(self) == 1 and self[0][0] in unPurePred: return True
            if len(self) >= 3 and self[0][0] in ('predGFuncName', 'predAFuncName') and self[1] == ('bracket', '(') and \
            all(sym[0] in unPureVar for sym in self[2::2]):
                return True
            if len(self) == 5 and self[1][0] in unPureVar and self[2][0] == 'compare' and self[3][0] in unPureVar:
                return True
            if len(self) == 5 and self[1][0] in unPureVar and self[2][0] == 'equal' and self[3][0] in unPureVar:
                return True
            if len(self) == 5 and self[1][0] in unPurePred and self[2][0] == 'connect' and self[3][0] in unPurePred:
                return True

        return False


    def operatorArgs(self)-> Tuple['Statement', 'Statement'] | None:
        """
        Returns args of operator/connective/comparative/equality statement.
        Returns None if not operator/connective/comparative/equality statement.
        """
        res = self.formulasInForm((
            ('bracket', '('),
        ), (
            ('bracket', ')'),
        ), (
            ('equal',),
        ),
        opt1obj=True,
        opt2obj=True)
        if res is not None: return res[0]
        for op in opers:
            res = self.formulasInForm((
                ('bracket', '('),
            ), (
                ('bracket', ')'),
            ), (
                ('oper', op),
            ),
            opt1obj=True,
            opt2obj=True)
            if res is not None: return res[0]
        for con in connects:
            res = self.formulasInForm((
                ('bracket', '('),
            ), (
                ('bracket', ')'),
            ), (
                ('connect', con),
            ))
            if res is not None: return res[0]
        for com in compares:
            res = self.formulasInForm((
                ('bracket', '('),
            ), (
                ('bracket', ')'),
            ), (
                ('compare', com),
            ),
            opt1obj=True,
            opt2obj=True)
            if res is not None: return res[0]
        return None
    def operatorSymbol(self)-> Tuple[str, ...] | None:
        """
        Returns operator symbol of operator/connective/comparative/equality statement.
        Returns None if not operator/connective/comparative/equality statement.
        """
        if self.form((
            ('bracket', '('),
        ), (
            ('bracket', ')'),
        ), (
            ('equal',),
        ),
        opt1obj=True,
        opt2obj=True): return ('equal',)
        for op in opers:
            if self.form((
                ('bracket', '('),
            ), (
                ('bracket', ')'),
            ), (
                ('oper', op),
            ),
            opt1obj=True,
            opt2obj=True): return ('oper', op)
        for con in connects:
            if self.form((
                ('bracket', '('),
            ), (
                ('bracket', ')'),
            ), (
                ('connect', con),
            ),
            opt1obj=False,
            opt2obj=False): return ('connect', con)
        for com in compares:
            if self.form((
                ('bracket', '('),
            ), (
                ('bracket', ')'),
            ), (
                ('compare', com),
            ),
            opt1obj=True,
            opt2obj=True): return ('compare', com)
        return None

baseRules = tuple(Statement.lex(rule.statement) for rule in getBaseRules())
