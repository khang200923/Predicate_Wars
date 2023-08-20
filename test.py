from typing import Any, Tuple
import sys
import os
import predicate as pd
import pwars as pw

res: Any = None

os.system('color')

sucTest = 0
totalTest = 0
try: testIndex = int(sys.argv[1])
except IndexError: testIndex = None

def testReturn(name: str, bl: bool, failinfo: Any, note: str = '', totalTest = totalTest) -> Tuple[bool, str]:
    failstr = ': ' + repr(failinfo)
    testResChoice = {True: 'success', False: 'failure'}
    if bl:
        text = f'\033[1m\033[32mTest {name} {testResChoice[bl]}\033[0m'
    else:
        text = f'\033[1m\033[31mTest {name} {testResChoice[bl]}\033[0m{failstr}'
    text += note
    return (bl, text)

def printTest(result: Tuple[bool, str]) -> None:
    global sucTest, totalTest
    totalTest += 1

    if totalTest == testIndex or testIndex is None:
        if result[0]:
            sucTest += 1
        print(f'\033[1m\033[34m{totalTest}\033[0m. {result[1]}')

def test(name: str, bl: bool, failinfo: Any, note: str = ''):
    printTest(testReturn(name, bl, failinfo, note))

def summary() -> None:
    if testIndex is None:
        print(f'\n{sucTest}/{totalTest} successful tests')
    else:
        print('\n1/1 successful tests')

def summary():
    if testIndex == None: print('\n{0}/{1} successful tests'.format(sucTest, totalTest))
    else: print('\n{0}/1 successful tests'.format(sucTest))

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
test('Statement.wellformed {}'.format(len(statements) + 1), pd.Statement.lex('((3+2)=5)').wellformed(), False)
test('Statement.wellformed {}'.format(len(statements) + 2), pd.Statement.lex('((3+(5+x))=(x-4))').wellformed(), False)

test('Statement.wellformedobj 1', pd.Statement.lex('(3+2)').wellformedobj(), False)

res = pd.Statement.lex('(f(x) = x)')
test('Statement.form', pd.Statement.lex('(f(x) = x)').form(
    tuple(pd.Statement.lex('(')),
    tuple(pd.Statement.lex('= x)')),
    opt1obj=True
), False)

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

state = pd.Statement.lex('(f(x) = x)')
res = state.formulasInForm(
    tuple(pd.Statement.lex('(')),
    tuple(pd.Statement.lex('= x)')),
    opt1obj=True
)
test('Statement.formulasInForm 3', res == ((pd.Statement.lex('f(x)'),),), False)

res = statements[0].substitute({
    ('var', '24'): ('var', '25'),
    ('var', '25'): ('var', '24'),
    ('pred', '17'): ('pred', '18'),
})
test('Statement.substitute 1', res == statements[0], res)
test('Statement.substitute 2', res == statements[1], res)
test('Statement.substitute 3', res != statements[2], res)

res = statements[0].complexSubstitute({
    ('var', '24'): (('var', '25'),),
    ('var', '25'): (('var', '24'),),
    ('pred', '17'): (('pred', '18'),),
})
test('Statement.complexSubstitute 1', res == statements[0], str(res))
test('Statement.complexSubstitute 2', res == statements[1], str(res))
test('Statement.complexSubstitute 3', res != statements[2], str(res))
res = pd.Statement.lex('P(x)').complexSubstitute({
    ('var', '24'): (('var', '25'), ('bracket', '('), ('bracket', ')')),
})
test('Statement.complexSubstitute 4', res == pd.Statement.lex('P(x())'), str(res))

res = pd.Statement.lex('([ATK](P(x)) and (forall(y_1)( Q_3(y_1, 5) )))').symbolPoint()
test('Statement.symbolPoint', res == 8+1+1+1+2+2+2+2+1, res)

proof = pd.ProofBase.convert(('P', '(Q(y) imply R(x))', '(A(y) and B(z))'))
res = proof.syms()
test('ProofBase.syms', set(res) == {('pred', '16'), ('pred', '17'), ('pred', '18'), ('pred', '1'), ('pred', '2'), ('var', '24'), ('var', '25'), ('var', '26')}, res)
res = proof.symsWithout(2)
test('ProofBase.symsWithout', set(res) == {('pred', '16'), ('pred', '17'), ('pred', '18'), ('var', '24'), ('var', '25')}, res)

