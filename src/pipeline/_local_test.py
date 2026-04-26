2026-04-24 14:51:18,008 - DEBUG - lgbm_classification.py - feature_importance - Feature importances: [ 3  4  6  8  2  1  6  8 16  2 10  0  0  5  1  0  8  9  2 10  3  3  0  0
  0  0  4  4  1  1  8  5  0  0  0  2  3  1  5  5  0  1  4  6  0  0  0  0
  5 14  1  8  5  5  2  0  0  2  0  6  4  1  0 12  5  1  7  0  0  0  3  1
  1  4  7  2  2 14]
2026-04-24 14:51:18,011 - INFO - lgbm_classification.py - feature_importance - Top 150 feature importances:
                     feature  importance
8                    USD_JPY          16
77      GOLD_trend_regime_30          14
49           BRENT_return_30          14
63                DXY_vol_20          12
19           CBOE_VIX_vol_20          10
10                   USD_CAD          10
17     CBOE_VIX_mean_revr_10           9
30                SPY_vol_20           8
51              BRENT_vol_10           8
16        CBOE_VIX_return_30           8
3                      BRENT           8
7                    USD_CHF           8
66       DXY_trend_regime_30           7
74               GOLD_vol_20           7
2                        WTI           6
6                    GBP_USD           6
43       WTI_trend_regime_20           6
59             DXY_return_20           6
52              BRENT_vol_20           5
38             WTI_return_30           5
31                SPY_vol_30           5
13         CBOE_VIX_return_5           5
48           BRENT_return_20           5
64                DXY_vol_30           5
53              BRENT_vol_30           5
39          WTI_mean_revr_10           5
73               GOLD_vol_10           4
27             SPY_return_30           4
1                        SPY           4
26             SPY_return_20           4
42                WTI_vol_30           4
60             DXY_return_30           4
21  CBOE_VIX_trend_regime_20           3
20           CBOE_VIX_vol_30           3
70            GOLD_return_20           3
0                        DXY           3
36             WTI_return_10           3
4                    Bitcoin           2
76      GOLD_trend_regime_20           2
75               GOLD_vol_30           2
35              WTI_return_5           2
9                    USD_SEK           2
54     BRENT_trend_regime_20           2
57              DXY_return_5           2
18           CBOE_VIX_vol_10           2
5                    EUR_USD           1
29                SPY_vol_10           1
14        CBOE_VIX_return_10           1
72         GOLD_mean_revr_10           1
65       DXY_trend_regime_20           1
61          DXY_mean_revr_10           1
50        BRENT_mean_revr_10           1
71            GOLD_return_30           1
41                WTI_vol_20           1
37             WTI_return_20           1
28          SPY_mean_revr_10           1
12           CBOE_VIX_return           0
11                  CBOE_VIX           0
25             SPY_return_10           0
24              SPY_return_5           0
15        CBOE_VIX_return_20           0
22  CBOE_VIX_trend_regime_30           0
45              BRENT_return           0
44       WTI_trend_regime_30           0
40                WTI_vol_10           0
34                WTI_return           0
33       SPY_trend_regime_30           0
32       SPY_trend_regime_20           0
23                SPY_return           0
46            BRENT_return_5           0
58             DXY_return_10           0
56                DXY_return           0
55     BRENT_trend_regime_30           0
47           BRENT_return_10           0
69            GOLD_return_10           0
68             GOLD_return_5           0
67               GOLD_return           0
62                DXY_vol_10           0
2026-04-24 14:51:18,011 - INFO - lgbm_classification.py - feature_importance - Cumulative sum of importances:
8      16
77     30
49     44
63     56
19     66
10     76
17     85
30     93
51    101
16    109
3     117
7     125
66    132
74    139
2     145
6     151
43    157
59    163
52    168
38    173
31    178
13    183
48    188
64    193
53    198
39    203
73    207
27    211
1     215
26    219
42    223
60    227
21    230
20    233
70    236
0     239
36    242
4     244
76    246
75    248
35    250
9     252
54    254
57    256
18    258
5     259
29    260
14    261
72    262
65    263
61    264
50    265
71    266
41    267
37    268
28    269
12    269
11    269
25    269
24    269
15    269
22    269
45    269
44    269
40    269
34    269
33    269
32    269
23    269
46    269
58    269
56    269
55    269
47    269
69    269
68    269
67    269
62    269


2026-04-24 14:51:18,146 - INFO - lgbm_classification.py - evaluating_backtest_strategy - Information below are for the strategy from model : LGBMClassifier 
2026-04-24 14:51:18,147 - DEBUG - financial_metrics.py - calculate_cagr - CAGR (compoound annual growth range) : 33.087%
2026-04-24 14:51:18,147 - DEBUG - financial_metrics.py - drawdown_from_peak - Drawdown is : -19.003% 
2026-04-24 14:51:18,147 - DEBUG - financial_metrics.py - return_std - Stand deviation is 0.942%
2026-04-24 14:51:18,147 - DEBUG - financial_metrics.py - return_std - Vol_annual is 14.960%
2026-04-24 14:51:18,148 - DEBUG - financial_metrics.py - dates_numbers - Number of na's: 2304
2026-04-24 14:51:18,148 - DEBUG - financial_metrics.py - dates_numbers - First date of the reviewed dataframe: 2014-09-18 00:00:00
2026-04-24 14:51:18,148 - DEBUG - financial_metrics.py - dates_numbers - Last date of the reviewed dataframe: 2026-04-02 00:00:00
2026-04-24 14:51:18,148 - DEBUG - financial_metrics.py - dates_numbers - First date to be considered as no trade or trade: 2023-12-22 00:00:00
2026-04-24 14:51:18,149 - DEBUG - financial_metrics.py - dates_numbers - Last date to be considered as no trade or trade: 2026-04-02 00:00:00
2026-04-24 14:51:18,150 - DEBUG - financial_metrics.py - dates_numbers - Number of trades executed : 167. Number of trades not exeucted: 399 (being below the threshold)
2026-04-24 14:51:18,151 - INFO - lgbm_classification.py - evaluating_backtest_strategy - PnL Long: 0.020506095954326172
2026-04-24 14:51:18,151 - INFO - lgbm_classification.py - evaluating_backtest_strategy - Average Trade Return: 0.0011932118551820454
2026-04-24 14:51:18,151 - INFO - lgbm_classification.py - evaluating_backtest_strategy - Information below are for  BUY and HOLD approach
2026-04-24 14:51:18,151 - DEBUG - financial_metrics.py - buy_and_hold_strateg - BUY and HOLD returns is  : 265.331%; basically your return starting from trade date at trade price till today(latest available data)
2026-04-24 14:51:18,152 - DEBUG - financial_metrics.py - calculate_cagr - CAGR (compoound annual growth range) : 11.873%
2026-04-24 14:51:18,152 - DEBUG - financial_metrics.py - drawdown_from_peak - Drawdown is : -22.002% 
2026-04-24 14:51:18,153 - DEBUG - financial_metrics.py - return_std - Stand deviation is 1.008%
2026-04-24 14:51:18,153 - DEBUG - financial_metrics.py - return_std - Vol_annual is 16.006%