def main (x , y):
    if ( x < -10 ):
        return y
    elif ( x < 10  ):
        return neg(x) or pos(y)
    else :
        return 2*y

def neg(v):
    if v < 0:
        return True
    else:
        return False

def pos(v):
    if v > 0:
        return True
    else:
        return False

def expected_result():
    return [ -1 ,0 ,1]