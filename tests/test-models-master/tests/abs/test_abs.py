
from __future__ import division
import numpy as np
from pysd import functions

def time():
    return _t

def flowa():
    """
    
    """

    output = 1
	

    return output

def stocka():
    return _state['stocka']

def _stocka_init():
    return -10

def _dstocka_dt():
    return flowa()

def test_abs():
    """
    
    """

    output = abs(stocka())
	

    return output

def final_time():
    """
    
    """

    output = 20
	

    return output

def initial_time():
    """
    
    """

    output = 0
	

    return output

def saveper():
    """
    
    """

    output = time_step()

    return output

def time_step():
    """
    
    """

    output = 1
	

    return output
