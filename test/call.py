def main (x):
    if abs(x) >= 0:
        return 0
    else:
        return 1

def abs(v):
    if v >= 0:
        return v
    else:
        return -1 * v

def expected_result():
    return [0]