proof = pd.ProofBase.convert(('P(b, c, c_0, d, d_0, d_1, e_0, e_1)',))
class DeterministicRNG: #Credit to an AI chatbot
    def __init__(self):
        self.num = 0

    def randint(self, a, b):
        self.num += 1
        return self.num
rng = DeterministicRNG()
res = proof.unusedVarSuggester(rng)
test('ProofBase.unusedVarSuggester 1', res == ('var', '1'), res)
res = proof.unusedVarSuggester(rng)
test('ProofBase.unusedVarSuggester 2', res == ('distVar', '2', '0'), res)
res = proof.unusedVarSuggester(rng)
test('ProofBase.unusedVarSuggester 3', res == ('distVar', '3', '1'), res)
res = proof.unusedVarSuggester(rng)
test('ProofBase.unusedVarSuggester 4', res == ('distVar', '4', '2'), res)
res = proof.unusedVarSuggester(rng)
test('ProofBase.unusedVarSuggester 5', res == ('var', '5'), res)

proof: pd.ProofBase | pd.Proof = None

proof = pd.ProofBase.convert(('P(b, c, c_0, d, d_0, d_1, e_0, e_1)',))
test('ProofBase.subProof 1', proof.subProof(), False)
proof = pd.Proof.convert(('P(b, c, c_0, d, d_0, d_1, e_0, e_1)',))
test('Proof.subProof 2', not proof.subProof(), True)
proof = pd.ProofBase.convert(('(A and B(x))',)).infer(0, 0)
test('ProofBase.subProof 3', proof.subProof(), False)

proof = pd.ProofBase.convert(('P', '(Q imply R)'))
res = proof.inferConclusions(pd.InferType.ImpliInst, 0, 1)
test('ProofBase.inferConclusions ImpliInst 1', res == (pd.Statement.lex('(P imply (Q imply R))'),), res)

proof = pd.ProofBase.convert(('(not P)', '(Q imply R)'))
res = proof.inferConclusions(pd.InferType.ImpliInst, 0, 1)
test('ProofBase.inferConclusions ImpliInst 2', res == (pd.Statement.lex('(P imply (Q imply R))'), pd.Statement.lex('((not P) imply (Q imply R))')), res)

proof = pd.ProofBase.convert(('(not P)', '(not (Q and P))'))
res = proof.inferConclusions(pd.InferType.ImpliInst, 0, 1)
test('ProofBase.inferConclusions ImpliInst 3', res == (pd.Statement.lex('(P imply (Q and P))'), pd.Statement.lex('(P imply (not (Q and P)))'), pd.Statement.lex('((not P) imply (not (Q and P)))')), res)

proof = pd.ProofBase.convert(('(not P)', '(not (Q and P))'))
res = proof.inferConclusions(pd.InferType.ExpliInst, 0, 1)
test('ProofBase.inferConclusions ExpliInst 1', res == (pd.Statement.lex('(not ((not P) imply (Q and P)))'),), tuple(str(ree) for ree in res))

proof = pd.ProofBase.convert(('(not P)', '(Q and P)'))
res = proof.inferConclusions(pd.InferType.ExpliInst, 0, 1)
test('ProofBase.inferConclusions ExpliInst 2', res == (), tuple(str(ree) for ree in res))

proof = pd.ProofBase.convert(('((A and B) imply Q)', '(A and B)'))
res = proof.inferConclusions(pd.InferType.ModPonens, 0, 1)
test('ProofBase.inferConclusions ModPonens 1', res == (pd.Statement.lex('Q'),), tuple(str(ree) for ree in res))

proof = pd.ProofBase.convert(('((A and B) and R)', '(A and B)'))
res = proof.inferConclusions(pd.InferType.ModPonens, 0, 1)
test('ProofBase.inferConclusions ModPonens 2', res == (), tuple(str(ree) for ree in res))

proof = pd.ProofBase.convert(('((A and B) imply R)', '(A and Q)'))
res = proof.inferConclusions(pd.InferType.ModPonens, 0, 1)
test('ProofBase.inferConclusions ModPonens 3', res == (), tuple(str(ree) for ree in res))

