# rental_property_deal_analysis

A script to analyze good/bad rental property investment deal.

Credits to: https://www.biggerpockets.com/renewsblog/2010/06/30/introduction-to-real-estate-analysis-investing/

## Example Usage
```
# modify input data/example.yml

# output to console
$ ./deal_analysis.py data/example.yml
...
== SUMMARY ==
PURCHASE_PRICE: 400000
TOTAL_COST: 418000
DOWNPAY: 98000
ANNUAL_GROSS_INCOME: +49920
ANNUAL_EXPENSES: -12760
NOI: 37160
ANNUAL_MORTGAGE_PAYMENT: -25548
ANNUAL_CASH_FLOW: 11612
CAP_RATE: 8.89%
CASH_ROI: 11.85%
TOTAL_ROI: 23.70%

# output to file
$ ./deal_analysis.py data/example.yml 1
input: https://raw.githubusercontent.com/xiaotdl/rental_property_deal_analysis/master/data/example.yml
output: https://raw.githubusercontent.com/xiaotdl/rental_property_deal_analysis/master/result/example.txt
```

## Other

### Review Results
```
$ tail result/*MemphisInvest*
```

### Refresh Results 
```
$ ./refresh.py
```
