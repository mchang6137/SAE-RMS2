def main (x, y):
    if x == 2:
        if y != 3:
            return 0
        else:
            return 1
    else:
        return 2

def expected_result():
    return [0,1,2]