proof = pd.ProofBase.convert(('(forall(x)(x = x))', 'Q(y)', 'P(z)'))
res = proof.inferConclusions(pd.InferType.UniversalInst, 0, -1, pd.Statement.lex('y'))
test('ProofBase.inferConclusions UniversalInst 1', set(tuple(state) for state in res[:-1]) ==
    {tuple(pd.Statement.lex('(y = y)'))},
    tuple(str(ree) for ree in res)
)

proof = pd.ProofBase.convert(('(forall(x)(x = a))', 'Q(y)', 'P(z)'))
res = proof.inferConclusions(pd.InferType.UniversalInst, 0, -1, pd.Statement.lex('b'))
test('ProofBase.inferConclusions UniversalInst 2', set(tuple(state) for state in res[:-1]) ==
    {tuple(pd.Statement.lex('(b = a)'))},
    tuple(str(ree) for ree in res)
)

proof = pd.ProofBase.convert(('(forall(x)P)',))
res = proof.inferConclusions(pd.InferType.UniversalInst, 0, -1, pd.Statement.lex('c_33'))
test('ProofBase.inferConclusions UniversalInst 3', set(tuple(state) for state in res[:-1]) ==
    {tuple(pd.Statement.lex('P'))},
    tuple(str(ree) for ree in res)
)

proof = pd.ProofBase.convert(('(P(x) and (P(y) and P(z)))', 'Q(z)'))
res = proof.inferConclusions(pd.InferType.UniversalGenr, 0, -1, pd.Statement.lex('b_1'))
test('ProofBase.inferConclusions UniversalGenr 1',
    {tuple(pd.Statement.lex('(forall(b_1) (P(x) and (P(y) and P(z))))'))}.\
    issubset(set(tuple(state) for state in res)) and len(tuple(tuple(state) for state in res)) == 2,
    tuple(str(ree) for ree in res)
)

proof = pd.ProofBase.convert(('(P(x) and (P(y) and P(z)))', 'Q(z)'))
res = proof.inferConclusions(pd.InferType.UniversalGenr, 0, -1, pd.Statement.lex('z'))
test('ProofBase.inferConclusions UniversalGenr 2',
    set(tuple(state) for state in res) == set(),
    tuple(str(ree) for ree in res)
)

proof = pd.ProofBase.convert(('(forall(x)(P(x) imply Q(x)))', '(x = 10)'))
res = proof.inferConclusions(pd.InferType.UniversalGenrWRef, 1, 0)
test('ProofBase.inferConclusions UniversalGenrWRef 1', set(tuple(state) for state in res) ==
    {tuple(pd.Statement.lex('(forall(x)(x = 10))'))},
    tuple(str(ree) for ree in res)
)

proof = pd.ProofBase.convert(('(exists(x) (P and Q(x)))',))
res = proof.inferConclusions(pd.InferType.ExistentialInst, 0, -1)
test('ProofBase.inferConclusions ExistentialInst 1', set(tuple(state) for state in res) ==
    {tuple(pd.Statement.lex('(P and Q(x))'))},
    tuple(str(ree) for ree in res)
)

proof = pd.ProofBase.convert(('(forall(x) (P and Q(x)))',))
res = proof.inferConclusions(pd.InferType.ExistentialInst, 0, -1)
test('ProofBase.inferConclusions ExistentialInst 2', set(tuple(state) for state in res) ==
    set(),
    tuple(str(ree) for ree in res)
)

proof = pd.ProofBase.convert(('(P(y) and Q(x))', 'Q(a, b(a))',))
res = proof.inferConclusions(pd.InferType.ExistentialGenr, 0, -1)
test('ProofBase.inferConclusions ExistentialGenr 1', set(tuple(state) for state in res) ==
    {tuple(pd.Statement.lex('(exists(x) (P(y) and Q(x)))')), tuple(pd.Statement.lex('(exists(y) (P(y) and Q(x)))'))},
    tuple(str(ree) for ree in res)
)

