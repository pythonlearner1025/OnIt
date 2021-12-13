import numpy as np
import math, time, os 
import sklearn as sk
from sklearn.linear_model import Ridge
from sklearn.linear_model import LinearRegression

# output a matrix that predicts eye-position
# value given an intercept, coefficient, and
# feature x values 
def predictWithCoef(x, intercept, coef):
    # for now:
    intercept = np.array(intercept, dtype='float16')
    coef = np.array(coef, dtype='float16')
    x = np.array(x, dtype='float16')
    # 1x2 + (1x2485) * (2485*2)
    #prediction = intercept + (x @ coef.T)
    b = x @ coef.T
    prediction = intercept + b 
    return prediction 




# pass a Ridge object as arg regression,
# and perform linear fitting using y as 
# the target output that coefficients should be
# minimizing. Return the coefficient and intercept. 
def getParams(x,y): 
    # x dims = (1,2485) 
    # y dims = (1,2)
    regression = Ridge(alpha=0.09)
    regression.fit(x,y)
    # coef dims = (2,2485)
    # intercept dims = (1,2)
    return regression.coef_, regression.intercept_

def transform(L):
    if not isinstance(L[0], list):
        transformed = []
        for e in L:
            transformed.append([e])
        return transformed
    else:
        rows, cols = len(L), len(L[0])
        newrows, newCols = cols, rows
        
        transformed = [[0 for _ in range(newCols)] for _ in range(newRows)]
        for col in range(cols):
            for row in range(rows):
                transformed[col][row] = L[col][row]
        return transformed

def smallDot(A,B):
    dotProduct = 0
    for i in range(len(A)):
        dotProduct += (A[i] * B[i][0])
    return dotProduct


def dot(A,B):
    BT = transform(B)
    dotted = []
    for i in range(len(A)):
        dotted.append([smallDot(A[i], BT)])
    return dotted
    

# add ones to 2D list
def standardize(L):
    standardized = [1] + L
    return standardized 


