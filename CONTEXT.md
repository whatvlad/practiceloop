# MathLoop domain language

MathLoop generates integration exercises, checks learner submissions and
keeps private learning history. These terms are canonical across the UI, API and
database.

## Language

**Problem**:
A generated integration exercise saved before it is returned to an authenticated learner.
_Avoid_: Question, task

**Attempt**:
A non-empty answer submitted for a problem, including an invalid expression.
_Avoid_: Try, response

**Solved problem**:
A problem with at least one correct attempt. Later incorrect or invalid attempts do not undo it.
_Avoid_: Correct answer count

**Reveal**:
An explicit learner request to see the final answer or the checked solution steps.
_Avoid_: Hint, automatic feedback

**Template**:
A versioned rule that generates one family of problems from bounded primitive parameters.
_Avoid_: Prompt, LLM prompt

**Difficulty**:
One of five levels determined by mathematical structure and required transformations, not by large values.
_Avoid_: Complexity score
