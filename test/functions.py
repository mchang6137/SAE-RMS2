def main(x, y):
    return f(g(x), h(y))

def g(x):
    if x >= 0:
        return x + x
    else:
        return -x

def h(x):
    if x >= 0:
        return x + x
    else:
        return x


def f(v, w):
    return v + w