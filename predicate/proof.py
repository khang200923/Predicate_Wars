"""
Provides essential classes and methods for proving predicate logic statements.
"""
from copy import deepcopy
from dataclasses import dataclass, field
from enum import Enum
from itertools import combinations
import random
from typing import Any, List, Optional, Set, Tuple

from predicate.statement import Statement, baseRules
from predicate.utils import doOperator, smallestMissingInteger

class StateTag(Enum):
    AXIOM = 0
    LEMMA = 1

class InferType(Enum):
    ImpliInst = 12
    ExpliInst = 11
    ModPonens = 0
    UniversalInst = 2
    UniversalGenr = 3
    UniversalGenrWRef = 25
    ExistentialInst = 4
    ExistentialGenr = 5
    Conjunc = 6
    Simplific = 7
    FalsyAND = 15
    Addition = 8
    FalsyOR = 16
    UnivModPonens = 9
    ExistModPonens = 10
    SubsProp = 17
    Identity = 18
    SymmProp = 19
    TransProp = 20
    SubsPropEq = 26
    OpSimplify = 21
    Comparison = 22
    RuleInclusion = 27

    CondProof = 23
    IndProof = 24

premiseUsesOfInferType = { #(p1, p2, x, z1, z2, z3)
    InferType.ImpliInst: (True, True, False, False, False, False),
    InferType.ExpliInst: (True, True, False, False, False, False),
    InferType.ModPonens: (True, True, False, False, False, False),
    InferType.UniversalInst: (True, False, True, False, False, False),
    InferType.UniversalGenr: (True, False, True, False, False, False),
    InferType.UniversalGenrWRef: (True, True, False, False, False, False),
    InferType.ExistentialInst: (True, False, False, False, False, False),
    InferType.ExistentialGenr: (True, False, False, False, False, False),
    InferType.Conjunc: (True, True, False, False, False, False),
    InferType.Simplific: (True, False, False, False, False, False),
    InferType.FalsyAND: (True, False, False, False, False, False),
    InferType.Addition: (True, False, False, False, False, False),
    InferType.FalsyOR: (True, True, False, False, False, False),
    InferType.UnivModPonens: (True, True, False, False, False, False),
    InferType.ExistModPonens: (True, True, False, False, False, False),
    InferType.SubsProp: (True, False, True, False, False, False),
    InferType.Identity: (False, False, True, False, False, False),
    InferType.SymmProp: (True, False, False, False, False, False),
    InferType.TransProp: (True, True, False, False, False, False),
    InferType.SubsPropEq: (True, False, True, False, False, False),
    InferType.OpSimplify: (True, False, False, False, False, False),
    InferType.Comparison: (True, False, False, False, False, False),
    InferType.RuleInclusion: (False, False, False, False, False, False),

    InferType.CondProof: (True, False, False, True, True, False),
    InferType.IndProof: (False, False, True, True, True, True),
}

class InferenceError(Exception): pass

