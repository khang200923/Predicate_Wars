# This file is part of Predicate Wars.

# Predicate Wars is free software: you can redistribute it and/or
# modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation, either version 3 of
# the License, or (at your option) any later version.

# Predicate Wars is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.

# You should have received a copy of the GNU General Public License along
# with Predicate Wars. If not, see <https://www.gnu.org/licenses/>.
from copy import deepcopy
from dataclasses import dataclass, field
from enum import Enum
from itertools import combinations
import math
import random
import re
from typing import Any, Callable, List, Optional, Sequence, Set, Tuple

def mappableDict(dct: dict) -> bool:
    """
    Returns if dict values don't overlap.
    """
    return len(set(dct.values())) == len(dct.values())

def checkSubSeq(subseq: Sequence, seq: Sequence) -> bool:
    #From https://stackoverflow.com/questions/425604/best-way-to-determine-if-a-sequence-is-in-another-sequence
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

def subSeqIndexes(subseq: Sequence, seq: Sequence) -> Tuple[int]:
    #From https://stackoverflow.com/questions/425604/best-way-to-determine-if-a-sequence-is-in-another-sequence
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

def checkSeqForm(
        seq: Sequence,
        start: Sequence,
        end: Sequence,
        mid: Sequence=(),
        startEndMatch = lambda x, y: x == y
    ) -> bool:
    """
    Check the sequence if it is the form of [start..., ?, mid..., ?, end...].
    """
    if not startEndMatch(seq[:len(start)], start): return False
    if not startEndMatch(seq[-len(end):], end): return False
    if not checkSubSeq(mid, seq[len(start):-len(end)]): return False
    return True

def seqFormOptionalsIndexes(
        seq: Sequence,
        start: Sequence,
        end: Sequence,
        mid: Sequence = (),
        midcond: Callable[[int], bool] = lambda x: True,
        startEndMatch = lambda x, y: x == y
    ) -> Tuple[Tuple, ...] | None:
    """
    Return indexes of optional subsequences in the sequence of the seq form.
    ((subseq1start, subseq2end), ((subseq1end, subseq2start),...)?)
    Conditional function of mid filter is fed starting index to each mid
    """
    if checkSeqForm(seq, start, end, mid, startEndMatch):
        if len(mid) == 0:
            return ((len(start), len(seq) - len(end)),)
        else:
            return ((len(start), len(seq) - len(end)),
                tuple(
                    (index + len(start), index + len(start) + len(mid))
                    for index in subSeqIndexes(mid, seq[len(start):-len(end)])
                    if midcond(index + len(start))
                )
            )
    return None

def smallestMissingInteger(sequence: Sequence[int], ground=0, default=0) -> int:
    if len(sequence) == 0:
        return default
    elements = sorted(set(sequence))
    if elements[0] - ground >= 1:
        return ground
    for element, change in ((elements[i], elements[i+1] - elements[i]) for i in range(len(elements)-1)):
        if change != 1:
            return element + 1
    return max(elements) + 1

def doOperator(a: str, b: str, oper: str) -> str | None:
    match oper:
        case '+': res = int(a) + int(b)
        case '-': res = int(a) - int(b)
        case '*': res = int(a) * int(b)
        case '/': res = round(int(a) / int(b))
        case 'f/': res = math.floor(int(a) / int(b))
        case 'c/': res = math.ceil(int(a) / int(b))
        case '%': res = int(a) % int(b)
        case _: return None
    return str(res)
