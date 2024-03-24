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
from typing import Any, Callable, Sequence, Tuple
import sys
import os
import predicate as pd
import pwars as pw

res: Any = None

os.system('color')

sucTest = 0
totalTest = 0
failedTests = []
try: testIndex = int(sys.argv[1])
except IndexError: testIndex = None

def _formatSeq(sequence: Sequence, func: Callable = str, delimiter: str = '\n'):
    return delimiter.join(func(x) for x in sequence)

def testReturn(name: str, bl: bool, failinfo: Any, note: str = '') -> Tuple[bool, str]:
    if isinstance(failinfo, str) and failinfo.startswith(':print:'):
        failstr = ':\n' + str(failinfo)
    else:
        failstr = ': ' + repr(failinfo)
    testResChoice = {True: 'success', False: 'failure'}
    if bl:
        text = f'\033[1m\033[32mTest {name} {testResChoice[bl]}\033[0m'
    else:
        text = f'\033[1m\033[31mTest {name} {testResChoice[bl]}\033[0m{failstr}'
    text += f'\033[1m\033[36m{note}\033[0m'
    return (bl, text)

def printTest(result: Tuple[bool, str]) -> None:
    global sucTest, totalTest
    totalTest += 1

    if totalTest == testIndex or testIndex is None:
        if result[0]:
            sucTest += 1
        else:
            failedTests.append(totalTest)
        print(f'\033[1m\033[34m{totalTest}\033[0m. {result[1]}')

def test(name: str, bl: bool, failinfo: Any, note: str = ''):
    printTest(testReturn(name, bl, failinfo, note))

def summary():
    if testIndex == None:
        print(f'\n\033[1m\033[32m{sucTest}\033[0m/{totalTest} successful tests; failed [\033[1m\033[31m{repr(failedTests)[1:-1]}\033[0m]')
    else:
        print(f'\n{sucTest}/1 successful test')

test('checkSubSeq true 1', pd.checkSubSeq((1, 2, 5, 6), (2, 3, 1, 2, 5, 6, 'e')), False)

test('checkSubSeq true 2', pd.checkSubSeq((), (2, 3, 1, 2, 5, 6, 'e')), False)

test('checkSubSeq false', not pd.checkSubSeq((1, 2, 5, 7), (2, 3, 1, 2, 5, 'ye', 7)), True)

res = pd.subSeqIndexes((1, 2, 5, 6), (2, 3, 1, 2, 5, 6, 'e'))
test('subSeqIndexes 1', res == (2,), res)

res = pd.subSeqIndexes((1, 2, 5, 7), (2, 3, 1, 2, 5, 'ye', 7))
test('subSeqIndexes 2', res == (), res)

test('checkSeqForm 1', pd.checkSeqForm((4,7,4,2,7,'er',4,3,9,9,9), (4,7,4), (9,9,9)), False)

test('checkSeqForm 2', pd.checkSeqForm((4,7,4,2,7,'er',4,3,9,9,9), (4,7,4), (9,9,9), (7,'er')), False)

test('checkSeqForm 3', not pd.checkSeqForm((4,7,4,2,7,4,'er',3,9,9,9), (4,7,4), (9,9,9), (7,'er')), True)

res = pd.seqFormOptionalsIndexes((4,7,4,2,7,'er',4,3,9,9,9), (4,7,4), (9,9,9))
test('seqFormOptionalsIndexes 1', res == ((3, 8),), res)

res = pd.seqFormOptionalsIndexes((4,7,4,2,7,'er',4,3,9,9,9), (4,7,4), (9,9,9), (7,'er'))
test('seqFormOptionalsIndexes 2', res == ((3, 8), ((4, 6),)), res)

res = pd.seqFormOptionalsIndexes((4,7,4,2,7,4,'er',3,9,9,9), (4,7,4), (9,9,9), (7,'er'))
test('seqFormOptionalsIndexes 3', res is None, res)

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

