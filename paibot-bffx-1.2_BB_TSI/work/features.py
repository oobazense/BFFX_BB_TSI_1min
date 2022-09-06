import talib
import numpy as np


features = sorted([
    'ADX',
    'ADXR',
#    'APO',
    'AROON_aroondown',
    'AROON_aroonup',
    'AROONOSC',
    'CCI',
    'DX',
    'MACD_macd',
    'MACD_macdsignal',
    'MACD_macdhist',
    'MFI',
#     'MINUS_DI',
#     'MINUS_DM',
#    'MOM',
#     'PLUS_DI',
#     'PLUS_DM',
    'RSI',
    'STOCH_slowk',
    'STOCH_slowd',
    'STOCHF_fastk',
#     'STOCHRSI_fastd',
    'ULTOSC',
#    'WILLR',
#     'ADOSC',
#     'NATR',
    'HT_DCPERIOD',
    'HT_DCPHASE',
#    'HT_PHASOR_inphase',
#    'HT_PHASOR_quadrature',
    'HT_TRENDMODE',
    'BETA',
    'LINEARREG',
#    'LINEARREG_ANGLE',
#    'LINEARREG_INTERCEPT',
#    'LINEARREG_SLOPE',
#    'STDDEV',
#    'BBANDS_upperband',
    'BBANDS_middleband',
#    'BBANDS_lowerband',
    'DEMA',
    'EMA',
    'HT_TRENDLINE',
    'KAMA',
    'MA',
#    'MIDPOINT',
    'T3',
    'TEMA',
    'TRIMA',
    'WMA',
    'cl_diff48',
    'minute',
    'hour',
#    'day',
    "vol_roc",
    "SMA_14_5",
    "ROC_2",
    "ROC_5",
    "ROC_10",
#    "vol_STD10",
#    "vol_STD50",
#    "vol_STD10_50",
#    "volume_log",
#    "volume_log_diff_5",
#    "volume_log_diff_10",
#    "cl_log",
    "cl_log_diff",
#    "cl_log_diff_STD5",
#    "cl_log_diff_STD10"
    "ATR5_hilo",
    "ATR5_clop",
    "ATR14_hilo",
    "ATR14_clop",
    "STDEV5_hilo",
    "STDEV5_clop",
    "STDEV14_hilo",
    "STDEV14_clop",
    'TSI'
])




