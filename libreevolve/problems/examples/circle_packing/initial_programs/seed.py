def solve():
    r = 0.08
    rows = [5, 6, 5, 6, 4]
    spacing = 1e-6
    row_gap = 2.0 * r + spacing
    step = 2.0 * r + spacing
    y = r + (1.0 - (2.0 * r + row_gap * (len(rows) - 1))) / 2.0
    circles = []
    for count in rows:
        x = r + (1.0 - (2.0 * r + step * (count - 1))) / 2.0
        for i in range(count):
            circles.append((x + i * step, y, r))
        y += row_gap
    return circles