state = pd.Statement.lex('(f(x) = x)')
res = state.matchingParentheses()
test('Statement.matchingParentheses 1', set(res) == {(0, 7), (2, 4)}, res)
state = pd.Statement.lex('(s = ((2*6)+(2+55*(5+1)+(43))))')
res = state.matchingParentheses()
test('Statement.matchingParentheses 2',
     set(res) == {(4, 8), (15, 19), (21, 23), (10, 24), (3, 25), (0, 26)},
     res
)
state = pd.Statement.lex('(s = ((2*6)+(2+55*(5+1)+(43)))')
res = state.matchingParentheses()
test('Statement.matchingParentheses 3', res == None, res)

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

res = pd.Statement.lex('f(455, 4333, (76 + 5))').functionArgs()
test('Statement.functionArgs 1',
     res == tuple(pd.Statement.lex(arg) for arg in ('455', '4333', '(76 + 5)')),
     str(res)
)
res = pd.Statement.lex('G(455, x, (76 + 5))').functionArgs()
test('Statement.functionArgs 2',
     res == tuple(pd.Statement.lex(arg) for arg in ('455', 'x', '(76 + 5)')),
     str(res)
)

res = pd.Statement.lex('(4 + 5)').functionArgs()
test('Statement.functionArgs 3', res is None, res)

res = pd.Statement.lex('2222222222222222222222222222222222').simple(obj=True)
test('Statement.simple 1', res, False)

res = pd.Statement.lex('[randPlayer](6, 5)').simple(obj=True) #For the sake of testing
test('Statement.simple 2', res, False)

res = pd.Statement.lex('[randPlayer](g, 5)').simple(obj=True)
test('Statement.simple 3', not res, True)

res = pd.Statement.lex('(4 + 5)').simple(obj=True)
test('Statement.simple 4', res, False)

res = pd.Statement.lex('(x + 5)').simple(obj=True)
test('Statement.simple 5', not res, True)

res = pd.Statement.lex('tT').simple()
test('Statement.simple 6', res, False)

res = pd.Statement.lex('[PLAYER](4)').simple()
test('Statement.simple 7', res, False)

res = pd.Statement.lex('[PLAYER](i)').simple()
test('Statement.simple 8', not res, True)

res = pd.Statement.lex('(5 < 3)').simple()
test('Statement.simple 9', res, False)

res = pd.Statement.lex('(5 < (4 + 5))').simple()
test('Statement.simple 10', not res, True)

res = pd.Statement.lex('(5 = 3)').simple()
test('Statement.simple 11', res, False)

res = pd.Statement.lex('(tT or tF)').simple()
test('Statement.simple 12', res, False)

res = pd.Statement.lex('(tT or P)').simple()
test('Statement.simple 13', not res, True)

res = pd.Statement.lex('$player:4$', special=True).simple(obj=True)
test('Statement.simple 14', res, False)

try:
    pd.Statement.lex('$player:4$', special=False).simple(obj=True)
except ValueError:
    test('Statement.simple 15', True, 'wait what how did this message appear')
else:
    test('Statement.simple 15', False, 'no err')

res = pd.Statement.lex('P($player:6$, $card:123$)', special=True).simple()
test('Statement.simple 15', not res, True)

res = pd.Statement.lex('[PLAYER](4)').deterministic()
test('Statement.deterministic 1', res, False)

res = pd.Statement.lex('(4 = 5)').deterministic()
test('Statement.deterministic 2', res, False)

res = pd.Statement.lex('((4 + 5) = 5)').deterministic()
test('Statement.deterministic 3', res, False)

res = pd.Statement.lex('((4 + 9) / (1 + (1 + (2 + 3))))').deterministic(obj=True)
test('Statement.deterministic 4', res, False)

res = pd.Statement.lex('(tT and (tT imply tF))').deterministic()
test('Statement.deterministic 5', res, False)

res = pd.Statement.lex('[chosenPlayer](x)').deterministic(obj=True)
test('Statement.deterministic 6', not res, True)

res = pd.Statement.lex('f(3, 4, 5)').deterministic(obj=True)
test('Statement.deterministic 7', not res, True)

res = pd.Statement.lex('[chosenPlayer](f(3, 4, 5))').deterministic(obj=True)
test('Statement.deterministic 8', not res, True)

res = pd.Statement.lex('((5 + 6) = 4)').operatorArgs()
if res is None: res = ('err',)
test('Statement.operatorArgs 1', res == (pd.Statement.lex('(5 + 6)'), pd.Statement.lex('4')), tuple(str(ree) for ree in res))

