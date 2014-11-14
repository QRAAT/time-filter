import qraat, qraat.srv
import MySQLdb as mdb
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as pp
import os, sys, time
import pickle

dep_id  = 105
site_id = 8
t_start = 1410721127.0
t_end   = 1410807696.0

try: 
  start = time.time()
  print >>sys.stderr, "misc: start time:", time.asctime(time.localtime(start))

  db_con = qraat.srv.util.get_db('writer')
  cur = db_con.cursor()
 
  points = qraat.csv.csv('partition.csv')
  good = {} 
  for p in points: 
    good[int(p.est_id)] = True if int(p.good) is 1 else False

  # Remove bad points.
  for (id, is_good) in good.iteritems():
    if not is_good: 
      cur.execute('DELETE FROM est WHERE id=%s', (id,))
  
  # Add uniform random noise. 
  N = 2500
  U = np.random.uniform(t_start, t_end, N)
  for t in list(U):
    cur.execute('''INSERT INTO est (deploymentID, siteID, timestamp, band3, band10, edsp) 
                       VALUE (%s, %s, %s, %s, %s, %s)''', 
                            (dep_id, site_id, t, 0, 0, np.random.uniform(0,1,1)[0]))


except mdb.Error, e:
  print >>sys.stderr, "misc: error: [%d] %s" % (e.args[0], e.args[1])
  sys.exit(1)

except qraat.error.QraatError, e:
  print >>sys.stderr, "misc: error: %s." % e

finally: 
  print >>sys.stderr, "misc: finished in %.2f seconds." % (time.time() - start)
