import qraat, qraat.srv
import MySQLdb as mdb
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as pp
from scipy.optimize import curve_fit
import os, sys, time
import pickle

score_error_step = 0.005
variation_step = 0.025

exp = {}

basename = sys.argv[1]
#policies = [(20, 1), (18, 1), (16, 1), (14, 1), (12, 1), (10,1), (8,1), (5,1), (3,1), (2,1)]
policies = [(2,1), (1,1)]

for EST_SCORE_THRESHOLD in map(lambda(x) : float(x), sys.argv[2:]):

  exp[EST_SCORE_THRESHOLD] = {}

  for (Cp, Cn) in policies:
    
    #if (Cp < 15 and EST_SCORE_THRESHOLD == 0.3): 
    #  exp[EST_SCORE_THRESHOLD][(Cp, Cn)] = []
    #  continue
    
    curves = []

    print "Running %0.2f, (%d, %d)" % (EST_SCORE_THRESHOLD, Cp, Cn)
    (X, Y, pos, neg) = pickle.load(open('%s%0.2f' % (basename, EST_SCORE_THRESHOLD)))
    extent = [0.0, 1.0, 
              0.0, 0.2]
    
    ### Trade-off policy ###
    tradeoff = abs((Cp * pos) + (Cn * neg)) # TODO

    opt = []
    opt_total_cost = 0
    for i in range(X.shape[0]):
      opt.append(Y[-np.argmin(tradeoff[:,i])])
      opt_total_cost += np.min(tradeoff[:,i])
    opt =  np.array(opt)
    

    # Hyperbolic f(x)
    class F:

      def __call__(self, x, a, b, c): 
        return (a / (x + b)) + c

      def inverse(self, y, a, b, c):
        return (a / (y - c)) - b 

      def get(self, popt):
        return "lambda(x) : (%0.4f / (x + %0.4f)) + %0.4f" % tuple(popt)

    print 
    try: 
      f = F()
      popt, pcov = curve_fit(f.__call__, X, opt)
      string = f.get(popt)
      print "f(x) =", string
      total_cost = 0
      for x in X:
        i = int(x / variation_step)
        j = int(f(x, *popt) / score_error_step) 
        if j < len(Y): total_cost += tradeoff[-j,i]
      print "   cost = %0.4f" % total_cost
      curves.append((string, total_cost, "hyper"))
    except RuntimeError: 
      f = None
      print "f(x) = no fit" 

    print # 6-degree polynomial p(x)
    coeff = np.polyfit(X, opt, 6)
    p = np.poly1d(coeff) 
    string = "np.poly1d(%s)" % map(lambda x : round(x, 5), list(coeff))
    print "p(x) =", string
    total_cost = 0
    for x in X:
      i = int(x / variation_step)
      j = int(p(x) / score_error_step) 
      total_cost += tradeoff[-j,i]
    print "   cost = %0.4f" % total_cost
    curves.append((string, total_cost, "poly"))
   
    print # Best constant pulse error 
    total_costs = np.zeros(Y.shape)
    for j in range(Y.shape[0]): 
      total_costs[j] = np.sum(tradeoff[j,:])
    const = Y[-np.argmin(total_costs)]
    string = "lambda(x) : %0.4f" % const
    print "const =", string
    print "   cost = %0.4f" % (np.min(total_costs))
    curves.append((string, total_cost, "const"))

    print # Optimal trade-off
    print "Optimal trade-off:\n", opt
    print "  cost = %0.4f" % opt_total_cost 
    curves.append(((opt, const), total_cost, "opt"))

    exp[EST_SCORE_THRESHOLD][(Cp, Cn)] = curves
    
    ### Plot ###
    Y = opt
    
    # False positives
    pp.imshow(pos, extent=extent, aspect='auto', interpolation='nearest')
    pp.plot(X, Y, 'wo', label='Optimal trade-off')
    pp.plot(X, p(X), 'k-', label="Fitted curve")
    if f: pp.plot(X, f(X, *popt), 'k.', label="Fitted curve")
    fig = pp.gcf()
    fig.set_size_inches(16,12)
    cb = pp.colorbar()
    cb.set_label("Total")
    pp.savefig('false_positives_%0.2f_%d-%d.png' % (EST_SCORE_THRESHOLD, Cp, Cn))
    pp.title("Frequency of false positives (threshold = %0.2f" % EST_SCORE_THRESHOLD)
    pp.xlabel("Variation")
    pp.ylabel("Score error")
    pp.clf()

    # False negatives
    pp.imshow(neg, extent=extent, aspect='auto', interpolation='nearest')
    pp.plot(X, Y, 'wo', label='Optimal trade-off')
    pp.plot(X, p(X), 'k-', label="Fitted curve")
    if f: pp.plot(X, f(X, *popt), 'k.', label="Fitted curve")
    fig = pp.gcf()
    fig.set_size_inches(16,12)
    cb = pp.colorbar()
    cb.set_label("Total")
    pp.savefig('false_negatives_%0.2f_%d-%d.png' % (EST_SCORE_THRESHOLD, Cp, Cn))
    pp.title("Frequency of false negatives (threshold = %0.2f" % EST_SCORE_THRESHOLD)
    pp.xlabel("Variation")
    pp.ylabel("Score error")
    pp.clf()

    # Trade-off space
    pp.imshow(tradeoff, extent=extent, aspect='auto', interpolation='nearest')
    pp.plot(X, Y, 'wo', label='Optimal trade-off')
    pp.plot(X, p(X), 'k-', label="Fitted curve")
    if f: pp.plot(X, f(X, *popt), 'k.', label="Fitted curve")
    fig = pp.gcf()
    fig.set_size_inches(16,12)
    cb = pp.colorbar()
    cb.set_label("Total")
    pp.savefig('tradeoff_%0.2f_%d-%d.png' % (EST_SCORE_THRESHOLD, Cp, Cn))
    pp.title("Tradeo off space (threshold = %0.2f" % EST_SCORE_THRESHOLD)
    pp.xlabel("Variation")
    pp.ylabel("Score error")
    pp.clf()

pickle.dump(exp, open('exp', 'w'))
