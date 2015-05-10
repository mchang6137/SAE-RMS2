def main (x, y):
    if x > 0:
        if y > 0:
            return 5 % 2
        else:
            return 5 ** 2
    else:
        if y > 0:
            return 4 >> 2
        else:
            return 4 << 2

def expected_result():
    return [1,25,1,16]