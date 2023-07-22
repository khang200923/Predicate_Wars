(semi-completed)
## Requirements:
- 2-16 **players**
- 256 **blank cards** that when [edited](#card-editing-rules) should have:
    - Rock-paper-scissors **tag** (publicly seen)
    - **Power cost** number (publicly seen)
    - **Effect** (written in [predicate logic](#predicate-logic-and-the-proving-system) in the form of statements)
    - **Symbol point** of the effect
    - **Card's creator identifier** (private)
- **Deck** with 100 blank cards by default
- Player **stats**:
    - **Health** (default: total players * 50) (public)
    - **Power** (default: 100) (public)
    - **Owned cards** (default: 2 blank cards) (only game function type count used in the effect and RPS tag is public)
    - **Proving potency** (default: 25) (public)

## Rules:
### Initial gameplay:
- Players sit in a circle.
- Each player is dealt eight blank cards.
- Players [edit](#card-editing-rules) their cards they want to, each one subtracts the players' power by twice the edited card's symbol costs.
- Choose a random player to start the turn first.
### Gameplay phases each round:
#### Phase I: Creation
- Each player chooses to take a blank card or not, during this other players decisions are private.
- The cards in the deck goes visible to all players, then gets hidden again.
- If the amount of blank cards on the deck is larger than to equal to the number of players that chooses to take the blank cards, then each of the players take one blank card.
- If the amount of blank cards on the deck is smaller than the number of players that chooses to take the blank cards, then the latest player takes one blank card.
- If no one takes any card, this phase ends. If not, continue.
- Each of the players taking the card takes half of the card's power cost, floor-wise.
#### Phase II: Editing
- Each player [edits](#card-editing-rules) only 1 blank card, if desired.
- If the player does not edit a blank card, they edit a card with twice the power cost of the card, if desired.
#### Phase III: Claiming
Each player in a cycle of players, moving clockwise, starting from the latest player:
- chooses to take a specific card (that has a power cost lower or equal to the claiming player) from another player or not.
- If yes, then the claiming player's power is removed by the card's power cost.
After that, each player that has [edited](#card-editing-rules) a card this round and the created card is still in their hand, takes half of the card's power cost, ceil-wise.
#### Phase IV: Playing
Each player has proving power (public) which can only be used for this round, determined by their proving potency

Go in cycles of remained players, moving clockwise, starting from the latest player, ends when there is only 1 remaining:
- The player remains if they still have cards left, or not choosing to not remain
- The player can:
    - Play two cards (one that has smaller symbol count is called *main* card) and apply its effects (if there is no card played yet, or your *main* card tag beats the previous *main* card's, or (the previous *main* card has more symbol count than yours, if the previous *main* card tag doesn't beat yours)), or
    - Raise a card's power cost by 2 and discard it into the discard pile, or
    - Claim a card from the deck for twice the power cost (if affordable), or
    - Choose not to remain
- The player can then [prove](#proving-rules) a predicate game function applied to a player is true or false in the scope of a played card by the [proving system](#predicate-logic-and-the-proving-system), only if they have enough proving power to do it, then the proving power is subtracted by the number of lines used in the proof.
- If a player loses all health (to 0), they lose the game and cannot participate in the game in any way.
#### Phase V: Final
- If there is only one player left, the player in the game wins.
- Top [half of the number of players, floor-wise] remaining players receive 2 more proving potency. Except the last remaining player, who receives 5 more proving potency.
- Each player, if desired, buys a *subproof* to use in their proofs, which costs the whole symbol point of the *proof* to the proving potency.
### Card editing rules:
When a player edits a card, they add/change tag, power cost (smaller or equal to their current power) and effect (written in [predicate logic](#predicate-logic-and-the-proving-system) syntax). They must add/change their identifier onto the card.
### Proving rules:
- When a player proves a predicate game function applied to a player is true or false in the scope of a played card, they start with a *proof* containing all of the statements in the card as \[Axiom\] and subproofs the player has, then infer the *proof* repeatedly. If (\[PREDICATEACTIONFUNCTIONNAME...\](...)) is derived, then the other players can optionally prove the *proof* is contradictory. If the players do not or cannot prove, then the game effect is applied.
- When a player proves a *proof* is contradictory, they start with a *proof* containing all of the statements in the *proof* and in all the *rules* as \[Axiom\] and subproofs the player has, then infer the *proof* repeatedly. If **A** and (¬**A**) are both derived, then the game effect is not applied.
- When a player proves a potential *rule* is contradictory, they start with a *proof* containing all of the statements in all the *rules* and the potential *rule* as \[Axiom\] and subproofs the player has, then infer the *proof* repeatedly. If **A** and (¬**A**) are both derived, then the rule is not added.
- Proofs can only apply their effect if the player creating the proof has enough proving power (larger than the symbol point of the proof), then subtract the proving power by the symbol point of the proof.
### Game function rules:
Game functions are fixed, meaning they have a predetermined value. Action functions are not.
- \[randPlayer\](i): Returns a random player. Reference different random players by using different number i.
- \[randCard\](i): Returns a random card. Reference different random cards by using different number i.
- \[chosenPlayer\](i): Returns a player chosen by the player, including themselves. Reference many chosen players by using different number i.
- \[chosenCard\](i): Returns a card chosen by the player owned by any player, excluding the deck and the pile. Reference many chosen cards by using different number i.
- \[playerOfChosenCard\](i): Returns a player owning the ith chosen card.
- \[PLAYER\](x): Returns true if x is a player.
- \[CARD\](x): Returns true if x is a card owned by any player.
- \[HEALTHLOWER\](x, i) and \[HEALTHHIGHER\](x, i): Returns true if player x has lower/higher health than number i
- \[POWERLOWER\](x, i) and \[POWERHIGHER\](x, i): Returns true if player x has lower/higher power than number i
- \[PROVPOWERLOWER\](x, i) and \[PROVPOWERHIGHER\](x, i): Returns true if player x has lower/higher proving power than number i
- \[SYMBOLPOINTLOWER\](x, i) and \[SYMBOLPOINTHIGHER\](x, i): Returns true if card x has lower/higher symbol point than number i
- \[POWERCOSTLOWER\](x, i) and \[POWERCOSTHIGHER\](x, i): Returns true if card x has lower/higher power cost than number i
#### Action function rules:
If one of these action function is proven to be true, then the effect is applied:
- \[CLAIM\]() for all i, x: Claim a chosen card of any player for twice its power cost
- \[ATK\](x, i) for all i, x: Subtract health of the player x by max number i (max: 20)
- \[HEAL\](x, i) for all i, x: Add health of the player x by max number i (max: 15)
- \[ADDPOWER\](x, i) for all i, x: Add power of the player x by max number i (max: 10)
- \[SUBPOWER\](x, i) for all i, x: Subtract power of the player x by max number i (max: 8)
- \[ADDRULE\](i, **A**) for all i, x (if there is only one **A** that \[ADDRULE\](i, **A**), then apply): Replace a *rule* of index i to **A**, if the rule is empty
- \[DELETERULE\](i) for all i: Replace a *rule* of index i to empty
#### *Game rule* rules
*Rules* of the game are by default, contains 32 empty statements, with index 0 to 31 for reference. They are saved across rounds.

## Predicate logic and the proving system:
### *Statement*
A *statement* is an ordered list of *symbols*, which consists of:
- Variables: lowercase letters ('x', 'y', 'z', ...) (symbol point each: 1)
- Predicates: uppercase letters ('P', 'Q', 'R', ...) (symbol point each: 1)
- Truth value (predicate): 'tT', 'tF'
- Quantifiers: '∀', '∃' (symbol point each: 2)
- Connectives: '¬', '∧', '∨', '→' (symbol point each: 1)
- Brackets: '(', ')' (symbol point each: 0)
- Equality: '='
- Comma: ',' (symbol point each: 0)
- Underline: '_' (symbol point each: 0)
- Number (variable, cannot be function name): 0, 1, 2, 3, 4, ...
- Distinct variables (variable): ('x_0', 'x_1', ..., 'y_0', 'y_1', ...)
- Distinct predicates (predicate): ('P_0', 'P_1', ..., 'Q_0', 'Q_1', ...)
- Functions (variable, cannot be function name): lowercase character or distinct variable or \[gameFunctionName...\] + '(' + optional( + variable + repeated(',' + variables)) + ')'
- Predicate functions (predicate): uppercase character or distinct predicate or \[PREDICATEGAMEFUNCTIONNAME...\] + '(' + optional( variable + repeated(',' + variables)) + ')'
- Game function names: '\[randPlayer\]', '\[randCard\]', '\[chosenPlayer\]', '\[chosenCard\]', '\[playerOfChosenCard\]' (symbol point each: 4)
- Predicate game function names: '\[PLAYER\]', '\[CARD\]', '\[HEALTHLOWER\]', '\[HEALTHHIGHER\]', '\[POWERLOWER\]', '\[POWERHIGHER\]', '\[PROVPOWERLOWER\]', '\[PROVPOWERHIGHER\]', '\[SYMBOLPOINTLOWER\]', '\[SYMBOLPOINTHIGHER\]'
(symbol point each: 4)
- Predicate action function names: '\[CLAIM\]', '\[ATK\]', '\[HEAL\]', '\[ADDPOWER\]', '\[SUBPOWER\]' (symbol point each: 4) '\[ADDRULE\]', '\[DELETERULE\]' (symbol point each: 12)
### *Proof*
A *proof* is an ordered list of *statements* and *proof tags* associated with them and a set of proofs. A *proof* is *proper* iff all *subproofs* are *proper*, and:
- *Proof tags* associated with all *statements* in it are all \[Axiom\] or,
- It is *inferred* from another *proper proof*.

A *proof* X is *inferred* from another *proof* Y having a *subproof* Z that has only one statement tagged \[Axiom\] iff it adds a new *statement* **c** and a *proof tag* \[Lemma\] associated with it, and one of these conditions is true:

(here **p1** is a statement from Y, **p2** is another statement from Y; **z1** is a statement tagged \[Axiom\] from Z, **z2**, **z3** are statements tagged \[Lemma\] from Z; **A**, **B** are WFFs; and **A**{x ↦ a} is a result formula of substituting every term a for each free occurrence of x in A; and 'd' is a  variable that does not appear in Y (except p1 and p2 where the variable appears) or **A**; and **A**(x) is a WFF that takes one variable that does not occur in **A**; every variable/predicate symbols referenced can be all replaced from a single variable/predicate symbol to another variable/predicate symbol)
- Implication instantiation: If (**p1** is **A** or (¬**A**), and **p2** is **B**), or (**p1** is (¬**A**) and **p2** is (¬**B**)), then **c** is (**A** → **B**)
- Explication instantiation: If **p1** is **A** and **p2** is (¬**B**), then **c** is (¬(**A** → **B**))
- Modus ponens: If **p1** is (**A** → **B**) and **p2** is **A**, then **c** is **B**
- Universal instantiation: If **p1** is (∀(x)**A**) then **c** is **A**{x ↦ a}
- Universal generalization: If **p1** is **A**(d) then **c** is (∀(d)**A**(d))
- Existential instantiation: If **p1** is (∃(x)P(x)) then **c** is P(x)
- Existential generalization: If **p1** is P(x) then **c** is (∃(x)P(x))
- Conjunction: If **p1** is **A** and **p2** is **B** then **c** is (**A** ∧ **B**)
- Simplification: If **p1** is (**A** ∧ **B**) then **c** is **A** or **B**
- Falsy AND: If **p1** is (¬**A**) then **c** is (¬(**A** ∧ **B**))
- Addition: If **p1** is **A**, then **c** is (**A** ∨ **B**) for any **B**
- Falsy OR: If **p1** is (¬**A**) and **p2** is (¬**B**) then **c** is (¬(**A** ∨ **B**))
- Conditional proof: If **z1** is **A**, **z2** is **B**, and **p1** is **A**(x), then **c** is **B**(x)
- Indirect proof: If **z1** is (¬**A**), **z2** is **B**, **z3** is (¬**B**), then **c** is **A**(x)
- Universal modus ponens: If **p1** is (∀(x)(**A**(x) → **B**(x))) and **p2** is **A**(y), then **c** is **B**(y)
- Existential modus ponens: If **p1** is ∃(x)(**A**(x)) and **p2** is (**A**(y) → **B**(y)) then **c** is ∃(z)(**B**(z))
- Identity: **c** is (∀(x)(x = x))
- Symmetric property: If **p1** is x = y, then **c** is y = x
- Substitution property: If **p1** is x = y, and  **p2** is y = z, then **c** is x = z
- Truth: **c** is tT
- Falsehood: **c** is (¬tF)

A *proof* has a symbol point of the total symbol points of the *symbols* of all the \[Lemma\]-tagged statements in the *proof* (excluding the *subproofs*)
### *WFF* (*Well-formed formula*)
A *statement* is a *WFF* if a statement is a predicate, a predicate function wrapped by brackets, or one of these ordered set of symbols:

(here **A** and **B** are *WFF*s, every *variable/predicate* symbols referenced can be all replaced from a single *variable/predicate* *symbol* to another *variable/predicate* *symbol/function*)
- Forall syntax: (∀(x)**A**)
- Exists syntax: (∃(x)**A**)
- Not syntax: (¬**A**)
- And syntax: (**A**∧**B**)
- Or syntax: (**A**∨**B**)
- Imply syntax: (**A**→**B**)
- Equal syntax: (x=y)
