
import pickle
  
(X, Y, Z, report) = pickle.load(open('report'))

print "False positive rate\n"; index = 5
for score_thresh in sorted(X):
  print "      ",
  policies = list(reversed(sorted(Y, key=lambda(x) : float(x[0]) / x[1])))
  for policy in policies: 
    print "(%2d,%2d)          " % policy,
  print "\n"
  print "%.2f  " % score_thresh,
  for curve in ['opt', 'hyper', 'poly', 'const']: 
    for policy in policies:
      val = report[score_thresh][policy].get(curve)
      if val == None:
        print "%s =       " % (curve),
      else: print "%-5s = %0.4f   " % (curve, val[index]),
    print "\n      ",
        
