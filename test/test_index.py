import os
import pytest
from indexfile.index import *

def test_replicates():
    i = Index('test/data/index.txt')
    i.set_format('test/data/format.json')
    i.open()
    reps = i.find_replicates(id="EWP.1,EWP.2")
    d = reps[0]
    others = reps[1:]
    m = d.merge(others)
    for k in m._metadata.keys():
        vals = [d._metadata[k] for d in reps]
        if len(set(vals)) > 1:
            if k == 'id':
                vals = ','.join(vals)
            assert m._metadata[k] == vals
        else:
            assert m._metadata[k] == vals[0]

def test_replicates_w_metadata():
    i = Index('test/data/index.txt')
    i.set_format('test/data/format.json')
    i.open()
    i.insert(id='aWL3.1,aWL3.2', path='test/data/format.json', type='json', view='json')
    i.select(id='aWL3.1,aWL3.2')
    i.remove(path='test/data/format.json', clear=True)
