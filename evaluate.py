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

  for (EST_SCORE_THRESHOLD, score_err_str, cost, pretty_str) in exp: 
    
    # Run filter. 
    print "evaluate: running filter (%0.2f) ... " % EST_SCORE_THRESHOLD
    if pretty_str == 'opt': 
      (opt, const) = score_err_str
      qraat.srv.signal.SCORE_ERROR = lambda(x) : _opt(x, opt, const)
    else: 
      qraat.srv.signal.SCORE_ERROR = eval(score_err_str)
    (total, _) = qraat.srv.signal.Filter(db_con, dep_id, t_start, t_end)
    
    # Generate report. 
    cur = db_con.cursor()
    cur.execute('''SELECT estID, score / theoretical_score
                     FROM estscore JOIN est ON est.ID = estscore.estID
                    WHERE deploymentID = %s 
                      AND timestamp >= %s
                      AND timestamp < %s''', (dep_id, t_start, t_end))

    false_pos = false_neg = 0
    good_count = bad_count = 0
    for (id, rel_score) in cur.fetchall():
      if good.get(id) == None: 
        #print 'Uh oh!', id
        continue
    
      if good[id] and rel_score > EST_SCORE_THRESHOLD:        pass # Ok
      elif not good[id] and rel_score <= EST_SCORE_THRESHOLD: pass # Ok
      elif not good[id] and rel_score > EST_SCORE_THRESHOLD:  false_pos += 1 # False positive
      elif good[id] and rel_score <= EST_SCORE_THRESHOLD:     false_neg += 1 # False negative
      if good[id]: good_count += 1
      else: bad_count += 1
    
    print 
    print "Score error . . . . %s" % pretty_str
    print "Score threshold . . %0.2f" % EST_SCORE_THRESHOLD
    print 
    print "Good points . . . . %d" % good_count
    print "False negatives . . %d" % false_neg
    print "   Rate . . . . . . %0.4f" % (float(false_neg) / good_count)
    print 
    print "Bad points  . . . . %d" % bad_count
    print "False positives . . %d" % false_pos
    print "   Rate . . . . . . %0.4f" % (float(false_pos) / bad_count)
    print


except mdb.Error, e:
  print >>sys.stderr, "evaluate: error: [%d] %s" % (e.args[0], e.args[1])
  sys.exit(1)

except qraat.error.QraatError, e:
  print >>sys.stderr, "evaluate: error: %s." % e

finally: 
  print "evaluate: finished in %.2f seconds." % (time.time() - start)
