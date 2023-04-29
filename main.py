import pandas as pd
import warnings
import numpy as np
from scipy.optimize import minimize
from matplotlib import pyplot as plt
from tqdm import tqdm

 def pcx_dev(x, df):
        return -1 * df['Close'].shift(periods=12).corr(
            df['Close_Mxn'] * x[0] + df['Close_Cad'] * x[1] + df['Close_Nok'] * x[2])


def constraint_1(x):
    return x[0] + x[1] + x[2] - 1


if __name__ == '__main__':
    pd.set_option('mode.chained_assignment', None)
    pd.set_option("expand_frame_repr", False)
    warnings.filterwarnings("ignore")

    usd_cad = pd.read_csv('data/USD_CADcomp.csv', index_col='Date Time')
    usd_rub = pd.read_csv('data/USD_MXNcomp.csv', index_col='Date Time')
    usd_nok = pd.read_csv('data/USD_NOKcomp.csv', index_col='Date Time')
    usd_wti = pd.read_csv('data/WTIcomp.csv', index_col='Date Time')

    cur_oil = usd_cad.merge(usd_rub, left_index=True, right_index=True).merge(usd_nok, left_index=True,
                                                                              right_index=True).merge(usd_wti,
                                                                                                      left_index=True,
                                                                                                      right_index=True)
    cur_oil = cur_oil.iloc[::3, :]  # every nth entry

    cur_oil = cur_oil[['Close_Mxn', 'Close_Cad', 'Close_Nok', 'Close']]
    cur_oil.index = pd.to_datetime(cur_oil.index)

    cur_oil = cur_oil[cur_oil.index.dayofweek < 5]
    cur_oil = cur_oil[cur_oil.index.hour >= 9]
    cur_oil = cur_oil[cur_oil.index.hour < 16]
    oil_grouped = cur_oil.groupby(pd.Grouper(freq='D'))

    print('collected')

    # oil = [group for _, group in oil_grouped if not group.empty and len(group) >= 380]

    oil = [group for _, group in oil_grouped if not group.empty]


    b = (-1, 1)
    bnds = (b, b, b)

    con1 = {'type': 'eq', 'fun': constraint_1}

    mxn_lead, cad_lead, nok_lead, pcx_lead = [], [], [], []


    demo = oil[3]

    demo = (demo - demo.mean()) / demo.std()

    train_test_split = int(len(demo) * 0.7)

    oil_cal = demo.iloc[:train_test_split, :]
    oil_act = demo.iloc[train_test_split:, :]

    sol = minimize(pcx_dev, np.array([0.33, 0.33, 0.33]), args=(oil_cal,), bounds=bnds)

    temp = oil_act

    print(sol)

    temp['pcx'] = temp['Close_Mxn'] * sol.x[0] + temp['Close_Cad'] * sol.x[1] + temp['Close_Nok'] * sol.x[2]

    print(temp.head())

    lines = temp.plot.line()

    plt.show()


