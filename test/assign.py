def main(x, y):
    if x > y:
        z = 1
    else:
        z = -1
    
    a = f(x, y)
    return a

def f(v, w):
    if v > w:
        return True
    else:
        return False

def expected_result():
    return [0, 1]