res = pd.Statement.lex('((5 f/ 6) + 4)').operatorArgs()
if res is None: res = ('err',)
test('Statement.operatorArgs 2', res == (pd.Statement.lex('(5 f/ 6)'), pd.Statement.lex('4')), tuple(str(ree) for ree in res))

res = pd.Statement.lex('((5 + 22) f/ 4)').operatorArgs()
if res is None: res = ('err',)
test('Statement.operatorArgs 3', res == (pd.Statement.lex('(5 + 22)'), pd.Statement.lex('4')), tuple(str(ree) for ree in res))

res = pd.Statement.lex('(tT or P(1, 2))').operatorArgs()
if res is None: res = ('err',)
test('Statement.operatorArgs 4', res == (pd.Statement.lex('tT'), pd.Statement.lex('P(1, 2)')), tuple(str(ree) for ree in res))

res = pd.Statement.lex('(F_265 imply T(1, 2))').operatorArgs()
if res is None: res = ('err',)
test('Statement.operatorArgs 5', res == (pd.Statement.lex('F_265'), pd.Statement.lex('T(1, 2)')), tuple(str(ree) for ree in res))

res = pd.Statement.lex('(x > 5)').operatorArgs()
if res is None: res = ('err',)
test('Statement.operatorArgs 6', res == (pd.Statement.lex('x'), pd.Statement.lex('5')), tuple(str(ree) for ree in res))

res = pd.Statement.lex('((x + 1) < 5)').operatorArgs()
if res is None: res = ('err',)
test('Statement.operatorArgs 7', res == (pd.Statement.lex('(x + 1)'), pd.Statement.lex('5')), tuple(str(ree) for ree in res))

res = pd.Statement.lex('P(1, 2)').operatorArgs()
if res is None: res = ('right',)
test('Statement.operatorArgs 8', res == ('right',), tuple(str(ree) for ree in res))

res = pd.Statement.lex('(5 = 4)').operatorSymbol()
test('Statement.operatorSymbol 1', res == ('equal',), res)

res = pd.Statement.lex('((4 + 3) + x)').operatorSymbol()
test('Statement.operatorSymbol 2', res == ('oper', '+'), res)

res = pd.Statement.lex('((2 - 3) > 4)').operatorSymbol()
test('Statement.operatorSymbol 3', res == ('compare', '>'), res)

res = pd.Statement.lex('(P imply (P and Q))').operatorSymbol()
test('Statement.operatorSymbol 4', res == ('connect', 'imply'), res)

res = [(i, state) for i, state in enumerate(pd.baseRules) if not state.wellformed()]
test('baseRules', not res, ':print:\n' + '\n'.join(f'{i}: {x}' for i, x in res))

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
test('ProofBase.inferConclusions UniversalInst 1', set(tuple(state) for state in res) ==
    {tuple(pd.Statement.lex('(y = y)'))},
    tuple(str(ree) for ree in res)
)

proof = pd.ProofBase.convert(('(forall(x)(x = a))', 'Q(y)', 'P(z)'))
res = proof.inferConclusions(pd.InferType.UniversalInst, 0, -1, pd.Statement.lex('b'))
test('ProofBase.inferConclusions UniversalInst 2', set(tuple(state) for state in res) ==
    {tuple(pd.Statement.lex('(b = a)'))},
    tuple(str(ree) for ree in res)
)

