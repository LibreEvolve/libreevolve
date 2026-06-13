# EVOLVE-BLOCK-START network
def network():
    comparators = []
    for end in range(7, 0, -1):
        for i in range(end):
            comparators.append((i, i + 1))
    return comparators
# EVOLVE-BLOCK-END
