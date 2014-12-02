import qraat, qraat.srv

db_con = qraat.srv.util.get_db('writer')

dep_id  = 105
cal_id  = 3
t_start = 1407448826
t_end   = 1407466793
t_delta = 5
t_window = 30 
t_chunk = 60 * 60 * 4

sv = qraat.srv.position.steering_vectors(db_con, cal_id)
center = qraat.srv.position.get_center(db_con)

chunks = []
ts = t_start
while (t_end - ts > t_chunk):
  chunks.append((ts, ts+t_chunk))
  ts += t_chunk
chunks.append((ts, t_end))

print "Running `const_high` time filter"
qraat.srv.signal.SCORE_ERROR = lambda(x) : 0.1255
(total, id) = qraat.srv.signal.Filter(db_con, dep_id, t_start, t_end)

# none 
print "Running `none`"
for i in range(len(chunks)):
  estimator = qraat.srv.position.estimator(dep_id, 
       chunks[i][0], chunks[i][1], t_window, t_delta)
  num_est = estimator.get_est_data(db_con, -99999)
  if num_est > 0:
    estimator.get_bearing_likelihood(sv)
    for new_estimator in estimator.windowed():
      new_estimator.insert_bearings(db_con, dep_id=10003)
      new_estimator.insert_positions(db_con, center, dep_id=10003)

# band
print "Running `band`"
for i in range(len(chunks)):
  estimator = qraat.srv.position.estimator(dep_id, 
       chunks[i][0], chunks[i][1], t_window, t_delta)
  num_est = estimator.get_est_data(db_con, -0.00001)
  if num_est > 0:
    estimator.get_bearing_likelihood(sv)
    for new_estimator in estimator.windowed():
      new_estimator.insert_bearings(db_con, dep_id=10001)
      new_estimator.insert_positions(db_con, center, dep_id=10001)

# const_high
print "Running `const_high`"
for i in range(len(chunks)):
  estimator = qraat.srv.position.estimator(dep_id, 
       chunks[i][0], chunks[i][1], t_window, t_delta)
  num_est = estimator.get_est_data(db_con, 0.2)
  if num_est > 0:
    estimator.get_bearing_likelihood(sv)
    for new_estimator in estimator.windowed():
      new_estimator.insert_bearings(db_con, dep_id=10004)
      new_estimator.insert_positions(db_con, center, dep_id=10004)

# hyper
print "Running `hyper` time filter"
qraat.srv.signal.SCORE_ERROR = lambda(x) : (-0.6324 / (x + 7.7640)) + 0.1255
(total, id) = qraat.srv.signal.Filter(db_con, dep_id, t_start, t_end)
print "Running `hyper`"
for i in range(len(chunks)):
  estimator = qraat.srv.position.estimator(dep_id, 
       chunks[i][0], chunks[i][1], t_window, t_delta)
  num_est = estimator.get_est_data(db_con, 0.2)
  if num_est > 0:
    estimator.get_bearing_likelihood(sv)
    for new_estimator in estimator.windowed():
      new_estimator.insert_bearings(db_con, dep_id=10000)
      new_estimator.insert_positions(db_con, center, dep_id=10000)

# const_low
print "Running `const_low` time filter"
qraat.srv.signal.SCORE_ERROR = lambda(x) : 0.02
(total, id) = qraat.srv.signal.Filter(db_con, dep_id, t_start, t_end)
print "Running `const_low`"
for i in range(len(chunks)):
  estimator = qraat.srv.position.estimator(dep_id, 
       chunks[i][0], chunks[i][1], t_window, t_delta)
  num_est = estimator.get_est_data(db_con, 0.2)
  if num_est > 0:
    estimator.get_bearing_likelihood(sv)
    for new_estimator in estimator.windowed():
      new_estimator.insert_bearings(db_con, dep_id=10002)
      new_estimator.insert_positions(db_con, center, dep_id=10002)