proof = pd.ProofBase.convert(('(forall(x)P)',))
res = proof.inferConclusions(pd.InferType.UniversalInst, 0, -1, pd.Statement.lex('c_33'))
test('ProofBase.inferConclusions UniversalInst 3', set(tuple(state) for state in res) ==
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

proof = pd.Proof.convert(('(P and Q)', '(not (P and Q))'),)
res = proof.contradictory()
test('Proof.contradictory 1', res, False)

proof = pd.Proof.convert(('(P and Q)', '(not (Q and R))'),)
res = proof.contradictory()
test('Proof.contradictory 2', not res, True)

proof = pd.Proof.convert(
    ("""
        (forall(x)(
            [PLAYER](x) imply
            (P(x) imply [ATK](x, 10))
        ))
    """, #0
    'P([chosenPlayer](0))'), #1
)
proof = proof.infer(0, object="[chosenPlayer](0)", conclusionI="""
    (
        [PLAYER]([chosenPlayer](0)) imply
        (P([chosenPlayer](0)) imply [ATK]([chosenPlayer](0), 10))
    )
""") #2
proof = proof.infer(conclusionI="""
    (forall(i)(
        [NUMBER](i)
        imply
        [PLAYER]([chosenPlayer](i))
    ))
""") #3
proof = proof.infer(3, object="0", conclusionI="""
    (
        [NUMBER](0)
        imply
        [PLAYER]([chosenPlayer](0))
    )
""") #4
proof = proof.infer(4, conclusionI="""
    (
        tT
        imply
        [PLAYER]([chosenPlayer](0))
    )
""") #5
proof = proof.infer(conclusionI="""
    tT
""") #6
proof = proof.infer(5, 6, conclusionI="""
    [PLAYER]([chosenPlayer](0))
""") #7
proof = proof.infer(2, 7, conclusionI="""
    (P([chosenPlayer](0)) imply [ATK]([chosenPlayer](0),10))
""") #8
proof = proof.infer(8, 1, conclusionI="""
    [ATK]([chosenPlayer](0), 10)
""") #9
test('ProofBase proving test', True, 'Easter egg???')
#print(list(statement.symbolPoint() for statement in proof.statements))
res = proof.symbolPoint()
#print(res)
test('ProofBase.symbolPoint', res == 49, res)



game = pw.PWars().advance()
test('PWars.advance 1', game.history == [pw.GameState(0, pw.GameStateType.INITIAL, None)], game.history)
test('PWars.currentGameStates 1', game.currentGameStates() == (pw.GameState(0, pw.GameStateType.INITIAL, None),), game.currentGameStates())

game = pw.PWars(INITPLAYER=3).advance()
game.action(pw.PlayerAction(
    0,
    pw.PlayerActionType.EDIT,
    ((0, pw.Card(blank=False, powerCost=5)),),
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

game = pw.PWars(INITPLAYER=3, INITCARDDECK=32).advance()
game.action(pw.PlayerAction(
    0,
    pw.PlayerActionType.EDIT,
    ((0, pw.Card(blank=False, powerCost=5)),),
))
game.advance()
game.action(pw.PlayerAction(
    0,
    pw.PlayerActionType.TAKEBLANK,
    2,
))
game.action(pw.PlayerAction(
    1,
    pw.PlayerActionType.TAKEBLANK,
    3,
))
game.action(pw.PlayerAction(
    2,
    pw.PlayerActionType.TAKEBLANK,
    5,
))
test('PWars.recentPlayerActions 3 TAKEBLANK', game.recentPlayerActions() == (
    pw.PlayerAction(player=0, type=pw.PlayerActionType.TAKEBLANK, info=2),
    pw.PlayerAction(player=1, type=pw.PlayerActionType.TAKEBLANK, info=3),
    pw.PlayerAction(player=2, type=pw.PlayerActionType.TAKEBLANK, info=5),), game.recentPlayerActions())
game.advance()
test('PWars.nextGameStates 1 advance', game.history[-1] == pw.GameState(layer=0, type=pw.GameStateType.EDITING, info=None)
     , game.history[-1])
game.action(pw.PlayerAction(
    1,
    pw.PlayerActionType.EDIT,
    ((0, pw.Card(blank=False, powerCost=5)),),
))
game.action(pw.PlayerAction(
    2,
    pw.PlayerActionType.EDIT,
    ((0, pw.Card(blank=False, powerCost=5)),),
))
res = game.currentGameStates()
test('PWars.currentGameState 4 EDIT', res == (pw.GameState(layer=0, type=pw.GameStateType.EDITING, info=None),), res)
game.advance()
res = game.currentGameStates()
test('PWars.currentGameState 5 CLAIMING', res[0] == pw.GameState(layer=0, type=pw.GameStateType.CLAIMING, info=None) and res[1].type == pw.GameStateType.RANDPLAYER, res)
game.advance()
res = game.currentGameStates()
res2 = game.players[res[2].info].power
game.action(pw.PlayerAction(
    res[2].info,
    pw.PlayerActionType.CLAIM,
    [(1, 0)],
))
test('PWars.action 1 CLAIM', res2 - game.players[res[2].info].power == 5, game.players[res[2].info].power)
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
################################################################calcInstance start
inst = game.genCalcInstance({0: 2, 13: 0}, {0: 0, 1: 3, 3: 2})
conditions = (
    inst.playerObjs == game.players,
    inst.cardObjs == game.players[0].cards + game.players[1].cards + game.players[2].cards,
    inst.chosenPlayer == {0: 2, 13: 0},
    inst.chosenCard == {0: 0, 1: 3, 3: 2}
)
test(
    'PWars.genCalcInstance',
    bl=all(conditions),
    failinfo=f':print:\n{inst.playerObjs}\n{inst.cardObjs}\n{inst.chosenPlayer}\n{inst.chosenCard}' + \
    f'\n{conditions}'
)

res = game.calcFunction('[randPlayer]', (('number', '0'),), inst)
res2 = game.calcFunction('[randPlayer]', (('number', '0'),), inst)
test('PWars.calcFunction 1 [randPlayer]', res[0][0] == 'player', res[0])
test('PWars.calcFunction 2 [randPlayer]', res == res2, f':print:\n{res}\n{res2}')

res = game.calcFunction('[randCard]', (('number', '2'),), inst)
res2 = game.calcFunction('[randCard]', (('number', '2'),), inst)
test('PWars.calcFunction 3 [randCard]', res[0][0] == 'card', res[0])
test('PWars.calcFunction 4 [randCard]', res == res2, f':print:\n{res}\n{res2}')

res = game.calcFunction('[chosenPlayer]', (('number', '13'),), inst)
test('PWars.calcFunction 5 [chosenPlayer]', res[0] == ('player', '0'), res[0])
res = game.calcFunction('[chosenPlayer]', (('number', '0'),), inst)
test('PWars.calcFunction 6 [chosenPlayer]', res[0] == ('player', '2'), res[0])

res = game.calcFunction('[chosenCard]', (('number', '1'),), inst)
test('PWars.calcFunction 7 [chosenCard]', res[0] == ('card', '3'), res[0])
res = game.calcFunction('[chosenCard]', (('number', '3'),), inst)
test('PWars.calcFunction 8 [chosenCard]', res[0] == ('card', '2'), res[0])

res = game.calcFunction('[playerOfCard]', (('card', '0'),), inst)
test(
    'PWars.calcFunction 9 [playerOfCard]',
    res[0] == ('player', '0'),
    res[0]
)

res = game.calcFunction('[health]', (('player', '0'),), inst)
test('PWars.calcFunction 10 [health]', res[0] == ('number', str(game.players[0].health)), res[0])
res = game.calcFunction('[power]', (('player', '1'),), inst)
test('PWars.calcFunction 11 [power]', res[0] == ('number', str(game.players[1].power)), res[0])
res = game.calcFunction('[potency]', (('player', '2'),), inst)
test('PWars.calcFunction 12 [potency]', res[0] == ('number', str(game.players[2].potency)), res[0])
res = game.calcFunction('[symbolPoint]', (('card', '1'),), inst)
test('PWars.calcFunction 13 [symbolPoint]', res[0] == ('number', '0'), res[0])
res = game.calcFunction('[powerCost]', (('card', '1'),), inst)
test('PWars.calcFunction 14 [powerCost]', res[0] == ('number', '0'), res[0])

res = game.calcFunction('[NUMBER]', (('number', '1'),), inst)
test('PWars.calcFunction 15 [NUMBER]', res[0] == ('truth', 'tT'), res[0])
res = game.calcFunction('[NUMBER]', (('player', '1'),), inst)
test('PWars.calcFunction 16 [NUMBER]', res[0] == ('truth', 'tF'), res[0])

res = game.calcFunction('[PLAYER]', (('player', '1'),), inst)
test('PWars.calcFunction 17 [PLAYER]', res[0] == ('truth', 'tT'), res[0])
res = game.calcFunction('[PLAYER]', (('card', '1'),), inst)
test('PWars.calcFunction 18 [PLAYER]', res[0] == ('truth', 'tF'), res[0])

res = game.calcFunction('[CARD]', (('card', '1'),), inst)
test('PWars.calcFunction 19 [CARD]', res[0] == ('truth', 'tT'), res[0])
res = game.calcFunction('[CARD]', (('number', '1'),), inst)
test('PWars.calcFunction 20 [CARD]', res[0] == ('truth', 'tF'), res[0])

res = game.calcSimple(pd.Statement.lex('((1 + 2) / 3)'), obj=True, calcInstance=inst)
test('PWars.calcSimple 1', res is None, res)
res = game.calcSimple(pd.Statement.lex('[ATK](20)'), obj=False, calcInstance=inst)
test('PWars.calcSimple 2', res is None, res)
res = game.calcSimple(pd.Statement.lex('(5 * 8)'), obj=True, calcInstance=inst)
test('PWars.calcSimple 3', res == pd.Statement.lex("40"), res)
res = game.calcSimple(pd.Statement.lex('[potency]($player:0$)', special=True), obj=True, calcInstance=inst)
test('PWars.calcSimple 4', res == pd.Statement.lex(str(game.players[0].potency)), res)

res = game.calcStatement(pd.Statement.lex('[potency]($player:0$)', special=True), obj=True, calcInstance=inst, conversion=False)
test('PWars.calcStatement 1', res == pd.Statement.lex(str(game.players[0].potency)), str(res))
res = game.calcStatement(pd.Statement.lex('(1 + ((3 * 4) - 2))'), obj=True, calcInstance=inst, conversion=False)
test('PWars.calcStatement 2', res == pd.Statement.lex(str(11)), str(res))
res = game.calcStatement(pd.Statement.lex('((1 + ((3 * 4) - 2)) = 11)'), obj=False, calcInstance=inst, conversion=False)
test('PWars.calcStatement 3', res == pd.Statement.lex('tT'), str(res))
res = game.calcStatement(pd.Statement.lex('((1 + ((3 * 4) - 2)) = 69420)'), obj=False, calcInstance=inst, conversion=False)
test('PWars.calcStatement 4', res == pd.Statement.lex('tF'), str(res))

res = game.convert(pd.Statement.lex('(x + $player:0$)', special=True), inst, False)
test('PWars.convert 1', res == pd.Statement.lex('(x + $player:0$)', special=True), str(res))
res = game.convert(pd.Statement.lex('(x + $player:0$)', special=True), inst, True)
test('PWars.convert 2', tuple(res) == pd.Statement.lex('(x + [chosenPlayer](13))').statement, str(res))
res = game.convert(pd.Statement.lex('((x + $player:2$) - $card:0$)', special=True), inst, True)
test('PWars.convert 3', tuple(res) == pd.Statement.lex('((x + [chosenPlayer](0)) - [chosenCard](0))').statement, str(res))
################################################################calcInstance end
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
game.remaining = [True, True, True]
game.playRank = []
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
test('PWars.action 3 DISCARD', res4, False)
if not res3:
    #Skip action in case of failure
    game.action(pw.PlayerAction(res[2].info, pw.PlayerActionType.DEBUGACT))
game.advance()
res = game.currentGameStates()
assert res[2].info == 1, '=('
cards =    [pw.Card(blank=True,
                    tag=pw.CardTag.PAPER,
                    powerCost=10,
                    effect=pd.Statement.lex("""
                                            (forall(x)([PLAYER](x) imply [ATK](x, 10)))
                                            """)
                    ),
            pw.Card(blank=True,
                    tag=pw.CardTag.PAPER,
                    powerCost=7,
                    effect=pd.Statement.lex("""
                                            [ATK]([chosenPlayer](0), 10)
                                            """)
                    )
            ]
game.players[res[2].info].cards = deepcopy(cards)
res2 = game.action(pw.PlayerAction(
    1,
    pw.PlayerActionType.PLAY,
    (0, 1)
))
test('PWars.action 4 PLAY', not res2, True)
res2 = game.action(pw.PlayerAction(
    1,
    pw.PlayerActionType.PLAY,
    (1, 0)
))
test('PWars.action 5 PLAY', res2, False)
test('PWars.action 6 PLAY', game.recentPlay == tuple(cards[::-1]), game.recentPlay)
game.advance()
res = game.currentGameStates()
test('PWars.action 7 PLAY', len(res) == 4 and res[3].type == pw.GameStateType.PROVE, res)
res2 = game.startAxioms(None)
test('PWars.startAxioms 1 PROVE',
    all(elem in (cards[0].effect, cards[1].effect) for elem in res2),
    res2
)
proof = pd.Proof(game.startAxioms(None))
res2 = game.action(pw.PlayerAction(
    1,
    pw.PlayerActionType.PROVE,
    (None, proof, 0)
))
test('PWars.startAxioms 1 PROVE activeDeductions',
    game.activeDeductions == [(proof, 0, 1)],
    game.activeDeductions
)
game.advance()
res = game.players[0].health
game.action(pw.PlayerAction(
    1,
    pw.PlayerActionType.EFFECTCHOOSE,
    (0, {0: 0}, dict())
))
game.advance()
res -= game.players[0].health
test('PWars.advance 2 EFFECT', res == 10, res)
game.action(pw.PlayerAction(
    2,
    pw.PlayerActionType.UNREMAIN
))
game.advance()
game.action(pw.PlayerAction(
    0,
    pw.PlayerActionType.UNREMAIN
))
game.advance()
game.action(pw.PlayerAction(
    1,
    pw.PlayerActionType.UNREMAIN
))
res = [game.players[player].potency for player in game.playRank]
game.advance()
res = [game.players[player].potency - res[i] for i, player in enumerate(game.playRank)]
test('PWars.advance 3 FINAL', res[0] < res[1] and res[1] < res[2], res)
res = game.currentGameStates()
test('PWars.advance 4 FINAL', res == (pw.GameState(0, pw.GameStateType.FINAL),), res)
game.advance()
res2 = game.players[0].potency
proof = pd.ProofBase.convert(('P',), [(pd.InferType.Addition, 0, None, '', 0)])
game.action(pw.PlayerAction(
    0,
    pw.PlayerActionType.SUBPROOF,
    proof
))
res = game.players[0].subproofs
res2 = res2 - game.players[0].potency
test('PWars.action 8 SUBPROOF', len(res) > 0 and res2 == proof.symbolPoint() * 2, res)
game.advance()
res = game.action(pw.PlayerAction(
    1,
    pw.PlayerActionType.ADDRULE,
    (0, pd.Statement.lex('C imply D'), 6)
))
test('PWars.action 1 ADDRULE', not res, res)
res = game.action(pw.PlayerAction(
    1,
    pw.PlayerActionType.ADDRULE,
    (0, pd.Statement.lex('C imply D'), 30)
))
test('PWars.action 2 ADDRULE', res and 0 in game.rules, (res, game.rules))


game = pw.PWars(INITPLAYER=2)
game.remaining = [True for _ in game.players]
game.players[0].health = 100
game.applyEffect(pd.Statement.lex('[ATK]($player:0$, 2)', special=True), pw.CalcInstance())
test('PWars.applyEffect 1 ATK', game.players[0].health == 98, game.players[0].health)
game.applyEffect(pd.Statement.lex('[HEAL]($player:0$, 6)', special=True), pw.CalcInstance())
test('PWars.applyEffect 2 HEAL', game.players[0].health == 104, game.players[0].health)
game.players[0].power = 100
game.applyEffect(pd.Statement.lex('[ADDPOWER]($player:0$, 15)', special=True), pw.CalcInstance())
test('PWars.applyEffect 3 ADDPOWER', game.players[0].power == 110, game.players[0].power)
game.applyEffect(pd.Statement.lex('[SUBPOWER]($player:0$, 0)', special=True), pw.CalcInstance())
test('PWars.applyEffect 4 SUBPOWER', game.players[0].power == 110, game.players[0].power)
game.applyEffect(pd.Statement.lex('[ATK]([chosenPlayer](1), ((5*4)+2))'), pw.CalcInstance(chosenPlayer={1: 0}))
test('PWars.applyEffect 5', game.players[0].health == 84, game.players[0].health)

summary()
