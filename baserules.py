from dataclasses import dataclass
from typing import List
import re
from predicate import Statement

def _countRepeatedChars(text: str, target: str) -> int:
    count = 0
    for char in text:
        if char == target:
            count += 1
        else:
            break
    return count

@dataclass
class BRulesParseResult:
    statement: Statement
    titles: List[str] #Empty for now

def parse(text: str) -> List[BRulesParseResult]:
    rules = []
    remaining = text
    while remaining:
        stateSearch = re.search(r'~.*?~', remaining, re.MULTILINE | re.DOTALL)
        titleSearch = re.search(r'>+.*', remaining, re.MULTILINE)
        if titleSearch and (titleSearch.start() < stateSearch.start()):
            ... #Just in case when we need titles
            remaining = remaining[:titleSearch.end()]
        elif stateSearch:
            statement = Statement.lex(stateSearch.group())
            rules.append(BRulesParseResult(statement, []))
            remaining = remaining[:stateSearch.end()]
        break
    return rules

def getBaseRules():
    with open('baserules.txt', 'r', encoding='utf-8') as f:
        text = f.read()
        results = parse(text)
    return results
