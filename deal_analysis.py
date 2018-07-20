#!/usr/bin/env python
"""
This script is running numbers and calculate cash flow stats.

REF: https://www.biggerpockets.com/renewsblog/2010/06/30/introduction-to-real-estate-analysis-investing/
"""
from __future__ import division
import os
import re
import sys
import math
import yaml


if len(sys.argv) >= 2:
    data_file = sys.argv[1]
else:
    data_file = "data/example.yml"

OUTPUT_PREFIX = 'https://raw.githubusercontent.com/xiaotdl/rental_property_deal_analysis/master/'
OUTPUT_DIR = 'result'
WRITE_TO_OUTPUT_DIR = False
if len(sys.argv) >= 3 and sys.argv[2]:
    WRITE_TO_OUTPUT_DIR = True

DATA = None
print "input: %s" % OUTPUT_PREFIX+data_file
with open(data_file, 'r') as f:
    try:
        DATA = yaml.load(f)
    except yaml.YAMLError as e:
        print("ERROR: %s" % e)


def roundup(f):
    return int(math.ceil(f))

def rounddown(f):
    return int(f)

def show(klass, debug=False, stream=sys.stdout):
    stream.write("== %s ==\n" % getattr(klass, "_%s__name" % klass.__name__))
    if klass.__dict__.get("_%s__attrs_order" % klass.__name__) and debug == False:
        attrs = getattr(klass, "_%s__attrs_order" % klass.__name__)
    else:
        attrs = sorted(klass.__dict__.keys())
    for attr in attrs:
        if not attr.startswith('__') and not attr.startswith("_"+klass.__name__):
            value = getattr(klass, attr)
            if not callable(value):
                if not debug:
                    attr = re.sub(r"^_", "", attr)
                    attr = re.sub(r"_FMT$", "", attr)
                stream.write("%s: %s\n" % (attr, value))
    stream.write("\n")

def calculate_monthly_mortgage_payment(loan, years, apr):
    """ref: https://www.mtgprofessor.com/formulas.htm"""
    MONS_PER_YR = 12
    c = apr/MONS_PER_YR
    n = MONS_PER_YR * years
    fixed_monthly_payment = loan * (c * (1 + c)**n) / ((1 + c)**n - 1)
    return roundup(fixed_monthly_payment)

def calculate_mortgage_balance(loan, years, apr, years_elapsed):
    """ref: https://www.mtgprofessor.com/formulas.htm"""
    MONS_PER_YR = 12
    c = apr/MONS_PER_YR
    n = MONS_PER_YR * years
    p = MONS_PER_YR * years_elapsed
    balance = loan * ((1 + c)**n - (1 + c)**p) / ((1 + c)**n - 1)
    return roundup(balance)


class Property(object):
    """Property Details: This is information about the physical design of the property, including number of units, square footage, utility metering design, etc"""
    __name = 'PROPERTY'
    __source=['seller', 'local County Records Office']
    __attrs_order = [
        'ADDRESS',
        'LINK',
        'DESCRIPTION',
        'BEDROOMS',
        'BATHROOMS',
        'UNITS',
        'SQFTS',
    ]

    ADDRESS = DATA["PROPERTY"]["ADDRESS"]
    LINK = DATA["PROPERTY"]["LINK"]
    DESCRIPTION = DATA["PROPERTY"]["DESCRIPTION"]
    BEDROOMS = DATA["PROPERTY"]["BEDROOMS"]
    BATHROOMS = DATA["PROPERTY"]["BATHROOMS"]
    UNITS = DATA["PROPERTY"]["UNITS"]
    SQFTS = DATA["PROPERTY"]["SQFTS"]


class Purchase(object):
    """Purchase Information: This is basic cost information about the property you are considering, such as the purchase price, the price of any rehab or improvement work you'll need to do, etc"""
    __name = 'PURCHASE'
    __source = ['seller', 'property inspector to ensure that there are no hidden issues or problems']
    __attrs_order = [
        'PURCHASE_PRICE',
        'IMPROVEMENT_COST',
        'CLOSING_COST',
        '_TOTAL_COST',
    ]

    PURCHASE_PRICE = DATA["PURCHASE"]["PURCHASE_PRICE"]
    IMPROVEMENT_COST = DATA["PURCHASE"]["IMPROVEMENT_COST"] # CapEx, REPAIR, NEW APPLIANCE, etc.
    CLOSING_COST = DATA["PURCHASE"]["CLOSING_COST"] # MORTGAGE COST, TITLE TRANSFER, etc.

    _TOTAL_COST = PURCHASE_PRICE + IMPROVEMENT_COST + CLOSING_COST


