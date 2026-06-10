def transform(x):
    # EVOLVE-BLOCK-START arithmetic_rule
    return x + 1
    # EVOLVE-BLOCK-END


def evaluate(eval_inputs):
    cases = eval_inputs["cases"]
    expected = eval_inputs["expected"]
    correct = 0
    for value, target in zip(cases, expected):
        if transform(value) == target:
            correct += 1
    score = correct / len(cases)
    return {"score": score, "is_valid": True}
