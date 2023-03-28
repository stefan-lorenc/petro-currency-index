import pandas as pd
import matplotlib.pyplot as plt
pd.set_option("expand_frame_repr", False)


record_2021 = pd.read_csv(r"C:\Users\stefa\Downloads\USDMXN\USDMXN_2021_all.csv", header=None,
                          names=["date", 'time', 'Open_Mxn', 'High_Mxn', 'Low_Mxn', 'Close_Mxn', 'Vol_Mxn'])

record_2020 = pd.read_csv(r"C:\Users\stefa\Downloads\USDMXN\USDMXN_2020_all.csv", header=None,
                          names=["date", 'time', 'Open_Mxn', 'High_Mxn', 'Low_Mxn', 'Close_Mxn', 'Vol_Mxn'])

record_2019 = pd.read_csv(r"C:\Users\stefa\Downloads\USDMXN\USDMXN_2019_all.csv", header=None,
                          names=["date", 'time', 'Open_Mxn', 'High_Mxn', 'Low_Mxn', 'Close_Mxn', 'Vol_Mxn'])

record_2018 = pd.read_csv(r"C:\Users\stefa\Downloads\USDMXN\USDMXN_2018_all.csv", header=None,
                          names=["date", 'time', 'Open_Mxn', 'High_Mxn', 'Low_Mxn', 'Close_Mxn', 'Vol_Mxn'])

record_2017 = pd.read_csv(r"C:\Users\stefa\Downloads\USDMXN\USDMXN_2017_all.csv", header=None,
                          names=["date", 'time', 'Open_Mxn', 'High_Mxn', 'Low_Mxn', 'Close_Mxn', 'Vol_Mxn'])

compiled = record_2017.append(record_2018).append(record_2019).append(record_2020).append(record_2021)


compiled['Date Time'] = compiled['date'] + compiled['time']

compiled['Date Time'] = pd.to_datetime(compiled['Date Time'], format='%Y.%m.%d%H:%M')

compiled = compiled.set_index(compiled['Date Time'])
compiled = compiled.drop(['date', 'time'], axis=1)
compiled = compiled.dropna()


print(compiled.head())
print(compiled.tail())
print(compiled.info())

compiled['Open_Mxn'].plot.line()

plt.show()

compiled.to_csv('data/USD_MXNcomp.csv', index=False)

