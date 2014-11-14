import qraat, qraat.srv
import MySQLdb as mdb
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as pp
import os, sys, time
import pickle

dep_id  = 105
t_start = 1410721127
t_end   = 1410807696

try: 
  start = time.time()
  print >>sys.stderr, "misc: start time:", time.asctime(time.localtime(start))

  db_con = qraat.srv.util.get_db('writer')
  cur = db_con.cursor()
 
  points = qraat.csv.csv('partition.csv')
  good = {} 
  for p in points: 
    good[int(p.est_id)] = True if int(p.good) is 1 else False

  # Number of band filter false negatives
  
  #  print "misc: running filter ..."
  #  (total, _) = qraat.srv.signal.Filter(db_con, dep_id, t_start, t_end)
  # 
  #  cur.execute('''SELECT estID, score 
  #                   FROM estscore
  #                   JOIN est ON est.ID = estscore.estID
  #                  WHERE deploymentID = %s
  #                    AND timestamp >= %s
  #                    AND timestamp <= %s''', (dep_id, t_start, t_end))
  #
  #  total = count = 0
  #  for (id, score) in cur.fetchall():
  #    if score < 0: 
  #      total += 1
  #      if good.get(id) == True:
  #        count += 1
  #
  #  print "misc: band filter false negatives:", count, "out of", total

  # Data rate w.r.t variaiton

  #  variation_step = 0.04
  #  X = np.arange(0, 4, variation_step)
  #  Y = []
  #  
  #  cur.execute('''SELECT timestamp, pulse_interval, pulse_variation
  #                   FROM estinterval
  #                  WHERE deploymentID = %s 
  #                    AND timestamp >= %s
  #                    AND timestamp <= %s
  #                  ORDER BY timestamp''', (dep_id, t_start, t_end))
  #
  #  intervals = list(cur.fetchall())
  #  
  #  for variation in X:
  #    total = 0
  #    for i in range(len(intervals)-1):
  #      if variation <= intervals[i][2] and intervals[i][2] < variation + variation_step:
  #        cur.execute('''SELECT count(*)
  #                         FROM est
  #                        WHERE deploymentID = %s 
  #                          AND timestamp >= %s
  #                          AND timestamp < %s''', (
  #                dep_id, intervals[i][0], intervals[i+1][0]))
  #        (count,) = cur.fetchone()
  #        total += count
  #    Y.append(total)
  #
  #  pp.plot(X, Y)
  #  pp.title("Data rate quantized by variation")
  #  pp.xlabel("Variation")
  #  pp.ylabel("Number of pulses")
  #  pp.savefig('data_rate.png')
  #  pp.clf()


except mdb.Error, e:
  print >>sys.stderr, "misc: error: [%d] %s" % (e.args[0], e.args[1])
  sys.exit(1)

except qraat.error.QraatError, e:
  print >>sys.stderr, "misc: error: %s." % e

finally: 
  print >>sys.stderr, "misc: finished in %.2f seconds." % (time.time() - start)
