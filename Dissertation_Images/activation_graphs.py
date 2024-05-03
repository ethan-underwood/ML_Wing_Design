from matplotlib import pyplot as plt
import numpy as np
from matplotlib import rcParams

def plot_activation_function(
        x:list, 
        g1:list, 
        g2:list, 
        g3:list, 
        activationFunctions:list, 
        #activationEquations:list
        ):
    rcParams['text.usetex'] = True
    rcParams['text.latex.preamble'] = r'\usepackage{amsthm}'
    plt.figure(figsize=(18, 5))
    plt.tight_layout()
    plt.subplot(1, 3, 1)
    plt.plot(x, g1, label=r'$f(x)=\frac{1}{1+e^{-x}}$')
    plt.title(f"{activationFunctions[0]} Activation Function")
    plt.legend(loc='upper left')
    plt.subplot(1, 3, 2)
    plt.plot(x, g2, label=r'$f(x)=\frac{e^{x}-e^{-x}}{e^{x}+e^{-x}}$')
    plt.title(f"{activationFunctions[1]} Activation Function")
    plt.legend(loc='upper left')
    plt.subplot(1, 3, 3)
    plt.plot(x, g3, label= r'$f(x)=\left\{\begin{array}{lr} x : x\geq 0\\ 0 : x<0\end{array}\right\}$')
    plt.title(f"{activationFunctions[2]} Activation Function")
    plt.legend(loc='upper left')

    plt.savefig("Activation_Functions")
    plt.close()


x = np.linspace(-10, 10, 200)
g1 = 1/(1+np.e**-x)
g2 = (np.e**x-np.e**-x)/(np.e**x+np.e**-x)
g3 = []
for i in x:
    if i < 0:
        g3.append(0)
    else:
        g3.append(i)
plot_activation_function(x, g1, g2, g3, ["Sigmoid", "Hyperbolic Tangent", "Rectified Linear Unit"])