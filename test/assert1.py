def main (x):
    assert( abs(x) >= 0 and abs(x) == abs(-x) )
    return 0

def abs(v):
    if v >= 0:
        return v
    else:
        return -1 * v

def expected_result():
    return [0]