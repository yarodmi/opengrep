import pickle
import pickle as p
from pickle import loads as lp
import dill
import shelve
import jsonpickle
import pandas as pd
import _pickle
import cPickle


def deserialize(data, stream):
    # ruleid: B301
    pickle.loads(data)
    # ruleid: B301
    pickle.loads("literal data")
    # ruleid: B301
    p.load(stream)
    # ruleid: B301
    lp(data)
    # ruleid: B301
    pickle.Unpickler(stream).load()
    # ruleid: B301
    dill.loads(data)
    # ruleid: B301
    dill.load(stream)
    # ruleid: B301
    dill.Unpickler(stream).load()
    # ruleid: B301
    shelve.open("database")
    # ruleid: B301
    shelve.DbfilenameShelf("database")
    # ruleid: B301
    jsonpickle.decode(data)
    # ruleid: B301
    jsonpickle.unpickler.decode(data)
    # ruleid: B301
    jsonpickle.unpickler.Unpickler().restore(data)
    # ruleid: B301
    pd.read_pickle(stream)
    # ok: B301
    pickle.dumps(data)
    # ok: B301
    pickle.dump(data, stream)
    # ok: B301
    dill.dumps(data)
    # ok: B301
    dill.dump(data, stream)
    # ok: B301
    jsonpickle.encode(data)
    # These module names are not in Bandit 1.9.4's default call blacklist.
    # ok: B301
    _pickle.loads(data)
    # ok: B301
    cPickle.loads(data)
    # ok: B301
    pickle.loads(data)  # nosec
    # ok: B301
    pickle.loads(data)  # nosec B301
    # ruleid: B301
    pickle.loads(data)  # nosec B506
