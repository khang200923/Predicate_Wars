from typing import Any
import sys
import os
import predicate as pd

res: Any = None

os.system('color')

def test(name: str, bl: bool, failinfo: Any, note: str = ''):
    failstr = ': ' + repr(failinfo)

    if bl: print('\033[1m\033[32mTest {0} success\033[0m'.format(name) + note)
    else: print('\033[1m\033[31mTest {0} failure\033[0m{1}'.format(name, failstr) + note)

test('_checkSubSeq true 1', pd._checkSubSeq((1, 2, 5, 6), (2, 3, 1, 2, 5, 6, 'e')), False)

test('_checkSubSeq true 2', pd._checkSubSeq((), (2, 3, 1, 2, 5, 6, 'e')), False)

test('_checkSubSeq false', not pd._checkSubSeq((1, 2, 5, 7), (2, 3, 1, 2, 5, 'ye', 7)), True)

res = pd._subSeqIndexes((1, 2, 5, 6), (2, 3, 1, 2, 5, 6, 'e'))
test('_subSeqIndexes 1', res == (2,), res)

res = pd._subSeqIndexes((1, 2, 5, 7), (2, 3, 1, 2, 5, 'ye', 7))
test('_subSeqIndexes 2', res == (), res)

test('_checkSeqForm 1', pd._checkSeqForm((4,7,4,2,7,'er',4,3,9,9,9), (4,7,4), (9,9,9)), False)

test('_checkSeqForm 2', pd._checkSeqForm((4,7,4,2,7,'er',4,3,9,9,9), (4,7,4), (9,9,9), (7,'er')), False)

test('_checkSeqForm 3', not pd._checkSeqForm((4,7,4,2,7,4,'er',3,9,9,9), (4,7,4), (9,9,9), (7,'er')), True)

res = pd._seqFormOptionalsIndexes((4,7,4,2,7,'er',4,3,9,9,9), (4,7,4), (9,9,9))
test('_seqFormOptionalsIndexes 1', res == ((3, 8),), res)

res = pd._seqFormOptionalsIndexes((4,7,4,2,7,'er',4,3,9,9,9), (4,7,4), (9,9,9), (7,'er'))
test('_seqFormOptionalsIndexes 2', res == ((3, 8), ((4, 6),)), res)

res = pd._seqFormOptionalsIndexes((4,7,4,2,7,4,'er',3,9,9,9), (4,7,4), (9,9,9), (7,'er'))
test('_seqFormOptionalsIndexes 3', res == None, res)

statements = tuple(pd.Statement.lex(x) for x in (
    """
    (forall(x)(
        P(x) imply
        (exists(y)(
            Q(x) or P(y)
        ))
    ))
    """, #0
    """
    (forall(y)(
        P(y) imply
        (exists(x)(
            R(y) or P(x)
        ))
    ))
    """, #1
    """
    (forall(x)(
        P(y) imply
        (exists(x)(
            Q(y) or P(x)
        ))
    ))
    """, #2
    """
    (forall(x)(
        P(y) imply
        (exists(x)(
            P(y) or P(x)
        ))
    ))
    """, #3
    """
    (forall(x)(
        forall(y)(
            ((x = y) imply ( (P(x) and P(y)) or (
                (not P(x)) and (not P(y))
            ) )) and P( f(x,y,a,b,c) )
        )
    ))
    """, #4
    """
    (forall(f)(
        P(f) imply R(g,f)
    ))
    """, #5
))

test('Statement.__eq__ 1', statements[0] == statements[0], False)
test('Statement.__eq__ 2', statements[0] == statements[1], False)
test('Statement.__eq__ 3', not statements[0] == statements[2], True)
test('Statement.__eq__ 4', not statements[0] == statements[3], True)

for index, state in enumerate(statements):
    test('Statement.wellformed {}'.format(index + 1), statements[index].wellformed(), False)

res = statements[4].formulasInForm(
    tuple(pd.Statement.lex('(forall(x)')),
    tuple(pd.Statement.lex(')'))
)
test('Statement.formulasInForm 1', res == (( pd.Statement.lex("""
    (forall(y)(
            ((x = y) imply ( (P(x) and P(y)) or (
                (not P(x)) and (not P(y))
            ) )) and P( f(x,y,a,b,c) )
        ))
"""), ),), res)

res = statements[5].formulasInForm(
    tuple(pd.Statement.lex('(forall(f)(')),
    tuple(pd.Statement.lex('))')),
    tuple(pd.Statement.lex(' imply ')),
)
test('Statement.formulasInForm 2', res == (( pd.Statement.lex("P(f)"), pd.Statement.lex("R(a,x)") ),), res)

res = statements[0].substitute({
    ('var', '24'): ('var', '25'),
    ('var', '25'): ('var', '24'),
    ('pred', '17'): ('pred', '18'),
})
test('Statement.substitute 1', res == statements[0], res)
test('Statement.substitute 2', res == statements[1], res)
test('Statement.substitute 3', res != statements[2], res)


states = ('P', '(Q imply R)')
states = [pd.Statement.lex(state) for state in states]
proof = pd.ProofBase(states, [pd.StateTag.AXIOM for _ in states])
res = proof.inferConclusions(pd.InferType.ImpliInst, 0, 1)
test('ProofBase.inferConclusions ImpliInst 1', res == (pd.Statement.lex('(P imply (Q imply R))'),), res)

states = ('(not P)', '(Q imply R)')
states = [pd.Statement.lex(state) for state in states]
proof = pd.ProofBase(states, [pd.StateTag.AXIOM for _ in states])
res = proof.inferConclusions(pd.InferType.ImpliInst, 0, 1)
test('ProofBase.inferConclusions ImpliInst 2', res == (pd.Statement.lex('(P imply (Q imply R))'), pd.Statement.lex('((not P) imply (Q imply R))')), res)

states = ('(not P)', '(not (Q and P))')
states = [pd.Statement.lex(state) for state in states]
proof = pd.ProofBase(states, [pd.StateTag.AXIOM for _ in states])
res = proof.inferConclusions(pd.InferType.ImpliInst, 0, 1)
test('ProofBase.inferConclusions ImpliInst 3', res == (pd.Statement.lex('(P imply (Q and P))'), pd.Statement.lex('(P imply (not (Q and P)))'), pd.Statement.lex('((not P) imply (not (Q and P)))')), res)

states = ('(not P)', '(not (Q and P))')
states = [pd.Statement.lex(state) for state in states]
proof = pd.ProofBase(states, [pd.StateTag.AXIOM for _ in states])
res = proof.inferConclusions(pd.InferType.ExpliInst, 0, 1)
test('ProofBase.inferConclusions ExpliInst 1', res == (pd.Statement.lex('(not ((not P) imply (Q and P)))'),), tuple(str(ree) for ree in res))

states = ('(not P)', '(Q and P)')
states = [pd.Statement.lex(state) for state in states]
proof = pd.ProofBase(states, [pd.StateTag.AXIOM for _ in states])
res = proof.inferConclusions(pd.InferType.ExpliInst, 0, 1)
test('ProofBase.inferConclusions ExpliInst 2', res == (), tuple(str(ree) for ree in res))