def calc_features(df):
    open = df['op']
    high = df['hi']
    low = df['lo']
    close = df['cl']
    volume = df['volume']
    
    orig_columns = df.columns

    hilo = (df['hi'] + df['lo']) / 2
    df['BBANDS_upperband'], df['BBANDS_middleband'], df['BBANDS_lowerband'] = talib.BBANDS(close, timeperiod=20, nbdevup=2, nbdevdn=2, matype=0)
    #df['BBANDS_upperband'] -= hilo
    #df['BBANDS_upperband'] = df['BBANDS_upperband']/df['cl']
    #df['BBANDS_middleband'] -= hilo
    #df['BBANDS_middleband'] = df['BBANDS_middleband']/df['cl']
    #df['BBANDS_lowerband'] -= hilo
    #df['BBANDS_lowerband'] =  df['BBANDS_lowerband']/df['cl']
    df['DEMA'] = (talib.DEMA(close, timeperiod=30) - hilo)/df['cl']
    df['EMA'] = (talib.EMA(close, timeperiod=30) - hilo)/df['cl']
    df['EMA25'] = (talib.EMA(close, timeperiod=25))
    df['EMA13'] = (talib.EMA(close, timeperiod=13))
    df['HT_TRENDLINE'] = (talib.HT_TRENDLINE(close) - hilo)/df['cl']
    df['KAMA'] = (talib.KAMA(close, timeperiod=30) - hilo)/df['cl']
    df['MA'] = (talib.MA(close, timeperiod=30, matype=0) - hilo)/df['cl']
    #df['MIDPOINT'] = talib.MIDPOINT(close, timeperiod=14) - hilo
    df['SMA'] = talib.SMA(close, timeperiod=30) - hilo
    df['T3'] = (talib.T3(close, timeperiod=5, vfactor=0) - hilo)/df['cl']
    df['TEMA'] = (talib.TEMA(close, timeperiod=30) - hilo)/df['cl']
    df['TRIMA'] = (talib.TRIMA(close, timeperiod=30) - hilo)/df['cl']
    df['WMA'] = (talib.WMA(close, timeperiod=30) - hilo)/df['cl']

    df['ADX'] = talib.ADX(high, low, close, timeperiod=14)
    df['ADXR'] = talib.ADXR(high, low, close, timeperiod=14)
    df['APO'] = talib.APO(close, fastperiod=12, slowperiod=26, matype=0)
    df['AROON_aroondown'], df['AROON_aroonup'] = talib.AROON(high, low, timeperiod=14)
    df['AROONOSC'] = talib.AROONOSC(high, low, timeperiod=14)
    df['BOP'] = talib.BOP(open, high, low, close)
    df['CCI'] = talib.CCI(high, low, close, timeperiod=14)
    df['DX'] = talib.DX(high, low, close, timeperiod=14)
    df['MACD_macd'], df['MACD_macdsignal'], df['MACD_macdhist'] = talib.MACD(close, fastperiod=12, slowperiod=26, signalperiod=9)
    df['MACD_macd'] = df['MACD_macd'] /df['cl']
    df['MACD_macdsignal'] = df['MACD_macdsignal'] /df['cl']
    df['MACD_macdhist'] = df['MACD_macdhist']/df['cl']
    # skip MACDEXT MACDFIX たぶん同じなので
    df['MFI'] = talib.MFI(high, low, close, volume, timeperiod=14)
    df['MINUS_DI'] = talib.MINUS_DI(high, low, close, timeperiod=14)
    df['MINUS_DM'] = talib.MINUS_DM(high, low, timeperiod=14)
    df['MOM'] = talib.MOM(close, timeperiod=10)
    df['PLUS_DI'] = talib.PLUS_DI(high, low, close, timeperiod=14)
    df['PLUS_DM'] = talib.PLUS_DM(high, low, timeperiod=14)
    df['RSI'] = talib.RSI(close, timeperiod=14)
    df['STOCH_slowk'], df['STOCH_slowd'] = talib.STOCH(high, low, close, fastk_period=5, slowk_period=3, slowk_matype=0, slowd_period=3, slowd_matype=0)
    df['STOCHF_fastk'], df['STOCHF_fastd'] = talib.STOCHF(high, low, close, fastk_period=5, fastd_period=3, fastd_matype=0)
    df['STOCHRSI_fastk'], df['STOCHRSI_fastd'] = talib.STOCHRSI(close, timeperiod=14, fastk_period=5, fastd_period=3, fastd_matype=0)
    df['TRIX'] = talib.TRIX(close, timeperiod=30)
    df['ULTOSC'] = talib.ULTOSC(high, low, close, timeperiod1=7, timeperiod2=14, timeperiod3=28)
    df['WILLR'] = talib.WILLR(high, low, close, timeperiod=14)

    df['AD'] = talib.AD(high, low, close, volume)
    df['ADOSC'] = talib.ADOSC(high, low, close, volume, fastperiod=3, slowperiod=10)
    df['OBV'] = talib.OBV(close, volume)

    df['ATR'] = talib.ATR(high, low, close, timeperiod=14)
    df['NATR'] = talib.NATR(high, low, close, timeperiod=14)
    df['TRANGE'] = talib.TRANGE(high, low, close)

    df['HT_DCPERIOD'] = talib.HT_DCPERIOD(close)
    df['HT_DCPHASE'] = talib.HT_DCPHASE(close)
    #df['HT_PHASOR_inphase'], df['HT_PHASOR_quadrature'] = talib.HT_PHASOR(close)
    #df['HT_PHASOR_inphase'] = df['HT_PHASOR_inphase']/df['cl']
    df['HT_SINE_sine'], df['HT_SINE_leadsine'] = talib.HT_SINE(close)
    df['HT_TRENDMODE'] = talib.HT_TRENDMODE(close)

    df['BETA'] = talib.BETA(high, low, timeperiod=5)
    df['CORREL'] = talib.CORREL(high, low, timeperiod=30)
    df['LINEARREG'] = (talib.LINEARREG(close, timeperiod=14) - close)/df['cl']
    df['LINEARREG_ANGLE'] = talib.LINEARREG_ANGLE(close, timeperiod=14)
    df['LINEARREG_INTERCEPT'] = talib.LINEARREG_INTERCEPT(close, timeperiod=14) - close
    df['LINEARREG_SLOPE'] = talib.LINEARREG_SLOPE(close, timeperiod=14)
    df['STDDEV'] = talib.STDDEV(close, timeperiod=5, nbdev=1)/df['cl']
    df['cl_diff48'] = df['cl'].diff(48) / df['cl']
    df['minute'] = df.index.minute
    df['hour'] = df.index.hour
    df['day'] = df.index.day
    df["ROC_5"] = talib.ROC(df['cl'], timeperiod=5)
    df["vol_stdev_10"] = talib.STDDEV(df["volume"], timeperiod=10)
    df["vol_stdev_50"] = talib.STDDEV(df["volume"], timeperiod=50)
    df["vol_stdev_10_50"] = df["vol_stdev_10"] / df["vol_stdev_50"] - 1
    df["vol_roc"] = df["ROC_5"] * df["vol_stdev_10_50"]
    df["SMA_5"] = talib.SMA(close, timeperiod=5) #Simple Moving Average
    df["SMA_14"] = talib.SMA(close, timeperiod=14)
    df["SMA_14_5"] = (df["SMA_14"] - df["SMA_5"]) / df["SMA_5"]
    
    # 価格の変化率
    df["ROC_2"] = talib.ROC(close, timeperiod=2)
    df["ROC_5"] = talib.ROC(close, timeperiod=5)
    df["ROC_10"] = talib.ROC(close, timeperiod=10)
    
    df['ATR5'] = talib.ATR(high, low, close, timeperiod=5)
    df['ATR14'] = talib.ATR(high, low, close, timeperiod=14)
    
    df["ATR5_hilo"] = df['ATR5'] / (df["hi"] - df["lo"])
    df["ATR5_clop"] = df['ATR5'] / (df["cl"] - df["op"])
    df["ATR14_hilo"] = df['ATR14'] / (df["hi"] - df["lo"])
    df["ATR14_clop"] = df['ATR14'] / (df["cl"] - df["op"])
    
    df['STDDEV5'] = talib.STDDEV(close, timeperiod=5, nbdev=1)
    df['STDDEV14'] = talib.STDDEV(close, timeperiod=14, nbdev=1)
    df["STDEV5_hilo"] = df['STDDEV5'] / (df["hi"] - df["lo"])
    df["STDEV5_clop"] = df['STDDEV5'] / (df["cl"] - df["op"])
    df["STDEV14_hilo"] = df['STDDEV14'] / (df["hi"] - df["lo"])
    df["STDEV14_clop"] = df['STDDEV14'] / (df["cl"] - df["op"])
    
    
    df["cl_log"] = np.log(df["cl"])
    df["cl_log_diff"] = df["cl_log"].diff()
    df["cl_log_diff_STD5"] = talib.STDDEV(df["cl_log_diff"], timeperiod=5) / df['cl']
    df["cl_log_diff_STD10"] = talib.STDDEV(df["cl_log_diff"], timeperiod=10) / df['cl']
    
    
    return df
