import pickle
import dill
import shelve
import jsonpickle
import pandas as pd
from pickle import loads as decode

# ruleid: B301
pickle.loads(data)
# ruleid: B301
decode(data)
# ruleid: B301
pickle.load(stream)
# ruleid: B301
pickle.Unpickler(stream)
# ruleid: B301
dill.loads(data)
# ruleid: B301
shelve.open("db")
# ruleid: B301
jsonpickle.decode(data)
# ruleid: B301
pd.read_pickle("db")
# ok: B301
pickle.dumps(data)
# ok: B301
other.loads(data)
# ruleid: B301
dill.load(stream)
# ruleid: B301
dill.Unpickler(stream)
# ruleid: B301
shelve.DbfilenameShelf("db")
# ruleid: B301
jsonpickle.unpickler.decode(data)
# ruleid: B301
jsonpickle.unpickler.Unpickler()
# ok: B301
pickle.loads(data)  # nosec B301
# ruleid: B301
pickle.loads(data)  # nosec B307
# ruleid: B301
pickle.loads("#nosec")
