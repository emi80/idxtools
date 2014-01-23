import os
import pytest
from indexfile.index import *

def test_create_empty_dataset():
    dataset = Dataset()

def test_create_dataset():
    info = {'id': '1', 'sex':'M', 'age':'65'}
    dataset = Dataset(**info)
    assert dataset.id == '1'
    assert dataset.sex == 'M'
    assert dataset.age == '65'

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
