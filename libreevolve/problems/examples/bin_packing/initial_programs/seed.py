def pack(items: list[int], capacity: int) -> list[list[int]]:
    """Valid next-fit baseline: only consider the most recently opened bin."""
    bins = []
    load = 0
    for item in items:
        if not bins or load + item > capacity:
            bins.append([])
            load = 0
        bins[-1].append(item)
        load += item
    return bins