class Financing(object):
    """Financing Details: These are the details of the loan you will obtain to finance the property. This includes such things as total loan amount, downpayment amount, interest rate, closing costs, etc"""
    __name = 'FINANCING'
    __source = ['lender', 'mortgage broker']
    __attrs_order = [
        '_MORTGAGE_LOAN_DOWNPAY_PERCENTAGE_FMT',
        '_MORTGAGE_LOAN_DOWNPAY_AMOUNT',
        '_MORTGAGE_LOAN_AMOUNT',
        'MORTGAGE_LOAN_YRS',
        '_MORTGAGE_LOAN_APR_FMT',
        '_MONTHLY_MORTGAGE_LOAN_PAYMENT',
        '_TOTAL_CASH_OUTLAY',
    ]

    MORTGAGE_LOAN_DOWNPAY_PERCENTAGE = DATA["FINANCING"]["MORTGAGE_LOAN_DOWNPAY_PERCENTAGE"]
    _MORTGAGE_LOAN_DOWNPAY_PERCENTAGE_FMT = "%.2f%%" % (MORTGAGE_LOAN_DOWNPAY_PERCENTAGE * 100)
    _MORTGAGE_LOAN_DOWNPAY_AMOUNT = roundup(Purchase.PURCHASE_PRICE * MORTGAGE_LOAN_DOWNPAY_PERCENTAGE)

    _MORTGAGE_LOAN_AMOUNT = roundup(Purchase.PURCHASE_PRICE * (1 - MORTGAGE_LOAN_DOWNPAY_PERCENTAGE))
    MORTGAGE_LOAN_YRS = DATA["FINANCING"]["MORTGAGE_LOAN_YRS"]
    MORTGAGE_LOAN_APR = DATA["FINANCING"]["MORTGAGE_LOAN_APR"]
    _MORTGAGE_LOAN_APR_FMT = "%.2f%%" % (MORTGAGE_LOAN_APR * 100) 
    _MONTHLY_MORTGAGE_LOAN_PAYMENT = \
        calculate_monthly_mortgage_payment(
            _MORTGAGE_LOAN_AMOUNT,
            MORTGAGE_LOAN_YRS,
            MORTGAGE_LOAN_APR
        )
    _ANNUAL_MORTGAGE_LOAN_PAYMENT = _MONTHLY_MORTGAGE_LOAN_PAYMENT * 12

    _TOTAL_CASH_OUTLAY = _MORTGAGE_LOAN_DOWNPAY_AMOUNT + Purchase.IMPROVEMENT_COST + Purchase.CLOSING_COST


class Income(object):
    """Income: This the detailed information about the income the property produces, such as rent payments"""
    __name = "INCOME"
    __source = ['pro-forma', 'property management company currently running the property']
    __attrs_order = [
        'MONTHLY_RENT',
        '_VACANCY_RATE_FMT',
        '_MONTHLY_NET_RENT',

        'MONTHLY_OTHER_INCOME',

        '_MONTHLY_GROSS_INCOME',
        '_ANNUAL_GROSS_INCOME',
    ]

    MONTHLY_RENT = DATA["INCOME"]["MONTHLY_RENT"]
    VACANCY_RATE = DATA["INCOME"]["VACANCY_RATE"]
    _VACANCY_RATE_FMT = "%.2f%%" % (VACANCY_RATE * 100)
    _MONTHLY_NET_RENT = roundup(MONTHLY_RENT * (1 - VACANCY_RATE))
    _ANNUAL_NET_RENT = _MONTHLY_NET_RENT * 12

    MONTHLY_OTHER_INCOME = DATA["INCOME"]["MONTHLY_OTHER_INCOME"]
    _ANNUAL_OTHER_INCOME = MONTHLY_OTHER_INCOME * 12

    _MONTHLY_GROSS_INCOME = _MONTHLY_NET_RENT + MONTHLY_OTHER_INCOME
    _ANNUAL_GROSS_INCOME = _MONTHLY_GROSS_INCOME * 12


