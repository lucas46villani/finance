#%% Stock's Download
import pandas as pd 
import yfinance as yf            


#%%Bajo COTIZACION DE ACCIONES de Yahoo Finance

def data(tickets, start=None):
    '''Dowload price and volume stocks from yahoofinance.
    Parameters:
    tickets: Ticket names as string
    start: The first day we want to have information.  
    '''  
    mktl=yf.download(tickets, start=start)
    return mktl      