proof = pd.ProofBase.convert(('(exists(x) (P(y) and Q(x)))', 'Q(a, b(a))',))
res = proof.inferConclusions(pd.InferType.ExistentialGenr, 0, -1)
test('ProofBase.inferConclusions ExistentialGenr 2', set(tuple(state) for state in res) ==
    {tuple(pd.Statement.lex('(exists(x) (exists(x) (P(y) and Q(x))))')), tuple(pd.Statement.lex('(exists(y) (exists(x) (P(y) and Q(x))))'))},
    tuple(str(ree) for ree in res)
)

proof = pd.ProofBase.convert(('(A imply B)', 'A'))
res = proof.inferConclusions(pd.InferType.Conjunc, 0, 1)
test('ProofBase.inferConclusions Conjunc', set(tuple(state) for state in res) ==
    {tuple(pd.Statement.lex('((A imply B) and A)'))},
    tuple(str(ree) for ree in res)
)

proof = pd.ProofBase.convert(('((A imply B) and A)',))
res = proof.inferConclusions(pd.InferType.Simplific, 0, -1)
test('ProofBase.inferConclusions Simplific', set(tuple(state) for state in res) ==
    {tuple(pd.Statement.lex('(A imply B)')), tuple(pd.Statement.lex('A'))},
    tuple(str(ree) for ree in res)
)

proof = pd.ProofBase.convert(('(not (A imply B))', 'C_3(x)'))
res = proof.inferConclusions(pd.InferType.FalsyAND, 0, -1)
test('ProofBase.inferConclusions FalsyAND', set(tuple(state) for state in res) ==
    {tuple(pd.Statement.lex('(not ((A imply B) and C_3(x)))')), tuple(pd.Statement.lex('(not ((A imply B) and (not C_3(x))))')), tuple(pd.Statement.lex('(not ((A imply B) and (not (A imply B))))')), tuple(pd.Statement.lex('(not ((A imply B) and (not (not (A imply B)))))'))},
    tuple(str(ree) for ree in res)
)

proof = pd.ProofBase.convert(('(A imply B)', 'C_23(x)'))
res = proof.inferConclusions(pd.InferType.Addition, 0, 1)
test('ProofBase.inferConclusions Addition', set(tuple(state) for state in res) ==
    {tuple(pd.Statement.lex('((A imply B) or C_23(x))')), tuple(pd.Statement.lex('((A imply B) or (not C_23(x)))')), tuple(pd.Statement.lex('((A imply B) or (A imply B))')), tuple(pd.Statement.lex('((A imply B) or (not (A imply B)))')),},
    tuple(str(ree) for ree in res)
)

proof = pd.ProofBase.convert(('(not A)', '(not [ATK]([randPlayer](x)))'))
res = proof.inferConclusions(pd.InferType.FalsyOR, 0, 1)
test('ProofBase.inferConclusions FalsyOR', set(tuple(state) for state in res) ==
    {tuple(pd.Statement.lex('(not (A or [ATK]([randPlayer](x))))'))},
    tuple(str(ree) for ree in res)
)

proof = pd.ProofBase.convert(('(forall(x)(A(x) imply B_2(x)))', 'A(q)'))
res = proof.inferConclusions(pd.InferType.UnivModPonens, 0, 1)
test('ProofBase.inferConclusions UnivModPonens', set(tuple(state) for state in res) ==
    {tuple(pd.Statement.lex('B_2(q)'))},
    tuple(str(ree) for ree in res)
)

proof = pd.ProofBase.convert(('(exists(x)A(x))', '(A(q) imply P(w, q))'))
res = proof.inferConclusions(pd.InferType.ExistModPonens, 0, 1)
test('ProofBase.inferConclusions ExistModPonens', set(tuple(state) for state in res) ==
    {tuple(pd.Statement.lex('(exists(x)P(w, x))')), tuple(pd.Statement.lex('(exists(q)P(w, q))'))},
    tuple(str(ree) for ree in res)
)

proof = pd.ProofBase.convert(('(forall(z)(z = z))', '(1 = 1)'))
res = proof.inferConclusions(pd.InferType.SubsProp, 0, object=pd.Statement.lex('f(x)'))
test('ProofBase.inferConclusions SubsProp', set(tuple(state) for state in res) ==
    {tuple(pd.Statement.lex('(f(x) = f(x))'))},
    tuple(str(ree) for ree in res)
)

