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

test('_subSeqIndexes 1', pd._subSeqIndexes((1, 2, 5, 6), (2, 3, 1, 2, 5, 6, 'e')) == (2,), pd._subSeqIndexes((1, 2, 5, 6), (2, 3, 1, 2, 5, 6, 'e')))

test('_subSeqIndexes 2', pd._subSeqIndexes((1, 2, 5, 7), (2, 3, 1, 2, 5, 'ye', 7)) == (), pd._subSeqIndexes((1, 2, 5, 7), (2, 3, 1, 2, 5, 'ye', 7)))

test('_checkSeqForm 1', pd._checkSeqForm((4,7,4,2,7,'er',4,3,9,9,9), (4,7,4), (9,9,9)), False)

test('_checkSeqForm 2', pd._checkSeqForm((4,7,4,2,7,'er',4,3,9,9,9), (4,7,4), (9,9,9), (7,'er')), False)

test('_checkSeqForm 3', not pd._checkSeqForm((4,7,4,2,7,4,'er',3,9,9,9), (4,7,4), (9,9,9), (7,'er')), True)

test('_seqFormOptionalsIndexes 1', pd._seqFormOptionalsIndexes((4,7,4,2,7,'er',4,3,9,9,9), (4,7,4), (9,9,9)) == ((3, 8),),
    pd._seqFormOptionalsIndexes((4,7,4,2,7,'er',4,3,9,9,9), (4,7,4), (9,9,9))
)

test('_seqFormOptionalsIndexes 2', pd._seqFormOptionalsIndexes((4,7,4,2,7,'er',4,3,9,9,9), (4,7,4), (9,9,9), (7,'er')) == ((3, 8), ((4, 6),)),
    pd._seqFormOptionalsIndexes((4,7,4,2,7,'er',4,3,9,9,9), (4,7,4), (9,9,9), (7,'er'))
)

test('_seqFormOptionalsIndexes 3', pd._seqFormOptionalsIndexes((4,7,4,2,7,4,'er',3,9,9,9), (4,7,4), (9,9,9), (7,'er')) == None,
    pd._seqFormOptionalsIndexes((4,7,4,2,7,4,'er',3,9,9,9), (4,7,4), (9,9,9), (7,'er'))
)

statements = tuple(pd.Statement.lex(x) for x in (
    """
    (forall(x)(
        P(x) imply
        (exists(y)(
            Q(x) or P(y)
        ))
    ))
    """,
    """
    (forall(y)(
        P(y) imply
        (exists(x)(
            R(y) or P(x)
        ))
    ))
    """,
    """
    (forall(x)(
        P(y) imply
        (exists(x)(
            Q(y) or P(x)
        ))
    ))
    """,
))

test('Statement.__eq__ 1', statements[0] == statements[0], False)

test('Statement.__eq__ 2', statements[0] == statements[1], False)

test('Statement.__eq__ 3', not statements[0] == statements[2], True)
