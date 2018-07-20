# C0: initial outlay
# Ct: net cash flows
# n: period
# N: holding periods
# r: discount rate

def NPV(C0, Ct, r):
    N = len(Ct)
    TOTAL_PV = 0
    for n in range(1, N + 1):
        PV = Ct[n-1] / ((1 + r) ** n)
        print "Year: %s, Cash Flow: %s, PV: %s" % (n, Ct[n-1], int(PV))
        TOTAL_PV += int(PV)
    NPV = TOTAL_PV - C0
    print "TOTAL PV: %s" % TOTAL_PV
    print "INITIAL OUTLAY: %s" % C0
    print "NPV: %s" % NPV
    return NPV

NPV(250000, [100000, 150000, 200000, 250000, 300000], 0.10)