proof = pd.ProofBase.convert(('P', '(1 = 1)'))
res = proof.inferConclusions(pd.InferType.Identity, 0, object=pd.Statement.lex('c_1( [randPlayer](1) )'))
test('ProofBase.inferConclusions Identity 1', set(tuple(state) for state in res) ==
    {tuple(pd.Statement.lex('(c_1( [randPlayer](1) ) = c_1( [randPlayer](1) ))'))},
    tuple(str(ree) for ree in res)
)

proof = pd.ProofBase.convert(('P', '(1 = 1)'))
res = proof.inferConclusions(pd.InferType.Identity, 0, object=pd.Statement.lex('x_1234567890000'))
test('ProofBase.inferConclusions Identity 2', set(tuple(state) for state in res) ==
    {tuple(pd.Statement.lex('(x_1234567890000 = x_1234567890000)'))},
    tuple(str(ree) for ree in res)
)

proof = pd.ProofBase.convert(('(x(y) = 3)', '(1 = 1)'))
res = proof.inferConclusions(pd.InferType.SymmProp, 0)
test('ProofBase.inferConclusions SymmProp', set(tuple(state) for state in res) ==
    {tuple(pd.Statement.lex('(3 = x(y))'))},
    tuple(str(ree) for ree in res)
)

proof = pd.ProofBase.convert(('(x(y) = 3)', '(3 = e)'))
res = proof.inferConclusions(pd.InferType.TransProp, 0, 1)
test('ProofBase.inferConclusions TransProp', set(tuple(state) for state in res) ==
    {tuple(pd.Statement.lex('(x(y) = e)'))},
    tuple(str(ree) for ree in res)
)

proof = pd.ProofBase.convert(('(x(y) = 3)', '(3 = e)'))
res = proof.inferConclusions(pd.InferType.SubsPropEq, 0, None, pd.Statement.lex('f'))
test('ProofBase.inferConclusions SubsPropEq', set(tuple(state) for state in res) ==
    {tuple(pd.Statement.lex('(f(x(y)) = f(3))'))},
    tuple(str(ree) for ree in res)
)

proof = pd.ProofBase.convert(('((4+3) = 7)', '(3 = e)'))
res = proof.inferConclusions(pd.InferType.OpSimplify, 0)
test('ProofBase.inferConclusions OpSimplify +', set(tuple(state) for state in res) ==
    {tuple(pd.Statement.lex('(7 = 7)'))},
    tuple(str(ree) for ree in res)
)

proof = pd.ProofBase.convert(('((4+(4-1)) = 7)', '(3 = e)'))
res = proof.inferConclusions(pd.InferType.OpSimplify, 0)
test('ProofBase.inferConclusions OpSimplify -', set(tuple(state) for state in res) ==
    {tuple(pd.Statement.lex('((4+3) = 7)'))},
    tuple(str(ree) for ree in res)
)

proof = pd.ProofBase.convert(('((4+((2*2)-1)) = (14/2))', '(3 = e)'))
res = proof.inferConclusions(pd.InferType.OpSimplify, 0)
test('ProofBase.inferConclusions OpSimplify * /', set(tuple(state) for state in res) ==
    {tuple(pd.Statement.lex('((4+(4-1)) = (14/2))')), tuple(pd.Statement.lex('((4+((2*2)-1)) = 7)'))},
    tuple(str(ree) for ree in res)
)

proof = pd.ProofBase.convert(('P((5 f/ 2), (5 c/ 2), x)', '(3 = e(x))'))
res = proof.inferConclusions(pd.InferType.OpSimplify, 0)
test('ProofBase.inferConclusions OpSimplify f/ c/', set(tuple(state) for state in res) ==
    {tuple(pd.Statement.lex('P((5 f/ 2), 3, x)')), tuple(pd.Statement.lex('P(2, (5 c/ 2), x)'))},
    tuple(str(ree) for ree in res)
)

proof = pd.ProofBase.convert(('((5 > 2) or (5 < 2))', '(3 = e(x))'))
res = proof.inferConclusions(pd.InferType.Comparison, 0)
test('ProofBase.inferConclusions Comparison', set(tuple(state) for state in res) ==
    {tuple(pd.Statement.lex('((5 > 2) or tF)')), tuple(pd.Statement.lex('(tT or (5 < 2))'))},
    tuple(str(ree) for ree in res)
)