@dataclass
class ProofBase:
    """
    Contains a list of Statements, with no subproof, and a list of inference.
    """
    statements: List[Statement] = field(default_factory=list)
    stateTags: List[StateTag] = None
                #[(inferType, premise1index, premise2index, object, conclusionIndex)...]
    inferences: List[Tuple[InferType, int, int, Statement, int] | None] = field(default_factory=list)

    def __post_init__(self):
        if self.stateTags is None:
            self.stateTags = [StateTag.AXIOM for _ in self.statements]

    @staticmethod
    def convert(
        strAxioms: Tuple[str],
        inferences: Optional[List[Tuple[InferType | None, int, int | None, Statement, int | str]]] = None
    ) -> 'ProofBase':
                                                   #[(inferType, premise1index, premise2index, object, conclusionIndex | conclusion)...]
        """
        Convert from strings of axioms to proof.
        """
        if inferences is None:
            inferences = []
        states = [Statement.lex(state) for state in strAxioms]
        proof = ProofBase(states, [StateTag.AXIOM for _ in states], [None for _ in states])
        for index, (_, premise1Index, premise2Index, object, conclusionI) in enumerate(inferences):
            if isinstance(conclusionI, int):
                proof = proof.infer(premise1Index, premise2Index, Statement.lex(object), conclusionI)
            elif isinstance(conclusionI, str):
                proof = proof.infer(premise1Index, premise2Index, Statement.lex(object), Statement.lex(conclusionI))
            else:
                raise TypeError(
                    f'''ProofBase.convert only supports conclusionI param types of int and str, your type is: {str(type(conclusionI))} at index {str(index)}'''
                )
        return proof

    def __getitem__(self, index: int) -> dict[str, Any]:
        try:
            return {
                'state': self.statements[index],
                'tag': self.stateTags[index],
                'infer': self.inferences[index]
            }
        except IndexError:
            return {
                'state': self.statements[index],
                'tag': self.stateTags[index],
                'infer': None
            }

    def syms(self) -> Set[Tuple]:
        """
        Returns vars and preds used in proof.
        """
        return {sym for state in self.statements for sym in state.syms()}

    def subProof(self) -> Set[Tuple]:
        """
        Check if this ProofBase can be a subproof.
        """

        if isinstance(self, Proof): return False
        return self.stateTags[0] == StateTag.AXIOM and \
        all(tag == StateTag.LEMMA for tag in self.stateTags[1:])

    def symsWithout(self, stateIndex) -> Set[Tuple]:
        """
        Returns vars and preds used in proof, without the statement on specified index.
        """
        return {
            sym
            for state in
            (state for index, state in enumerate(self.statements) if index != stateIndex)
            for sym in state.syms()
        }

    def unusedVarSuggester(self, randomClass = random):
        """
        Suggests an unused variable name based on existing syms in random.
        """
        char = randomClass.randint(1, 26)
        syms = self.syms()
        syms = {sym for sym in syms if sym[0] in ['var', 'distVar'] and sym[1] == str(char)}
        height = smallestMissingInteger(
            tuple(
                -1 if sym[0] == 'var' else int(sym[2])
                for sym in syms
            ),
            default=-1,
            ground=-1
        )
        if height == -1: return ('var', str(char))
        return ('distVar', str(char), str(height))

    def inferConclusions(
            self,
            inferType: InferType,
            premise1Index: int,
            premise2Index: int = None,
            object: Statement = Statement(())
        ) -> Tuple[Statement]:
        """
        Infers the proof and yields conclusions.
        """

        premiseUses = premiseUsesOfInferType[inferType]
        if premiseUses[0]:
            premise1: Statement = self[premise1Index]['state']
            if not premise1.wellformed():
                raise InferenceError('Premise 1 is ill-formed')
        if premiseUses[1]:
            premise2: Statement = self[premise2Index]['state']
            if not premise2.wellformed():
                raise InferenceError('Premise 2 is ill-formed')
        if premiseUses[2]:
            if not object.wellformedobj():
                raise InferenceError('Object is ill-formed')

        conclusions = []

        match inferType:
            case InferType.ImpliInst:
                A = premise1
                try: notA = premise1.formulasInForm(
                    (
                        ('bracket', '('),
                        ('connect', 'not'),
                    ),
                    (
                        ('bracket', ')'),
                    ),
                )[0][0]
                except TypeError: notA = None
                B = premise2
                try: notB = premise2.formulasInForm(
                    (
                        ('bracket', '('),
                        ('connect', 'not'),
                    ),
                    (
                        ('bracket', ')'),
                    ),
                )[0][0]
                except TypeError: notB = None
                if notA:
                    if notB:
                        conclusions.append(
                            Statement( (('bracket', '('),) ) + \
                            notA + \
                            Statement( (('connect', 'imply'),) ) + \
                            notB + \
                            Statement( (('bracket', ')'),) )
                        )
                    conclusions.append(
                        Statement( (('bracket', '('),) ) + \
                        notA + \
                        Statement( (('connect', 'imply'),) ) + \
                        B + \
                        Statement( (('bracket', ')'),) )
                    )
                conclusions.append(
                    Statement( (('bracket', '('),) ) + \
                    A + \
                    Statement( (('connect', 'imply'),) ) + \
                    B + \
                    Statement( (('bracket', ')'),) )
                )
            case InferType.ExpliInst:
                A = premise1
                try: notB = premise2.formulasInForm(
                    (
                        ('bracket', '('),
                        ('connect', 'not'),
                    ),
                    (
                        ('bracket', ')'),
                    ),
                )[0][0]
                except TypeError: notB = None
                if notB:
                    conclusions.append(
                        Statement( (('bracket', '('), ('connect', 'not'), ('bracket', '(')) ) + \
                        A + \
                        Statement( (('connect', 'imply'),) ) + \
                        notB + \
                        Statement( (('bracket', ')'), ('bracket', ')')) )
                    )
            case InferType.ModPonens:
                A = premise2
                try: Bb = premise1.formulasInForm(
                    (
                        ('bracket', '('),
                    ),
                    (
                        ('bracket', ')'),
                    ),
                    (
                        ('connect', 'imply'),
                    ),
                )[0]
                except TypeError: Bb = None
                if Bb and tuple(Bb[0]) == tuple(A): conclusions.append(Bb[1])
            case InferType.UniversalInst:
                try: A = premise1.formulasInForm(
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
                )[0][0]
                except TypeError: pass
                else:
                    if object.wellformedobj():
                        thatVar = premise1[3]
                        conclusions.append(A.complexSubstitute({thatVar: tuple(object)}))
                    else:
                        raise InferenceError('Object must be well formed')
            case InferType.UniversalGenr:
                if len(object) == 1 and \
                object[0][0] in ('var', 'distVar') and \
                object[0] not in self.symsWithout(premise1Index):
                    uniqueVars1 = (object[0], self.unusedVarSuggester())
                    for uniqueVar in uniqueVars1:
                        conclusions.append(Statement( (
                            ('bracket', '('),
                            ('quanti', 'forall'),
                            ('bracket', '('),
                            uniqueVar,
                            ('bracket', ')'),
                        ) ) + premise1 + Statement( (
                            ('bracket', ')'),
                        ) ))
            case InferType.UniversalGenrWRef:
                if premise2.form(
                        (
                            ('bracket', '('),
                            ('quanti', 'forall'),
                            ('bracket', '('),
                            ('var', '0'),
                            ('bracket', ')'),
                        ), (
                            ('bracket', ')'),
                        )
                    ):
                    x = premise2[3]
                    conclusions.append(Statement( (
                        ('bracket', '('),
                        ('quanti', 'forall'),
                        ('bracket', '('),
                        x,
                        ('bracket', ')'),
                    ) ) + premise1 + Statement( (
                        ('bracket', ')'),
                    ) ))
            case InferType.ExistentialInst:
                try: A = premise1.formulasInForm(
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
                )[0][0]
                except TypeError: A = None
                if A:
                    conclusions.append(A)
            case InferType.ExistentialGenr:
                for var in (sym for sym in premise1.syms() if 'ar' in sym[0]):
                    conclusions.append(
                        Statement((
                            ('bracket', '('),
                            ('quanti', 'exists'),
                            ('bracket', '('),
                            var,
                            ('bracket', ')'),
                        )) + premise1 + Statement((
                            ('bracket', ')'),
                        ))
                    )
            case InferType.Conjunc:
                conclusions.append(
                    Statement((
                        ('bracket', '('),
                    )) + premise1 + Statement((
                        ('connect', 'and'),
                    )) + premise2 + Statement((
                        ('bracket', ')'),
                    ))
                )
            case InferType.Simplific:
                try: A, B = premise1.formulasInForm(
                    (('bracket', '('),),
                    (('bracket', ')'),),
                    (('connect', 'and'),),
                )[0]
                except TypeError: A, B = (None, None)
                if A and B:
                    conclusions.append(A)
                    conclusions.append(B)
            case InferType.FalsyAND:
                try: A = premise1.formulasInForm(
                    (('bracket', '('),
                     ('connect', 'not')),
                    (('bracket', ')'),),
                )[0][0]
                except TypeError: A = None
                if A:
                    for B in self.statements:
                        conclusions.append(
                            Statement((
                                ('bracket', '('),
                                ('connect', 'not'),
                                ('bracket', '(')
                            )) +
                            A +
                            Statement((
                                ('connect', 'and'),
                            )) +
                            B +
                            Statement((
                                ('bracket', ')'),
                                ('bracket', ')'),
                            ))
                        )
                        conclusions.append(
                            Statement((
                                ('bracket', '('),
                                ('connect', 'not'),
                                ('bracket', '(')
                            )) +
                            A +
                            Statement((
                                ('connect', 'and'),
                                ('bracket', '('),
                                ('connect', 'not'),
                            )) +
                            B +
                            Statement((
                                ('bracket', ')'),
                                ('bracket', ')'),
                                ('bracket', ')'),
                            ))
                        )
            case InferType.Addition:
                for premise2 in self.statements:
                    conclusions.append(
                        Statement((
                            ('bracket', '('),
                        )) +
                        premise1 +
                        Statement((
                            ('connect', 'or'),
                        )) +
                        premise2 +
                        Statement((
                            ('bracket', ')'),
                        ))
                    )
                    conclusions.append(
                        Statement((
                            ('bracket', '('),
                        )) +
                        premise1 +
                        Statement((
                            ('connect', 'or'),
                            ('bracket', '('),
                            ('connect', 'not'),
                        )) +
                        premise2 +
                        Statement((
                            ('bracket', ')'),
                            ('bracket', ')'),
                        ))
                    )
            case InferType.FalsyOR:
                try: A = premise1.formulasInForm(
                    (('bracket', '('),
                     ('connect', 'not')),
                    (('bracket', ')'),),
                )[0][0]
                except TypeError: A = None
                try: B = premise2.formulasInForm(
                    (('bracket', '('),
                     ('connect', 'not')),
                    (('bracket', ')'),),
                )[0][0]
                except TypeError: B = None
                if A and B:
                    conclusions.append(
                        Statement((
                            ('bracket', '('),
                            ('connect', 'not'),
                            ('bracket', '(')
                        )) +
                        A +
                        Statement((
                            ('connect', 'or'),
                        )) +
                        B +
                        Statement((
                            ('bracket', ')'),
                            ('bracket', ')'),
                        ))
                    )
            case InferType.UnivModPonens:
                try: Ax, Bx = premise1.formulasInForm((
                    ('bracket', '('),
                    ('quanti', 'forall'),
                    ('bracket', '('),
                    ('var', '0'),
                    ('bracket', ')'),
                    ('bracket', '('),
                ), (
                    ('bracket', ')'),
                    ('bracket', ')'),
                ), (
                    ('connect', 'imply'),
                ),)[0]
                except TypeError: Ax, Bx = (None, None)
                if Ax and Bx:
                    assert premise1[3][0] in ['var', 'distVar'], 'brah'
                    bol, maps = Ax.eq(premise2)
                    x = premise1[3]
                    if bol and x in Ax.syms():
                        y = maps[x]
                        conclusions.append(Bx.substitute({x: y}))
            case InferType.ExistModPonens:
                try: Ax = premise1.formulasInForm((
                    ('bracket', '('),
                    ('quanti', 'exists'),
                    ('bracket', '('),
                    ('var', '0'),
                    ('bracket', ')'),
                ), (
                    ('bracket', ')'),
                ),)[0][0]
                except TypeError: Ax = None
                else:
                    x = premise1[3]
                    try: Ay, By = premise2.formulasInForm((
                        ('bracket', '('),
                    ), (
                        ('bracket', ')'),
                    ), (
                        ('connect', 'imply'),
                    ),)[0]
                    except TypeError: Ay, By = (None, None)
                    else:
                        bol, maps = Ax.eq(Ay)
                        if bol:
                            y = maps[x]
                            for z in (
                                sym for sym in self.syms() - By.syms()
                                if sym[0] in ['var', 'distVar']
                            ):
                                conclusions.append(
                                    Statement.lex('(exists(') +
                                    Statement((z,)) +
                                    Statement.lex(')') +
                                    By.substitute({y: z}) +
                                    Statement.lex(')')
                                )
                            conclusions.append(
                                Statement.lex('(exists(') +
                                Statement((y,)) +
                                Statement.lex(')') +
                                By +
                                Statement.lex(')')
                            )
            case InferType.SubsProp:
                try: A = premise1.formulasInForm((
                    ('bracket', '('),
                    ('quanti', 'forall'),
                    ('bracket', '('),
                    ('var', '0'),
                    ('bracket', ')'),
                ), (
                    ('bracket', ')'),
                ))[0][0]
                except TypeError: pass
                else:
                    x = premise1[3]
                    res = A.complexSubstitute({x: tuple(object)})
                    if res: conclusions.append(res)
            case InferType.Identity:
                conclusions.append(
                    Statement.lex('(') +
                    object +
                    Statement.lex('=') +
                    object +
                    Statement.lex(')')
                )
            case InferType.SymmProp:
                try: X, Y = premise1.formulasInForm((
                    ('bracket', '('),
                ), (
                    ('bracket', ')'),
                ), (
                    ('equal',),
                ),
                opt1obj=True,
                opt2obj=True,
                )[0]
                except TypeError: pass
                else:
                    conclusions.append(
                        Statement.lex('(') +
                        Y +
                        Statement.lex('=') +
                        X +
                        Statement.lex(')')
                    )
            case InferType.TransProp:
                try: X, Y = premise1.formulasInForm((
                    ('bracket', '('),
                ), (
                    ('bracket', ')'),
                ), (
                    ('equal',),
                ),
                opt1obj=True,
                opt2obj=True,
                )[0]
                except TypeError: pass
                else:
                    try: Y2, Z = premise2.formulasInForm((
                        ('bracket', '('),
                    ), (
                        ('bracket', ')'),
                    ), (
                        ('equal',),
                    ),
                    opt1obj=True,
                    opt2obj=True,
                    )[0]
                    except TypeError: pass
                    else:
                        if tuple(Y2) == tuple(Y):
                            conclusions.append(
                                Statement.lex('(') +
                                X +
                                Statement.lex('=') +
                                Z +
                                Statement.lex(')')
                            )
            case InferType.SubsPropEq:
                try: x, y = premise1.formulasInForm((('bracket', '('),), (('bracket', ')'),), (('equal',),),
                    opt1obj=True,
                    opt2obj=True,
                )[0]
                except TypeError: pass
                else:
                    if len(object) == 1:
                        conclusions.append(
                            Statement.lex('(') +
                            object +
                            Statement.lex('(') +
                            x +
                            Statement.lex(') = ') +
                            object +
                            Statement.lex('(') +
                            y +
                            Statement.lex('))')
                        )
            case InferType.OpSimplify: #Holy complexity (reduced)
                occurences = (
                    (
                        premise1[i+1][1 % len(premise1[i+1])],
                        premise1[i+3][1 % len(premise1[i+3])],
                        premise1[i+2][1 % len(premise1[i+2])],
                        i,
                        i+5
                    )
                    for i in range(len(premise1) - 4) if \
                        premise1[i] == ('bracket', '(') and \
                        premise1[i+4] == ('bracket', ')') and \
                        premise1[i+2][0] == 'oper'
                )
                for num1, num2, connect, start, end in occurences:
                    resOp = doOperator(num1, num2, connect)

                    if resOp is not None:
                        res = list(premise1.statement)
                        res[start:end] = (('number', resOp),)
                        conclusions.append(Statement(res))
                    else: raise InferenceError('Wrong operator; impossible.')
            case InferType.Comparison: #Holy complexity
                occurences = \
                    (
                        (
                            premise1[i+1][1 % len(premise1[i+1])],
                            premise1[i+3][1 % len(premise1[i+3])],
                            premise1[i+2][1 % len(premise1[i+2])],
                            i,
                            i+5
                        )
                        for i in range(len(premise1) - 4) if \
                            premise1[i] == ('bracket', '(') and \
                            premise1[i+4] == ('bracket', ')') and \
                            premise1[i+2][0] == 'compare'
                    )
                mapper = {True: 'tT', False: 'tF'}
                for num1, num2, connect, start, end in occurences:
                    if connect == '>':
                        res = list(premise1.statement)
                        res[start:end] = (('truth', mapper[int(num1) > int(num2)],),)
                        conclusions.append(Statement(tuple(res)))
                        continue
                    elif connect == '<':
                        res = list(premise1.statement)
                        res[start:end] = (('truth', mapper[int(num1) < int(num2)],),)
                        conclusions.append(Statement(tuple(res)))
                        continue
            case InferType.RuleInclusion:
                availableRules = filter(lambda rule: rule not in self.statements, baseRules)
                conclusions.extend(availableRules)
            case _: raise InferenceError('Unsupported infer type: {}'.format(inferType))

        return tuple(conclusions)
    def inferAllConclusions(
            self,
            premise1Index: int | None,
            premise2Index: int | None= None,
            object: Statement = Statement(())
        ) -> Tuple[Tuple[Statement, InferType]]:
        """
        Infers the proof and yields all possilble conclusions.
        """

        premise1Use = premise1Index is not None
        premise2Use = premise2Index is not None
        objectUse = tuple(object) != ()

        if premise1Use:
            premise1: Statement = self[premise1Index]['state']
            if not premise1.wellformed():
                raise InferenceError('Premise 1 is ill-formed')
        if premise2Use:
            premise2: Statement = self[premise2Index]['state']
            if not premise2.wellformed():
                raise InferenceError('Premise 2 is ill-formed')
        if objectUse:
            if not object.wellformedobj():
                raise InferenceError('Object is ill-formed')
        checkableInferTypes = tuple(iType
                                    for iType in InferType
                                    if premiseUsesOfInferType[iType] ==
                                    (premise1Use, premise2Use, objectUse, False, False, False)
                                    )
        conclusion = ()
        for inferType in checkableInferTypes:
            for conclusionState in \
            self.inferConclusions(
                inferType=inferType,
                premise1Index=premise1Index,
                premise2Index=premise2Index,
                object=object
            ):
                conclusion += ((conclusionState, inferType),)
        return conclusion
    def infer(
            self,
            premise1Index: int | None = None,
            premise2Index: int | None = None,
            object: Statement | str = Statement(()),
            conclusionI: int | Statement | str = 0
        ) -> 'ProofBase':
        """
        Infers the proof and returns the result.
        """
        if isinstance(object, str):
            object = Statement.lex(object)
        if isinstance(conclusionI, str):
            conclusionI = Statement.lex(conclusionI)
        res = deepcopy(self)
        state = 0
        conclusions = res.inferAllConclusions(premise1Index, premise2Index, object)
        if isinstance(conclusionI, int):
            state, inferType = conclusions[conclusionI]
            res.inferences += [(inferType, premise1Index, premise2Index, object, conclusionI)]
        elif isinstance(conclusionI, Statement):
            if tuple(conclusionI) not in tuple(tuple(state) for state, _ in conclusions):
                raise InferenceError('Invalid conclusion')
            conclusionIndex = tuple(tuple(state) for state, _ in conclusions).index(tuple(conclusionI))
            state, inferType = conclusions[conclusionIndex]
            res.inferences += [(inferType, premise1Index, premise2Index, object, conclusionIndex)]
        else:
            raise TypeError(
                f'''ProofBase.infer only supports conclusionI param types of int and Statement, your type is: {str(type(conclusionI))}'''
            )
        assert not isinstance(state, int), 'brah'
        res.statements += [state]
        res.stateTags += [StateTag.LEMMA]
        return res
    def symbolPoint(self) -> int:
        """
        Returns the symbol point of this ProofBase.
        """
        #TODO: Test this method
        res = 0
        for state, \
            (
                inferType,
                premise1index, premise2index,
                obj, conclusionIndex
            ), tag in zip(self.statements, self.inferences, self.stateTags):
            if tag == StateTag.AXIOM:
                continue
            res += 1
            if premiseUsesOfInferType[inferType][2]:
                res += obj.symbolPoint()
            if premiseUsesOfInferType[inferType][:2] == (False, False):
                continue
            thisSymbolPoint = state.symbolPoint()
            if premiseUsesOfInferType[inferType][:2] == (True, True):
                res += min(
                    abs(thisSymbolPoint - self.statements[premise1index].symbolPoint()),
                    abs(thisSymbolPoint - self.statements[premise2index].symbolPoint()),
                )
            if premiseUsesOfInferType[inferType][0]:
                res += abs(thisSymbolPoint - self.statements[premise1index].symbolPoint())
            if premiseUsesOfInferType[inferType][1]:
                res += abs(thisSymbolPoint - self.statements[premise2index].symbolPoint())
        return res


    def contradictory(self) -> bool:
        """
        Returns whether this proof is contradictory by finding pair 'A' and 'not A'.
        """
        pairs = combinations(self.statements, 2)
        for state1, state2 in pairs:
            state1c = state1.formulasInForm(
                (
                    ('bracket', '('),
                    ('connect', 'not'),
                ),
                (
                    ('bracket', ')'),
                ),
            )
            state2c = state2.formulasInForm(
                (
                    ('bracket', '('),
                    ('connect', 'not'),
                ),
                (
                    ('bracket', ')'),
                ),
            )
            if (state2c and tuple(state1) == tuple(state2c[0][0])) or (state1c and tuple(state2) == tuple(state1c[0][0])):
                return True
        return False