class Expenses(object):
    """Expenses: This is the detailed information about costs of maintaining the property, including such things as property taxes, insurance, maintenance, etc"""
    __name = "EXPENSES"
    __source = ['pro-forma', 'building inspector could help warn you about any major repairs that may be coming due in the near future (new roof, new heating/AC, etc)']
    __attrs_order = [
        '_PROPERTY_MANAGEMENT_FEE_RATE_FMT',
        '_MONTHLY_PROPERTY_MANAGEMENT_FEE',
        '_PROPERTY_TAX_RATE_FMT',
        '_MONTHLY_PROPERTY_TAX',
        'MONTHLY_INSURANCE',
        'MONTHLY_HOA',
        'MONTHLY_MAINTENANCE',
        'MONTHLY_UTILITIES',
        'MONTHLY_ADVERTISING',
        'MONTHLY_LANDSCAPING',

        '_TOTAL_MONTHLY_EXPENSES',
        '_TOTAL_ANNUAL_EXPENSES',
    ]

    PROPERTY_MANAGEMENT_FEE_RATE = DATA["EXPENSES"]["PROPERTY_MANAGEMENT_FEE_RATE"]
    _PROPERTY_MANAGEMENT_FEE_RATE_FMT = "%.2f%%" % (PROPERTY_MANAGEMENT_FEE_RATE * 100)
    _MONTHLY_PROPERTY_MANAGEMENT_FEE = int(math.ceil(PROPERTY_MANAGEMENT_FEE_RATE * Income._MONTHLY_NET_RENT))
    _ANNUAL_PROPERTY_MANAGEMENT_FEE = _MONTHLY_PROPERTY_MANAGEMENT_FEE * 12

    PROPERTY_TAX_RATE = DATA["EXPENSES"]["PROPERTY_TAX_RATE"]
    _PROPERTY_TAX_RATE_FMT = "%.2f%%" % (PROPERTY_TAX_RATE * 100)
    _ANNUAL_PROPERTY_TAX = roundup(PROPERTY_TAX_RATE * Purchase.PURCHASE_PRICE)
    _MONTHLY_PROPERTY_TAX = roundup(_ANNUAL_PROPERTY_TAX / 12)

    MONTHLY_INSURANCE = DATA["EXPENSES"]["MONTHLY_INSURANCE"]
    _ANNUAL_INSURANCE = MONTHLY_INSURANCE * 12

    MONTHLY_HOA = DATA["EXPENSES"]["MONTHLY_HOA"]
    _ANNUAL_HOA = MONTHLY_HOA * 12

    # Maintenance & Repair + Grounds Maintenance + Cleaning + Pest Control
    MONTHLY_MAINTENANCE = DATA["EXPENSES"]["MONTHLY_MAINTENANCE"]
    _ANNUAL_MAINTENANCE = MONTHLY_MAINTENANCE * 12

    MONTHLY_UTILITIES = DATA["EXPENSES"]["MONTHLY_UTILITIES"]
    _ANNUAL_UTILITIES = MONTHLY_UTILITIES * 12

    MONTHLY_ADVERTISING = DATA["EXPENSES"]["MONTHLY_ADVERTISING"]
    _ANNUAL_ADVERTISING = MONTHLY_ADVERTISING * 12

    MONTHLY_LANDSCAPING = DATA["EXPENSES"]["MONTHLY_LANDSCAPING"]
    _ANNUAL_LANDSCAPING = MONTHLY_LANDSCAPING * 12

    _TOTAL_ANNUAL_EXPENSES = \
        _ANNUAL_PROPERTY_MANAGEMENT_FEE + \
        _ANNUAL_PROPERTY_TAX + \
        _ANNUAL_INSURANCE + \
        _ANNUAL_HOA + \
        _ANNUAL_MAINTENANCE + \
        _ANNUAL_UTILITIES + \
        _ANNUAL_ADVERTISING + \
        _ANNUAL_LANDSCAPING
    _TOTAL_MONTHLY_EXPENSES = roundup(_TOTAL_ANNUAL_EXPENSES / 12)


class Misc(object):
    __name = "MISC"
    __source = ['assumption']
    __attrs_order = [
        '_PROPERTY_APPRECIATION_RATE_FMT',
        '_PROPERTY_APPRECIATION_AMOUNT',
        '_EQUITY_ACCURAL_AMOUNT',
    ]

    PROPERTY_APPRECIATION_RATE = DATA["MISC"]["PROPERTY_APPRECIATION_RATE"]
    _PROPERTY_APPRECIATION_RATE_FMT = "%.2f%%" % (PROPERTY_APPRECIATION_RATE * 100)
    _PROPERTY_APPRECIATION_AMOUNT = roundup(PROPERTY_APPRECIATION_RATE * Purchase._TOTAL_COST)
    _EQUITY_ACCURAL_AMOUNT = \
        Financing._MORTGAGE_LOAN_AMOUNT - \
        calculate_mortgage_balance(
            Financing._MORTGAGE_LOAN_AMOUNT,
            Financing.MORTGAGE_LOAN_YRS,
            Financing.MORTGAGE_LOAN_APR,
            1
        )