proof = pd.Proof.convert(('(forall(x)(P(x) and Q))',), ( ('(forall(x)(P(x) and Q))', ((0, None, 'x', '(P(x) and Q)'), (1, None, '', 'P(x)'), (2, 0, '', '(forall(x)P(x))'))) ,))
res = proof.inferConclusions(pd.InferType.CondProof, 0, None, 0, 3, None)
test('Proof.inferConclusions CondProof 1', set(tuple(state) for state in res) ==
    {tuple(pd.Statement.lex('(forall(x)P(x))')),},
    tuple(str(ree) for ree in res)
)

proof = pd.Proof.convert(('(forall(x)(P(x) and Q))',), ( ('(forall(x)(P(x) and Q))', ((0, None, 'x', '(P(x) and Q)'), (1, None, '', 'P(x)'), (2, 0, '', '(forall(x)P(x))'))) ,))
res = proof.inferConclusions(pd.InferType.CondProof, 0, None, 0, 2, None)
test('Proof.inferConclusions CondProof 2', set(tuple(state) for state in res) ==
    set(),
    tuple(str(ree) for ree in res)
)

proof = pd.Proof.convert(('(1=1)',), ( ('(forall(x)(P(x) and  (not P(x) )))', (
    (0, None, 'x', '(P(x) and (not P(x)))'),
    (1, None, '', 'P(x)'),
    (1, None, '', '(not P(x))'),
    (2, 0, '', '(forall(x)P(x))'),
    (3, 0, '', '(forall(x)(not P(x)))'),
)) ,))
res = proof.inferConclusions(pd.InferType.IndProof, None, None, 0, 4, 5, pd.Statement.lex('y'))
test('Proof.inferConclusions IndProof 1', set(tuple(state) for state in res) ==
    {tuple(pd.Statement.lex('''(forall(y)(not
      (P(y) and  (not P(y) ))
    ))'''))},
    tuple(str(ree) for ree in res)
)

proof = pd.Proof.convert(('(1=1)',), ( ('(forall(x)(P(x) and  (not P(x) )))', (
    (0, None, 'x', '(P(x) and (not P(x)))'),
    (1, None, '', 'P(x)'),
    (1, None, '', '(not P(x))'),
    (2, 0, '', '(forall(x)P(x))'),
    (3, 0, '', '(forall(x)(not P(x)))'),
)) ,))
res = proof.inferConclusions(pd.InferType.IndProof, None, None, 0, 5, 4, pd.Statement.lex('y'))
test('Proof.inferConclusions IndProof 2', set(tuple(state) for state in res) ==
    set(),
    tuple(str(ree) for ree in res)
)

game = pw.PWars().advance()
test('PWars.advance 1', game.history == [pw.GameState(0, pw.GameStateType.INITIAL, None)], game.history)
test('PWars.currentGameStates 1', game.currentGameStates() == (pw.GameState(0, pw.GameStateType.INITIAL, None),), game.currentGameStates())

game = pw.PWars(INITPLAYER=3).advance()
game.action(pw.PlayerAction(
    0,
    pw.PlayerActionType.EDIT,
    (0, pw.Card(blank=False, powerCost=5)),
))
game.advance()
test('PWars.currentGameStates 2 EDIT', game.currentGameStates() == (pw.GameState(layer=0, type=pw.GameStateType.CREATION, info=None),), game.currentGameStates())
game.action(pw.PlayerAction(
    1,
    pw.PlayerActionType.TAKEBLANK,
    True,
))
test('PWars.recentPlayerActions 2 TAKEBLANK', game.recentPlayerActions() == (pw.PlayerAction(player=1, type=pw.PlayerActionType.TAKEBLANK, info=True),), game.recentPlayerActions())
game.advance()
test('PWars.currentGameStates 3 TAKEBLANK', game.currentGameStates() == (pw.GameState(layer=0, type=pw.GameStateType.EDITING, info=None),), game.currentGameStates())

