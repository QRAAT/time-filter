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

  variation_step = 0.1
  X = np.arange(0, 4, variation_step)
  Y = []
  Y_noise = []
  
  cur.execute('''SELECT timestamp, pulse_interval, pulse_variation, duration
                   FROM estinterval
                  WHERE deploymentID = %s 
                    AND timestamp >= %s
                    AND timestamp <= %s
                  ORDER BY timestamp''', (dep_id, t_start, t_end))

  intervals = list(cur.fetchall())
  
  for variation in X:
    total = 0
    total_noise = 0
    theoretical_total = 0
    num_windows = 0
    for i in range(len(intervals)-1):
      if variation <= intervals[i][2] and intervals[i][2] < variation + variation_step:
        cur.execute('''SELECT id FROM est
                        WHERE deploymentID = %s 
                          AND timestamp >= %s
                          AND timestamp < %s''', (
                dep_id, intervals[i][0], intervals[i+1][0]))
        est_ids = map(lambda(row) : row[0], cur.fetchall())
        theoretical_count = intervals[i][3] / (intervals[i][1] * 5)
        theoretical_total += theoretical_count
        total += len(est_ids)
        total_noise += len(filter(lambda(id) : good.get(id) != True, est_ids))
        num_windows += 1
    Y.append(0 if num_windows == 0 else total / (num_windows * theoretical_count))
    Y_noise.append(0 if num_windows == 0 else total_noise / (num_windows *theoretical_count))
  
  Y = np.array(Y)
  Y_noise = np.array(Y_noise)

  pp.plot(X, Y)
  pp.plot(X, Y_noise, 'r')
  pp.plot(X, Y_noise, 'r')
  pp.plot(X, Y - Y_noise, 'g')
  pp.legend(["Data", "Noise"])
  pp.title("Data rate quantized by variation")
  pp.xlabel("Variation")
  pp.ylabel("Number of pulses / number of possible pulses")
  pp.savefig('data_rate.png')
  pp.clf()


except mdb.Error, e:
  print >>sys.stderr, "misc: error: [%d] %s" % (e.args[0], e.args[1])
  sys.exit(1)

except qraat.error.QraatError, e:
  print >>sys.stderr, "misc: error: %s." % e

finally: 
  print >>sys.stderr, "misc: finished in %.2f seconds." % (time.time() - start)
