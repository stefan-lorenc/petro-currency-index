import pandas as pd
import sys
import warnings
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor
import numpy as np
from matplotlib import pyplot as plt
from scipy.optimize import minimize

#volume profile, footprint, eia**, iea

# USD / RUB ##  Not available
# USD / NOK **
# USD / CAD **
# USD / MXN **
# USD / CLP ## Not available
# USD / BRL ## Not available

def pcx_dev(vals):

    cad_w = vals[0]
    rub_w = vals[1]
    nok_w = vals[2]

    day = vals[3]

    day['pci'] = cad_w * day['Close_Cad'] + rub_w * day['Close_Mxn'] + nok_w * day['Close_Nok']

    return [day['Close'].corr(day['pci']), rub_w, cad_w, nok_w]


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
    # cur_oil = cur_oil.pct_change()
    cur_oil = (cur_oil - cur_oil.mean()) / cur_oil.std()
    # cur_oil = (cur_oil - cur_oil.min())/(cur_oil.max() - cur_oil.min())
    cur_oil.index = pd.to_datetime(cur_oil.index)

    cur_oil = cur_oil[cur_oil.index.dayofweek < 5]
    cur_oil = cur_oil[cur_oil.index.hour >= 6]
    cur_oil = cur_oil[cur_oil.index.hour < 16]

    cur_oil_grouped = cur_oil.groupby(pd.Grouper(freq='D'))

    cleaned = [group for _, group in cur_oil_grouped if not group.empty]

    cleaned = cleaned[2:3]

    values = []

    shi = 2

    for elem in tqdm(cleaned):
        cur_oil = elem
        morn = cur_oil[cur_oil.index.hour < 8]
        # morn = morn[morn.index.hour < 11]
        aft = cur_oil[cur_oil.index.hour >= 8]
        aft = aft[aft.index.hour < 10]
        # opening range strategy paired with the currency index. should oil move outisde the range, take position
        # in the index. but why not oil itself

        if morn.empty or aft.empty:
            continue

        else:

            # morn[['Close_Mxn', 'Close_Cad', 'Close_Nok']] = morn[['Close_Mxn', 'Close_Cad', 'Close_Nok']].shift(shi)
            # morn['Close'] = morn['Close'].shift(shi)

            check = [[x, y, z, a] for x, y, z, a in
                     zip(np.random.default_rng().uniform(-1, 1, 20000), np.random.default_rng().uniform(-1, 1, 20000),
                         np.random.default_rng().uniform(-1, 1, 20000), [morn] * 20000)]

            with ThreadPoolExecutor(max_workers=200) as executor:
                trial = list(executor.map(pcx_dev, check))
                correlations = [info[0] for info in trial]
                mxn = [info[1] for info in trial]
                cad = [info[2] for info in trial]
                nok = [info[3] for info in trial]
                ind = correlations.index(max(correlations))

                executor.shutdown(wait=True)

            print(mxn[ind], cad[ind], nok[ind], correlations[ind])

            aft['pci'] = cad[ind] * aft['Close_Cad'] + mxn[ind] * aft['Close_Mxn'] + nok[ind] * aft['Close_Nok']
            aft['pci_oil_corr'] = aft['pci'].rolling(3).corr(aft['Close'])

            aft[['pci', 'Close']].plot.line()

            plt.show()

            aft['pci_oil_corr'].plot.line()

            plt.show()

            values.append(aft)

    pcx_comp = pd.concat(values)

    print(pcx_comp)


    # pcx_comp.to_csv('pcx_comp.csv', index=True)

    # pcx_comp[['pci', 'Close']].plot.line()
    #
    # plt.show()


