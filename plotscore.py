import qraat, qraat.srv
import MySQLdb as mdb
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as pp
from scipy.optimize import curve_fit
import os, sys, time
import pickle


exp = []

for EST_SCORE_THRESHOLD in map(lambda(x) : float(x), sys.argv[1:]):

  print "Reading result%0.2f" % EST_SCORE_THRESHOLD
  (X, Y, pos, neg) = pickle.load(open('result%0.2f' % EST_SCORE_THRESHOLD))
  extent = [0.0, 4.0, 
            0.0, 0.2]
  
  ### Trade-off policy ###
  C_p = 10 
  C_n = 1
  tradeoff = abs((C_p * pos) + (C_n * neg)) # TODO

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
      i = int(x / 0.04)
      j = int(f(x, *popt) / 0.005) 
      total_cost += tradeoff[-j,i]
    print "   cost = %0.4f" % total_cost
    exp.append((EST_SCORE_THRESHOLD, string, total_cost, "hyper"))
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
    i = int(x / 0.04)
    j = int(p(x) / 0.005) 
    total_cost += tradeoff[-j,i]
  print "   cost = %0.4f" % total_cost
  exp.append((EST_SCORE_THRESHOLD, string, total_cost, "poly"))
 
  print # Best constant pulse error 
  total_costs = np.zeros(Y.shape)
  for j in range(Y.shape[0]): 
    total_costs[j] = np.sum(tradeoff[j,:])
  const = Y[-np.argmin(total_costs)]
  string = "lambda(x) : %0.4f" % const
  print "const =", string
  print "   cost = %0.4f" % (np.min(total_costs))
  exp.append((EST_SCORE_THRESHOLD, string, total_cost, "const"))

  print # Optimal trade-off
  print "Optimal trade-off:\n", opt
  print "  cost = %0.4f" % opt_total_cost 
  exp.append((EST_SCORE_THRESHOLD, (opt, const), total_cost, "opt"))

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
  pp.savefig('false_positives_%0.2f.png' % EST_SCORE_THRESHOLD)
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
  pp.savefig('false_negatives_%0.2f.png' % EST_SCORE_THRESHOLD)
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
  pp.savefig('tradeoff_%0.2f.png' % EST_SCORE_THRESHOLD)
  pp.title("Tradeo off space (threshold = %0.2f" % EST_SCORE_THRESHOLD)
  pp.xlabel("Variation")
  pp.ylabel("Score error")
  pp.clf()

pickle.dump(exp, open('exp', 'w'))
