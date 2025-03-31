import pandas as pd

sp500 = 'data/^spx_d.csv'
intel = 'data/intc_us_d.csv'
nvidia = 'data/nvda_us_d.csv'
def get_SP500():
    df = pd.read_csv(sp500)
    return df
def get_INTC():
    df = pd.read_csv(intel)
    return df

def get_NVDA():
    df = pd.read_csv(nvidia)
    return df