@dataclass
class Proof(ProofBase):
    """
    Contains a list of Statements, with subproofs, and a list of inference.
    """
    subproofs: List[ProofBase] = field(default_factory=list)

    @staticmethod
    def convert(
            strAxioms: Tuple[str],
            subProofs:
                      Tuple[Tuple[ str, Tuple[Tuple[int, int | None, str, int | Statement], ...] ]]
                      = ()
                ) -> 'Proof':
        states = [Statement.lex(state) for state in strAxioms]
        proof = Proof(
            states,
            [StateTag.AXIOM for _ in states],
            [None for _ in states],
            subproofs=list(
                ProofBase.convert((axiom,),
                    tuple(
                        (None, p1index, p2index, object, concI)
                        for p1index, p2index, object, concI in inference
                    )
                ) for axiom, inference in subProofs
            )
        )
        return proof

    def inferConclusions(
                         self,
                         inferType: InferType,
                         premise1Index: int,
                         premise2Index: int = None,
                         subProofIndex: int = None,
                         premise4Index: int = None,
                         premise5Index: int = None,
                         object: Statement = Statement(())
                         ) -> Tuple[Statement]:
        premiseUses = premiseUsesOfInferType[inferType]
        if premiseUses[0]:
            premise1: Statement = self[premise1Index]['state']
            if not premise1.wellformed():
                raise InferenceError('Premise 1 is ill-formed')
        if premiseUses[1]:
            premise2: Statement = self[premise2Index]['state']
            if not premise2.wellformed():
                raise InferenceError('Premise 2 is ill-formed')
        if premiseUses[2]:
            if not object.wellformedobj():
                raise InferenceError('Object is ill-formed')
        if premiseUses[3:] == (False, False, False):
            return super().inferConclusions(inferType, premise1Index, premise2Index, object)
        subproof = self.subproofs[subProofIndex]
        if premiseUses[3]:
            premise3: Statement = subproof[0]['state']
            if not premise3.wellformed():
                raise InferenceError('Premise 3 is ill-formed')
        if premiseUses[4]:
            premise4: Statement = subproof[premise4Index]['state']
            if not premise4.wellformed():
                raise InferenceError('Premise 4 is ill-formed')
        if premiseUses[5]:
            premise5: Statement = subproof[premise5Index]['state']
            if not premise5.wellformed():
                raise InferenceError('Premise 5 is ill-formed')

        conclusions = []

        match inferType:
            case InferType.CondProof:
                try:
                    Ax = premise3.formulasInForm(
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
                    )[0][0]
                    Bx = premise4.formulasInForm(
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
                    )[0][0]
                    Ay = premise1.formulasInForm(
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
                    )[0][0]
                except TypeError: pass
                else:
                    bol, _ = Ax.eq(Ay)
                    if bol:
                        x = premise3[3]
                        y = premise1[3]
                        conclusions.append(premise4.substitute({x: y}))
            case InferType.IndProof:
                try:
                    Ax = premise3.formulasInForm(
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
                    )[0][0]
                    Bx = premise4.formulasInForm(
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
                    )[0][0]
                    Bx2 = premise5.formulasInForm(
                        (
                            ('bracket', '('),
                            ('quanti', 'forall'),
                            ('bracket', '('),
                            ('var', '0'),
                            ('bracket', ')'),
                            ('bracket', '('),
                            ('connect', 'not'),
                        ),
                        (
                            ('bracket', ')'),
                            ('bracket', ')'),
                        ),
                    )[0][0]
                except TypeError: pass
                else:
                    if Bx == Bx2 and len(tuple(object)) == 1:
                        x = premise4[3]
                        y = object[0]
                        conclusions.append(
                            Statement.lex('(forall(')
                            +
                            Statement((y,))
                            +
                            Statement.lex(')(not ')
                            +
                            Ax.substitute({x: y})
                            +
                            Statement.lex('))')
                        )
        return conclusions