class Metrics(object):
    __name = "METRICS"
    __source = ['calculation']
    __attrs_order = [
        '_PRICE_PER_SQFT',
        '_COST_PER_UNIT',
        '_NOI',
        '_CASH_FLOW',
        '_MONTHLY_CASH_FLOW',
        '_DSCR_FMT',
        '_CAP_RATE_FMT',
        '_CASH_ROI_FMT',
        '_TOTAL_ROI_FMT',
    ]

    _PRICE_PER_SQFT = roundup(Purchase._TOTAL_COST / Property.SQFTS)
    _COST_PER_UNIT = roundup(Purchase._TOTAL_COST / Property.UNITS)

    # NOI = INCOME - EXPENSES
    _NOI = Income._ANNUAL_GROSS_INCOME - Expenses._TOTAL_ANNUAL_EXPENSES

    # CASH_FLOW = NOI - DEBT
    _CASH_FLOW = _NOI - Financing._ANNUAL_MORTGAGE_LOAN_PAYMENT
    _MONTHLY_CASH_FLOW = rounddown(_CASH_FLOW / 12)

    # DSCR = NOI / DEBT
    _DSCR = _NOI / Financing._ANNUAL_MORTGAGE_LOAN_PAYMENT
    _DSCR_FMT = "%.2f%%" % (_DSCR * 100)

    # ROI = CASH_FLOW / INVESTMENT_BASIS
    # ----------------------------------
    # CAP_RATE = NOI / TOTAL_COST
    # CASH_ROI = CASH_ON_CASH_RETURN = CASH_FLOW / TOTAL_OUT_OF_POCKET
    # TOTAL_ROI = (CASH_FLOW + PROPERTY_APPRECIATION + EQUITY_ACCURAL + TAX_CONSEQUENCES) / TOTAL_COST
    _CAP_RATE = _NOI / Purchase._TOTAL_COST # EXPECT: 10%+
    _CAP_RATE_FMT = "%.2f%%" % (_CAP_RATE * 100)

    _CASH_ROI = _CASH_FLOW / Financing._TOTAL_CASH_OUTLAY # EXPECT: 10%+
    _CASH_ROI_FMT = "%.2f%%" % (_CASH_ROI * 100)

    TAX_CONSEQUENCES = 0

    _TOTAL_ROI = (_CASH_FLOW + Misc._PROPERTY_APPRECIATION_AMOUNT + Misc._EQUITY_ACCURAL_AMOUNT + TAX_CONSEQUENCES) / Financing._TOTAL_CASH_OUTLAY
    _TOTAL_ROI_FMT = "%.2f%%" % (_TOTAL_ROI * 100)


class Summary(object):
    __name = "SUMMARY"
    __attrs_order = [
        'PURCHASE_PRICE',
        'TOTAL_COST',
        'TOTAL_CASH_OUTLAY',

        'ANNUAL_GROSS_INCOME',
        'ANNUAL_EXPENSES',
        'NOI',
        'ANNUAL_MORTGAGE_PAYMENT',
        'ANNUAL_CASH_FLOW',

        'CAP_RATE',
        'CASH_ROI',
        'TOTAL_ROI',
    ]

    PURCHASE_PRICE = Purchase.PURCHASE_PRICE
    TOTAL_COST = Purchase._TOTAL_COST
    TOTAL_CASH_OUTLAY = Financing._TOTAL_CASH_OUTLAY

    ANNUAL_GROSS_INCOME = '+%s' % Income._ANNUAL_GROSS_INCOME
    ANNUAL_EXPENSES = '-%s' % Expenses._TOTAL_ANNUAL_EXPENSES
    NOI = Metrics._NOI
    ANNUAL_MORTGAGE_PAYMENT = '-%s' % Financing._ANNUAL_MORTGAGE_LOAN_PAYMENT
    ANNUAL_CASH_FLOW = Metrics._CASH_FLOW

    CAP_RATE = Metrics._CAP_RATE_FMT

    CASH_ROI = Metrics._CASH_ROI_FMT

    TOTAL_ROI = Metrics._TOTAL_ROI_FMT


def main():
    stream = sys.stdout
    if WRITE_TO_OUTPUT_DIR:
        outfilename = os.path.splitext(os.path.basename(data_file))[0] + '.txt'
        outfile = os.path.join(OUTPUT_DIR, outfilename)
        stream = open(outfile, 'w')
        print "output: %s" % OUTPUT_PREFIX+outfile

    show(Property, stream=stream)
    show(Purchase, stream=stream)
    show(Financing, stream=stream)
    show(Income, stream=stream)
    show(Expenses, stream=stream)
    show(Misc, stream=stream)
    show(Metrics, stream=stream)
    show(Summary, stream=stream)

    if WRITE_TO_OUTPUT_DIR:
        stream.close()

    sys.exit(0)


if __name__ == '__main__':
    main()
