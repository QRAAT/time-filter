# Evaluate the performance of (est threshold, score error function) pairs 
# for various trade off policies. 

import qraat, qraat.srv
import time, os, sys, commands
import MySQLdb as mdb
from optparse import OptionParser
import numpy as np
import pickle

dep_id  = 105
t_start = 1410721127
t_end   = 1410807696

exp = pickle.load(open('exp'))

def _opt(x, opt, const):
   Y = opt
   i = int(x / 0.04)
   if i < len(Y): 
     return Y[i]
   else: 
     return const


try: 
  start = time.time()
  print "evaluate: start time:", time.asctime(time.localtime(start))
  db_con = qraat.srv.util.get_db('writer')

  # Partition of good / bad points. 
  print "evaluate: loading test data ... "
  points = qraat.csv.csv('partition.csv')
  good = {} 
  for p in points: 
    good[int(p.est_id)] = True if int(p.good) is 1 else False
  
  results = {}
  X = set(); Y = set(); Z = set()

  for (score_thresh, policy_dict) in exp.iteritems():
    X.add(score_thresh)
    results[score_thresh] = {}
    for (policy, curves) in policy_dict.iteritems():
      Y.add(policy)
      results[score_thresh][policy] = {}
      for (score_err_str, cost, curve) in curves:
        Z.add(curve)

        # Run filter. 
        print "evaluate: score thresh. %0.2f, policy %s, %s" % (score_thresh, policy, curve),
        if curve == 'opt': 
          print
          (opt, const) = score_err_str
          qraat.srv.signal.SCORE_ERROR = lambda(x) : _opt(x, opt, const)
        else: 
          print "=", score_err_str
          qraat.srv.signal.SCORE_ERROR = eval(score_err_str)
        (total, _) = qraat.srv.signal.Filter(db_con, dep_id, t_start, t_end)
        
        # Evaluate result.
        cur = db_con.cursor()
        cur.execute('''SELECT estID, score / theoretical_score
                         FROM estscore JOIN est ON est.ID = estscore.estID
                        WHERE deploymentID = %s 
                          AND timestamp >= %s
                          AND timestamp < %s''', (dep_id, t_start, t_end))

        false_pos = false_neg = 0
        good_count = bad_count = 0
        for (id, rel_score) in cur.fetchall():
          if good.get(id) == None or rel_score < 0:  
            continue # Skip points that didn't pass lower filters.
        
          if good[id] and rel_score > score_thresh:        pass # Ok
          elif not good[id] and rel_score <= score_thresh: pass # Ok
          elif not good[id] and rel_score > score_thresh:  false_pos += 1 # False positive
          elif good[id] and rel_score <= score_thresh:     false_neg += 1 # False negative
          if good[id]: good_count += 1
          else: bad_count += 1
       
        print 
        print "Good points . . . . %d" % good_count
        print "False negatives . . %d" % false_neg
        print "   Rate . . . . . . %0.4f" % (float(false_neg) / good_count)
        print 
        print "Bad points  . . . . %d" % bad_count
        print "False positives . . %d" % false_pos
        print "   Rate . . . . . . %0.4f" % (float(false_pos) / bad_count)
        print

        results[score_thresh][policy][curve] = (good_count, false_neg, float(false_neg) / good_count, 
                                                bad_count, false_pos, float(false_pos) / bad_count, 
                                                cost) 

  pickle.dump((X, Y, Z, results), open('report', 'w'))
  
except mdb.Error, e:
  print >>sys.stderr, "evaluate: error: [%d] %s" % (e.args[0], e.args[1])
  sys.exit(1)

except qraat.error.QraatError, e:
  print >>sys.stderr, "evaluate: error: %s." % e

finally: 
  print "evaluate: finished in %.2f seconds." % (time.time() - start)
