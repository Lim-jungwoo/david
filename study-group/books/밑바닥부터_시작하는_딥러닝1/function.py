import numpy as np
import matplotlib.pylab as plt

def step_function(x):
    return np.array(x > 0, dtype=int)


def sigmoid_function(x):
    return 1 / (1 + np.exp(-x))


def relu(x):
    return np.maximum(0, x)


def identity_function(x):
    return x


def softmax_function(x):
    c = np.max(x)
    exp_x = np.exp(x - c)   # 오버플로 대책
    sum_exp_x = np.sum(exp_x)
    y = exp_x / sum_exp_x
    
    return y

if __name__ == '__main__':
    x = np.arange(-5.0, 5.0, 0.1)
    step_y = step_function(x)
    sigmoid_y = sigmoid_function(x)
    relu_y = relu(x)
    softmax_y = softmax_function(x)
    plt.plot(x, step_y)
    plt.plot(x, sigmoid_y)
    plt.plot(x, relu_y)
    plt.plot(x, softmax_y)
    plt.ylim(-0.1, 1.1)
    plt.show()