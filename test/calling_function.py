def main(x, y):
    if (  2*x == s(x, y) ):
        return 1
    else :
        return -1

def s(v, w):
    if ( v < w ):
        return w
    else:
        return v

def expected_result():
    return [-1, 1]