import os
import pytest
from indexfile.index import *

def test_create_dataset():
    info = {'labExpId': '1', 'sex':'M', 'age':'65'}
    dataset = Dataset(info)
    print str(dataset)
