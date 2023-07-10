from dataclasses import dataclass
import re
from typing import Tuple, Match

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
    ('connect', r'not | and | or | imply '),
    ('var', r'[a-z]'),
    ('pred', r'[A-Z]'),
    ('equal', r'='),
    ('comma', r','),
    ('bracket', r'[\(\)]'),
    ('number', r'[0-9]+'),
    ('space', r'\s'),
)

def symbolTypeCalc(symbol: str) -> str | None: return next((name for name, cond in symbolsType if re.match('^{}$'.format(cond), symbol)), None)

def symbolTrans(symbol: str) -> Tuple[str, ...] | None:
    symType = symbolTypeCalc(symbol)
    if symType == None:
        return None
    if symType == 'var':
        return (symType, ord(symbol.lower()) - ord('a') + 1)
    if symType == 'pred':
        return (symType, ord(symbol.lower()) - ord('a') + 1)
    if symType == 'distVar':
        return (symType, ord(symbol[0].lower()) - ord('a') + 1, symbol[2:])
    if symType == 'distPred':
        return (symType, ord(symbol[0].lower()) - ord('a') + 1, symbol[2:])
    if symType in ['gameFuncName', 'predGFuncName', 'predAFuncName', 'truth', 'quanti', 'connect', 'bracket', 'number']:
        return (symType, symbol)
    return (symType,)
@dataclass
class Statement:
    statement: Tuple[Tuple]

    @staticmethod
    def lex(string: str) -> 'Statement':
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
