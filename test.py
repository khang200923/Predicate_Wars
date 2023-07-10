from typing import Any
import sys
import os
import predicate as pd

os.system('color')

def test(name: str, bl: bool, failinfo: Any, note: str = ''):
    failstr = ': ' + repr(failinfo)

    if bl: print('\033[1m\033[32mTest {0} success\033[0m'.format(name) + note)
    else: print('\033[1m\033[31mTest {0} failure\033[0m{1}'.format(name, failstr) + note)

test('_checkSubSeq true 1', pd._checkSubSeq((1, 2, 5, 6), (2, 3, 1, 2, 5, 6, 'e')), False)
test('_checkSubSeq true 2', pd._checkSubSeq((), (2, 3, 1, 2, 5, 6, 'e')), False)
test('_checkSubSeq false', not pd._checkSubSeq((1, 2, 5, 7), (2, 3, 1, 2, 5, 'ye', 7)), True)
test('_subSeqIndex 1', pd._subSeqIndex((1, 2, 5, 6), (2, 3, 1, 2, 5, 6, 'e')) == 2, pd._subSeqIndex((1, 2, 5, 6), (2, 3, 1, 2, 5, 6, 'e')))
test('_subSeqIndex 2', pd._subSeqIndex((1, 2, 5, 7), (2, 3, 1, 2, 5, 'ye', 7)) == -1, pd._subSeqIndex((1, 2, 5, 7), (2, 3, 1, 2, 5, 'ye', 7)))
test('_checkSeqForm 1', pd._checkSeqForm((4,7,4,2,7,'er',4,3,9,9,9), (4,7,4), (9,9,9)), False)
test('_checkSeqForm 2', pd._checkSeqForm((4,7,4,2,7,'er',4,3,9,9,9), (4,7,4), (9,9,9), (7,'er')), False)
test('_checkSeqForm 3', not pd._checkSeqForm((4,7,4,2,7,4,'er',3,9,9,9), (4,7,4), (9,9,9), (7,'er')), True)
test('_seqFormOptionalsIndex 1', pd._seqFormOptionalsIndex((4,7,4,2,7,'er',4,3,9,9,9), (4,7,4), (9,9,9)) == ((3, 8),),
    pd._seqFormOptionalsIndex((4,7,4,2,7,'er',4,3,9,9,9), (4,7,4), (9,9,9))
)
test('_seqFormOptionalsIndex 2', pd._seqFormOptionalsIndex((4,7,4,2,7,'er',4,3,9,9,9), (4,7,4), (9,9,9), (7,'er')) == ((3, 4), (6, 8)),
    pd._seqFormOptionalsIndex((4,7,4,2,7,'er',4,3,9,9,9), (4,7,4), (9,9,9), (7,'er'))
)
test('_seqFormOptionalsIndex 3', pd._seqFormOptionalsIndex((4,7,4,2,7,4,'er',3,9,9,9), (4,7,4), (9,9,9), (7,'er')) == None,
    pd._seqFormOptionalsIndex((4,7,4,2,7,4,'er',3,9,9,9), (4,7,4), (9,9,9), (7,'er'))
)
