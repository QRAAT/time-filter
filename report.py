
import pickle
  
(X, Y, Z, report) = pickle.load(open('report'))

print "False positive rate"; index = 5
print "-------------------\n"
print "      ",
policies = list(reversed(sorted(Y, key=lambda(x) : float(x[0]) / x[1])))
for policy in policies: 
  print "(%2d,%2d)          " % policy,
print
for score_thresh in sorted(X):
  print "\n%.2f  " % score_thresh,
  for curve in ['opt', 'hyper', 'poly', 'const']: 
    for policy in policies:
      val = report[score_thresh][policy].get(curve)
      if val == None:
        print "%-5s =          " % (curve),
      else: print "%-5s = %0.4f   " % (curve, val[index]),
    print "\n      ",


print
print
print "False negative rate"; index = 2
print "-------------------\n"
print "      ",
policies = list(reversed(sorted(Y, key=lambda(x) : float(x[0]) / x[1])))
for policy in policies: 
  print "(%2d,%2d)          " % policy,
print
for score_thresh in sorted(X):
  print "\n%.2f  " % score_thresh,
  for curve in ['opt', 'hyper', 'poly', 'const']: 
    for policy in policies:
      val = report[score_thresh][policy].get(curve)
      if val == None:
        print "%-5s =          " % (curve),
      else: print "%-5s = %0.4f   " % (curve, val[index]),
    print "\n      ",


print
print
print "Total cost"; index = 6
print "----------\n"
print "      ",
policies = list(reversed(sorted(Y, key=lambda(x) : float(x[0]) / x[1])))
for policy in policies: 
  print "(%2d,%2d)          " % policy,
print
for score_thresh in sorted(X):
  print "\n%.2f  " % score_thresh,
  for curve in ['opt', 'hyper', 'poly', 'const']: 
    for policy in policies:
      val = report[score_thresh][policy].get(curve)
      if val == None:
        print "%-5s =           " % (curve),
      else: print "%-5s = %3.2f    " % (curve, val[index]),
    print "\n      ",



print
print
print "False positive count"; index = 4
print "--------------------\n"
print "      ",
policies = list(reversed(sorted(Y, key=lambda(x) : float(x[0]) / x[1])))
for policy in policies: 
  print "(%2d,%2d)          " % policy,
print
for score_thresh in sorted(X):
  print "\n%.2f  " % score_thresh,
  for curve in ['opt', 'hyper', 'poly', 'const']: 
    for policy in policies:
      val = report[score_thresh][policy].get(curve)
      if val == None:
        print "%-5s =          " % (curve),
      else: print "%-5s = %-5d    " % (curve, val[index]),
    print "\n      ",


print
print
print "False negative count"; index = 1
print "--------------------\n"
print "      ",
policies = list(reversed(sorted(Y, key=lambda(x) : float(x[0]) / x[1])))
for policy in policies: 
  print "(%2d,%2d)          " % policy,
print
for score_thresh in sorted(X):
  print "\n%.2f  " % score_thresh,
  for curve in ['opt', 'hyper', 'poly', 'const']: 
    for policy in policies:
      val = report[score_thresh][policy].get(curve)
      if val == None:
        print "%-5s =          " % (curve),
      else: print "%-5s = %-5d    " % (curve, val[index]),
    print "\n      ",