game = pw.PWars(INITPLAYER=3, INITCARDDECK=2).advance()
game.action(pw.PlayerAction(
    0,
    pw.PlayerActionType.EDIT,
    (0, pw.Card(blank=False, powerCost=5)),
))
game.advance()
game.action(pw.PlayerAction(
    0,
    pw.PlayerActionType.TAKEBLANK,
    True,
))
game.action(pw.PlayerAction(
    1,
    pw.PlayerActionType.TAKEBLANK,
    True,
))
game.action(pw.PlayerAction(
    2,
    pw.PlayerActionType.TAKEBLANK,
    True,
))
test('PWars.recentPlayerActions 3 TAKEBLANK', game.recentPlayerActions() == (
    pw.PlayerAction(player=0, type=pw.PlayerActionType.TAKEBLANK, info=True),
    pw.PlayerAction(player=1, type=pw.PlayerActionType.TAKEBLANK, info=True),
    pw.PlayerAction(player=2, type=pw.PlayerActionType.TAKEBLANK, info=True),), game.recentPlayerActions())
game.advance()
test('PWars.nextGameStates 1 advance', game.history[-1] == pw.GameState(layer=0, type=pw.GameStateType.EDITING, info=None) and \
    game.history[-2].type == pw.GameStateType.RANDPLAYER, game.history[-2:])
game.action(pw.PlayerAction(
    1,
    pw.PlayerActionType.EDIT,
    (0, pw.Card(blank=False, powerCost=5)),
))
game.action(pw.PlayerAction(
    2,
    pw.PlayerActionType.EDIT,
    (0, pw.Card(blank=False, powerCost=5)),
))
res = game.currentGameStates()
test('PWars.currentGameState 4 EDIT', res == (pw.GameState(layer=0, type=pw.GameStateType.EDITING, info=None),), res)
game.advance()
res = game.currentGameStates()
test('PWars.currentGameState 5 CLAIMING', res[0] == pw.GameState(layer=0, type=pw.GameStateType.CLAIMING, info=None) and res[1].type == pw.GameStateType.RANDPLAYER, res)
game.advance()
res = game.currentGameStates()
game.action(pw.PlayerAction(
    res[2].info,
    pw.PlayerActionType.CLAIM,
    [(1, 0)],
))
test('PWars.action 1 CLAIM', game.players[res[2].info].power == 95, game.players[res[2].info].power)
game.advance()
res = game.currentGameStates()
test('PWars.currentGameState 6 CLAIM', res[0] == pw.GameState(layer=0, type=pw.GameStateType.CLAIMING, info=None) and res[1].type == pw.GameStateType.RANDPLAYER and res[2].type == pw.GameStateType.TURN and \
    res[2].info == (res[1].info + 1) % game.INITPLAYER, res)
game.advance()
game.advance()
game.advance()
res = game.currentGameStates()
test('PWars.currentGameState 7 CLAIMING', res[0] == pw.GameState(layer=0, type=pw.GameStateType.MAIN, info=None) and res[1].type == pw.GameStateType.RANDPLAYER and res[2].type == pw.GameStateType.TURN and \
    res[2].info == res[1].info, res)
game.action(pw.PlayerAction(
    res[2].info,
    pw.PlayerActionType.UNREMAIN,
))
res2 = game.remaining
test('PWars.currentGameState 8 UNREMAIN', res2 == [i != res[2].info for i in range(game.INITPLAYER)], res2)
game.advance()
res = game.currentGameStates()
pwer = game.players[res[1].info].power
res2 = [player.power for player in game.players]
game.action(pw.PlayerAction(
    res[2].info,
    pw.PlayerActionType.CLAIMPLAY,
    [(2, 0)]
))
res2 = sum(x - y == 10 for x, y in zip(res2, [player.power for player in game.players])) == 1
test('PWars.action 2 CLAIMPLAY', res2, False)
game.advance()
while game.currentGameStates()[2].info != 0:
    game.action(pw.PlayerAction(res[2].info, pw.PlayerActionType.DEBUGACT))
    game.advance()
res = game.currentGameStates()
res2 = tuple(game.players[res[2].info].cards)
res3 = game.action(pw.PlayerAction(
    res[2].info,
    pw.PlayerActionType.DISCARD,
    0
))
res4 = game.players[res[2].info].cards == list(res2[1:]) and len(game.discardPile) == 1
test('PWars.action 3 DISCARD', res4, ('\n'.join(f'{str(a)}' for a in
                                                     (res3, game.players[res[2].info].cards, res2, game.discardPile, res[2].info)
)), ' (might fail sometimes)')

summary()
