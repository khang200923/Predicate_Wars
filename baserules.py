from dataclasses import dataclass
from typing import List
import re

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
    statement: str
    titles: List[str] #Empty for now

def parse(text: str) -> List[BRulesParseResult]:
    rules = []
    remaining = text
    while remaining:
        stateSearch = re.search(r'~(.*?)~', remaining, re.MULTILINE | re.DOTALL)
        titleSearch = re.search(r'>+.*', remaining, re.MULTILINE)
        if titleSearch and (not stateSearch or (titleSearch.start() < stateSearch.start())):
            ... #Just in case when we need titles
            remaining = remaining[titleSearch.end():]
        elif stateSearch:
            statement = stateSearch.group(1)
            rules.append(BRulesParseResult(statement, []))
            remaining = remaining[stateSearch.end():]
        else:
            break
    return rules

def getBaseRules():
    with open('baserules.txt', 'r', encoding='utf-8') as f:
        text = f.read()
        results = parse(text)
    return results
