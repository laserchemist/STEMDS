import numpy as np
from datascience import *
import matplotlib.pyplot as plt
plt.style.use('ggplot')
from bestfit import *

def standard_units(any_numbers):
    "Convert any array of numbers to standard units."
    return (any_numbers - np.mean(any_numbers))/np.std(any_numbers)  
def correlation(x, y):
    return np.mean(standard_units(x)*standard_units(y))

def slope(x, y):
    r = correlation(x, y)
    return r*np.std(y)/np.std(x)

def intercept(x, y):
    return np.mean(y) - slope(x, y)*np.mean(x)

def originalGrapher(slope, intercept, table, xlabel, ylabel, preset='Linear'):
    lowLimit = min(table.column(xlabel))
    highLimit = max(table.column(xlabel))
    increment = (highLimit-lowLimit)/30
    xvals = np.arange(lowLimit, highLimit, increment)

    if preset == 'Linear':
        plt.scatter(xvals, xvals*slope+intercept, color='red', label='fit')
    elif preset == 'Power':
        plt.scatter(xvals, slope * xvals**2 + intercept, color='red', label='fit')
    elif preset == 'Inverse':
        plt.scatter(xvals, slope / xvals + intercept, color='red', label='fit')
    elif preset == 'Root':
        plt.scatter(xvals, slope * xvals**0.5 + intercept, color='red', label='fit')
    else:
        return 'Not an accepted preset! Check for typos.'
    
    plt.plot(table[xlabel], table[ylabel], color='blue', label='actual data')

    plt.xlabel(xlabel)
    plt.ylabel(ylabel)

    plt.title(ylabel + ' as a function of ' + xlabel + ' with a best fit line.') 

    plt.legend()
    plt.show()
    
        