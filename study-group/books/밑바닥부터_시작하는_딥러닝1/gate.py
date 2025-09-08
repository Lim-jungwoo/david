import numpy as np

def AND(x1, x2, w1=1, w2=1, b=-1) -> int:
    x = np.array([x1, x2])
    w = np.array([w1, w2])
    result = np.sum(x*w) + b
    if result <= 0: return 0
    else: return 1
    

def OR(x1, x2, w1=1, w2=1, b=-0.5) -> int:
    x = np.array([x1, x2])
    w = np.array([w1, w2])
    result = np.sum(x*w) + b
    if result <= 0: return 0
    else: return 1


def NAND(x1, x2, w1=-0.5, w2=-0.5, b=1) -> int:
    x = np.array([x1, x2])
    w = np.array([w1, w2])
    result = np.sum(x*w) + b
    if result <= 0: return 0
    else: return 1


def XOR(x1, x2) -> int:
    s1 = OR(x1, x2)
    s2 = NAND(x1, x2)
    return AND(s1, s2)

if __name__ == '__main__':
    x1 = 0; x2 = 0
    print(AND(x1,x2), OR(x1,x2), NAND(x1,x2), XOR(x1,x2))
    x1 = 1; x2 = 0
    print(AND(x1,x2), OR(x1,x2), NAND(x1,x2), XOR(x1,x2))
    x1 = 0; x2 = 1
    print(AND(x1,x2), OR(x1,x2), NAND(x1,x2), XOR(x1,x2))
    x1 = 1; x2 = 1
    print(AND(x1,x2), OR(x1,x2), NAND(x1,x2), XOR(x1,x2))