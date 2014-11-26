# Compute the variance of position blobs corresponding to fixed transmitters. 
# Do iterative outlier elimination to remove biased positions. NOTE this 
# script doesn't take time range into account. 

import qraat, qraat.srv
import numpy as np

def get_positions(db_con, dep_id):
  cur = db_con.cursor()
  ct = cur.execute('''SELECT timestamp, easting, northing, ID
                        FROM qraat.position 
                       WHERE deploymentID=%s''', (dep_id,))

  P = np.zeros(ct, dtype=np.complex128)
  T = np.zeros(ct, dtype=np.float64)
  pos_ids = np.zeros(ct, dtype=np.int64)
  for (i, (t, easting, northing, pos_id)) in enumerate(cur.fetchall()):
    P[i] = np.complex(northing, easting)
    T[i] = t
    pos_ids[i] = pos_id
  
  return (P, T, pos_ids)


def set_tracks(db_con, dep_id, pos_ids, T):
  cur = db_con.cursor()
  cur.execute('''DELETE FROM qraat.track_pos
                  WHERE deploymentId=%s''', (dep_id,))
  
  for i in range(len(pos_ids)):
    cur.execute('''INSERT INTO qraat.track_pos 
                     (positionID, deploymentID, timestamp) 
                    VALUE (%s, %s, %s)''', (pos_ids[i], dep_id, T[i]))


# main  

dep_id=10004
db_con = qraat.srv.util.get_db('writer')
(P, T, pos_ids) = get_positions(db_con, dep_id)

# Iterated outlier elimination
ct = 0
while ct < 15:
  mean = np.mean(P)
  std = np.std(P)
  print "%-3d" % (ct+1), "mean:", mean, "std: %2.4f" % std, "total:", len(P)
  mask = np.abs(P - mean) <= 2 * std
  P = P[mask] 
  T = T[mask]
  pos_ids = pos_ids[mask]
  ct += 1

print "Variance: %.4f" % np.var(P)

# Display remaining positions as tracks in GUI. 
set_tracks(db_con, dep_id, pos_ids, T) 


