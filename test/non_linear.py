def ab(v):
    (a,b) = (True, False)
    if v >= 0:
        return True
    else:
        return False

def summa(v, w):
    return v + w

def main(x, y):
    z = ab(x) and ab(x)
    return z

def expected_result():
    return [False, -1, 2*4]