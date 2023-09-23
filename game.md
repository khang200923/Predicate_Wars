(semi-completed)
## Requirements:
- 2-16 **players**
- **Deck** with 128 **blank cards** (by default) that when [edited](#card-editing-rules) should have:
    - Rock-paper-scissors **tag** (publicly seen)
    - **Power cost** number (publicly seen)
    - **Effect** (written in [predicate logic](#predicate-logic-and-the-proving-system) in the form of a statement)
    - **Symbol point** of the effect
    - **Card's creator identifier** (private)
- Player **stats**:
    - **Health** (default: total players * 50) (public)
    - **Power** (default: 100) (public)
    - **Owned cards** (default: 2 blank cards) (only game function type count used in the effect and RPS tag is public)
    - **Proving potency** (default: 128) (public)

## Rules:
### Initial gameplay:
- Players sit in a circle.
- Each player is dealt eight blank cards from the deck.
- Players [edit](#card-editing-rules) their cards if they want to, each one subtracts the players' power by twice the edited card's symbol costs.
### Gameplay phases each round:
#### Phase I: Creation
- Each player chooses to take a blank card or not, during this other players decisions are private.
- The cards in the deck goes visible to all players, then gets hidden again.
- If the amount of blank cards on the deck is larger than to equal to the number of players that chooses to take the blank cards, then each of the players take one blank card.
- If the amount of blank cards on the deck is smaller than the number of players that chooses to take the blank cards, then a random player takes one blank card.
- If no one takes any card, this phase ends. If not, continue.
#### Phase II: Editing
- Each player [edits](#card-editing-rules) only 1 blank card, if desired.
- If the player does not edit a blank card, if desired, they edit an already edited card, taking twice the power cost of the overriden card.
#### Phase III: Claiming
Each player in a cycle of players, moving clockwise, starting from a random player:
- Chooses to take a specific card (that has a power cost lower or equal to the claiming player) from another player or not.
- If yes, then the claiming player's power is removed by the card's power cost; then claim cards again, if desired, up to a maximum of 8 times.
After that, each player that has [edited](#card-editing-rules) a card this round and the created card is still in their hand, takes half of the card's power cost, ceil-wise.
#### Phase IV: Playing (main phase)
Each player has proving power (public) which can only be used for this round, determined by their proving potency

Go in cycles of remained players, moving clockwise, starting from the latest player, ends when there is only 1 remaining:
- The player remains if they still have cards left, or not choosing to not remain
- The player can:
    - Play two paired cards (one that has smaller or equal symbol count is called *main* card, the other is called *secondary* card having larger symbol count) and apply its effects (if the player doesn't play a blank card; and if there is no card played yet, or the previous *main* card tag doesn't beat the player's *main* card's, or the previous *main* card has more symbol count than the player) and put them in the drop pile, or
    - Raise a card's power cost by 2 and discard it into the discard pile, or
    - Claim a card from the deck for twice the power cost (if affordable), or
    - Choose not to remain
- If chose playing, the player can then [prove](#proving-rules) a predicate game function applied to a player is true or false in the scope of two played cards by the [proving system](#predicate-logic-and-the-proving-system), only if they have enough proving power to do it, then the proving power is subtracted by the number of lines used in the proof.
- If a player loses all health (<= 0), they lose the game and cannot participate in the game in any way.
#### Phase V: Finalization
- If there is only one player left, the player in the game wins.
- Insert the discard pile and the drop pile to the deck again.
- Top [half of the number of players, floor-wise] remaining players receive 4 more proving potency. Except the last remaining player, who receives 8 more proving potency.
- Each player, if desired, buys a *proper subproof* to use in their proofs, which costs twice the symbol point of the *proof* to the proving potency.
- Each player in a cycle of players, moving clockwise, if desired, buys a *well-formed rule* to use in all proofs, which costs thrice the symbol point of the *rule* to the proving potency, or a cost higher than that chosen by the player (i.e. the potency cost of the *rule*), iff there are less than 32 *rules*.
- Each player in a cycle of players, moving clockwise, if desired, removes a *well-formed rule*, which costs the potency cost of the *rule*.
- Start a new round.
### Card editing rules:
When a player edits a card, they add/change tag, power cost (smaller or equal to their current power) and effect (written in [predicate logic](#predicate-logic-and-the-proving-system) syntax). They must add/change their identifier onto the card.
### Proving rules:
- When a player proves a predicate game function applied to a player is true or false in the scope of two paired cards, they start with a *proof* containing all of the statements in the cards as \[Axiom\] and *subproofs* the player has, then infer the *proof* repeatedly. If (\[PREDICATEACTIONFUNCTIONNAME...\](...)) is derived, then the other players can optionally prove the *proof* is contradictory. If the players do not or cannot prove, then the game effect is applied.
- When a player proves a *proof* is contradictory, they start with a *proof* containing all of the statements in the *proof*, all *rules* as \[Axiom\] and *subproofs* used in the proof with ones that the player has, then infer the *proof* repeatedly. If **A** and (¬**A**) are both derived, or tF is derived, then the game effect is not applied.
- When a player proves a potential *rule* is contradictory, they start with a *proof* containing all of the statements, all the *rules* and the potential *rule* as \[Axiom\] and *subproofs* used in the proof with ones that the player has, then infer the *proof* repeatedly. If **A** and (¬**A**) are both derived, or tF is derived, then the rule is not added.
- Proofs can only apply their effect if the player creating the proof has enough proving power (larger than the symbol point of the proof), then subtract the proving power by the symbol point of the proof.
### Game function rules:
Game functions are fixed, meaning they have a predetermined value. Action functions are not.
- \[randPlayer\](i): Returns a random player. Reference different random players by using different number i. Returns 0 otherwise.
- \[randCard\](i): Returns a random card. Reference different random cards by using different number i. Returns 0 otherwise.
- \[chosenPlayer\](i): Returns a player chosen by the player, including themselves. Reference many chosen players by using different number i. Returns 0 otherwise.
- \[chosenCard\](i): Returns a card chosen by the player owned by any player, excluding the deck and the pile. Reference many chosen cards by using different number i.
- \[playerOfChosenCard\](i): Returns a player owning the ith chosen card.
- \[health\](x): Returns health of player x. Returns 0 otherwise.
- \[power\](x): Returns power of player x. Returns 0 otherwise.
- \[potency\](x): Returns proving potency of player x. Returns 0 otherwise.
- \[symbolPoint\](x): Returns symbol point of card x. Returns 0 otherwise.
- \[powerCost\](x): Returns power cost of card x. Returns 0 otherwise.
- \[NUMBER\](x): Returns tT if x is a number. Returns tF otherwise.
- \[PLAYER\](x): Returns tT if x is a player. Returns tF otherwise.
- \[CARD\](x): Returns tT if x is a card owned by any player. Returns tF otherwise.
#### Action function rules:
If one of these action function is proven to be true, then the effect is applied:
- \[CLAIM\](x, i) for all i, x: Claim a chosen card of any player for twice its power cost
- \[ATK\](x, i) for all i, x: Subtract health of the player x by max number i (max: 20)
- \[HEAL\](x, i) for all i, x: Add health of the player x by max number i (max: 15)
- \[ADDPOWER\](x, i) for all i, x: Add power of the player x by max number i (max: 10)
- \[SUBPOWER\](x, i) for all i, x: Subtract power of the player x by max number i (max: 8)
#### *Game rule* rules
- *Rules* of the game are by default, contains 32 empty statements, associated with their potency cost, with index 0 to 31 for reference. They are saved across rounds.
- [*Base rules*](baserules.md) are built-in statements that cannot be changed, and are saved across rounds.
#### Game effect rules
There are 2 types of game effects, not based on the action function:
- Specific: an *deterministic* action function
- Conditional: (∀(x)(**C** imply **F**)) where:
    - **C** is a *deterministic WFF*
    - **F** is a *deterministic* action function

## Predicate logic and the proving system:
### *Statement*
A *statement* is an ordered list of *symbols*, which consists of:
- Variables (pure): lowercase letters ('x', 'y', 'z', ...) (symbol point each: 1)
- Predicates: uppercase letters ('P', 'Q', 'R', ...) (symbol point each: 1)
- Truth value (predicate): 'tT', 'tF' (symbol point each: 0)
- Quantifiers: '∀', '∃' (symbol point each: 2)
- Connectives: '¬', '∧', '∨', '→' (symbol point each: 1)
- Operators: '+', '-', '*', '/', 'f/', 'c/', '%' (symbol point each: 1)
- Comparators: '>', '<' (symbol point each: 1)
- Brackets: '(', ')' (symbol point each: 0)
- Equality: '=' (symbol point each: 1)
- Comma: ',' (symbol point each: 0)
- Number (variable, cannot be function name): 0, 1, 2, 3, 4, ... (symbol point each: 1)
- Distinct variables (pure variable): ('x_0', 'x_1', ..., 'y_0', 'y_1', ...) (symbol point each: 2)
- Distinct predicates (pure predicate): ('P_0', 'P_1', ..., 'Q_0', 'Q_1', ...) (symbol point each: 2)
- Functions (variable, cannot be function name): lowercase character or distinct variable or \[gameFunctionName...\] + '(' + optional( + variable + repeated(',' + variables)) + ')'
- Predicate functions (predicate): uppercase character or distinct predicate or \[PREDICATEGAMEFUNCTIONNAME...\] + '(' + optional( variable + repeated(',' + variables)) + ')'
- Game function names: '\[randPlayer\]', '\[randCard\]', '\[chosenPlayer\]', '\[chosenCard\]', '\[playerOfChosenCard\]', '\[health\]', '\[power\]', '\[potency\]', '\[symbolPoint\]', '\[powerCost\]' (symbol point each: 4)
- Predicate game function names: '\[NUMBER\]', '\[PLAYER\]', '\[CARD\]' (symbol point each: 4)
- Predicate action function names: '\[CLAIM\]', '\[ATK\]', '\[HEAL\]', '\[ADDPOWER\]', '\[SUBPOWER\]' (symbol point each: 4)
### *Proof*
A *proof* is an ordered list of *statements* and *proof tags* associated with them and a set of proofs. A *proof* is *proper* iff all *subproofs* are *proper*, and:
- *Proof tags* associated with all *statements* in it are all \[Axiom\] or,
- It is *inferred* from another *proper proof*.

A *proof* X is *inferred* from another *proof* Y having a *subproof* Z that has only one statement tagged \[Axiom\] iff it adds a new *statement* **c** and a *proof tag* \[Lemma\] associated with it, and one of these conditions is true:

(here **p1** is a statement from Y, **p2** is another statement from Y; **z1** is a statement tagged \[Axiom\] from Z, **z2**, **z3** are statements tagged \[Lemma\] from Z; **A**, **B** are WFFs; and **A**{x ↦ a} is a result formula of substituting every term a for each free occurrence of x in A; and 'd' is a  variable that does not appear in Y (except p1 and p2 where the variable appears) or **A**; and **A**(x) is a WFF that takes one variable that does not occur in **A**; every variable/predicate symbols referenced can be all replaced from a single variable/predicate symbol to another variable/predicate symbol; **x**, **y**, **z** are variables)
- Implication instantiation: If (**p1** is **A** or (¬**A**), and **p2** is **B**), or (**p1** is (¬**A**) and **p2** is (¬**B**)), then **c** is (**A** → **B**)
- Explication instantiation: If **p1** is **A** and **p2** is (¬**B**), then **c** is (¬(**A** → **B**))
- Modus ponens: If **p1** is (**A** → **B**) and **p2** is **A**, then **c** is **B**
- Universal instantiation: If **p1** is (∀(x)**A**) then **c** is **A**{x ↦ a}
- Universal generalization: If **p1** is **A**(d) then **c** is (∀(d)**A**(d))
- Universal generalization with reference: If **p1** is **A**(x) and **p2** is (∀(x)**B**(x)) then **c** is (∀(x)**A**(x))
- Existential instantiation: If **p1** is (∃(x)P(x)) then **c** is P(x)
- Existential generalization: If **p1** is P(x) then **c** is (∃(x)P(x))
- Conjunction: If **p1** is **A** and **p2** is **B** then **c** is (**A** ∧ **B**)
- Simplification: If **p1** is (**A** ∧ **B**) then **c** is **A** or **B**
- Falsy AND: If **p1** is (¬**A**) then **c** is (¬(**A** ∧ **B**))
- Addition: If **p1** is **A**, then **c** is (**A** ∨ **B**) for any **B**
- Falsy OR: If **p1** is (¬**A**) and **p2** is (¬**B**) then **c** is (¬(**A** ∨ **B**))
- Conditional proof: If **z1** is (∀(x)**A**(x)), **z2** is (∀(x)**B**(x)), and **p1** is (∀(y)**A**(y)), then **c** is (∀(y)**B**(y))
- Indirect proof: If **z1** is (∀(x)**A**(x)), **z2** is (∀(x)**B**(x)), **z3** is (∀(x)(¬**B**(x))), then **c** is (∀(y)(¬**A**(y)))
- Universal modus ponens: If **p1** is (∀(x)(**A**(x) → **B**(x))) and **p2** is **A**(y), then **c** is **B**(y)
- Existential modus ponens: If **p1** is ∃(x)(**A**(x)) and **p2** is (**A**(y) → **B**(y)) then **c** is ∃(z)(**B**(z))
- Substitution property: If **p1** is (∀(x)**A**(x)), then **c** is **A**(**x**).
- Identity: **c** is **x** = **x**
- Symmetric property: If **p1** is **x** = **y**, then **c** is **y** = **x**
- Transitive property: If **p1** is **x** = **y**, and  **p2** is **y** = **z**, then **c** is **x** = **z**
- Substitution property (equality): If **p1** is (**x** = **y**), then **c** is (f(**x**) = f(**y**)).
- Truth: **c** is tT
- Falsehood: **c** is (¬tF)
- Operator simplification: If **p1** has an occurence of (**x** **op** **y**), where **x** and **y** and numbers, and **op** is an operator, then **c** replaces the occurence with the result of the operation ('+' is addition, '-' is subtraction, '*' is multiplication, '/' is rounded division, 'f/' is floor division, 'c/' is ceil division, '%' is modulo)
- Comparison: If **p1** is has an occurence of (**x** **com** **y**), where **x** and **y** are numbers, and **com** is an comparator, then **c** replaces the occurence with the result of the comparison (the result is 'tT' or 'tF')

A *proof* has a symbol point of the total symbol points of the *symbols* of all the \[Lemma\]-tagged statements in the *proof* (excluding the *subproofs*)
### *WFF* (*Well-formed formula*)
A *statement* is a *WFF* if a statement is a predicate, a predicate function, or one of these ordered set of symbols:

(here **A** and **B** are *WFF*s, every *variable/predicate* symbols referenced can be all replaced from a single *variable/predicate* *symbol* to a *WFF/WFO* respectively)
- Forall syntax: (∀(x)**A**)
- Exists syntax: (∃(x)**A**)
- Not syntax: (¬**A**)
- And syntax: (**A**∧**B**)
- Or syntax: (**A**∨**B**)
- Imply syntax: (**A**→**B**)
- Equal syntax: (x=y)
### *WFO* (*Well-formed object*)
A *statement* is a *WFO* if a statement is a variable, or a function with its parameters being *WFO*s.
### *Deterministic statement*
A *WFO* can be *deterministic* if:
- It is a variable but not a *pure* variable
- It is a game function with only *deterministic WFOs* as its parameters

A *WFF* can be *deterministic* if:
- It is a predicate but not a *pure* predicate
- It is a predicate game/action function with only *deterministic WFOs* as its parameters
