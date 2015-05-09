def main(x):
    if x > 0:
        z = 10
    else:
        z = -10
    
    if x > z:
        return 0
    else:
        return 1
    
def expected_result():
    return [0, 1]