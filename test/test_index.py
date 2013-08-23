import os
import pytest
from indexfile.index import *

def test_create_empty_dataset():
    dataset = Dataset()

def test_create_dataset():
    info = {'labExpId': '1', 'sex':'M', 'age':'65', 'readType':'2x76'}
    dataset = Dataset(**info)
    assert dataset.id == '1'
    assert dataset.sex == 'M'
    assert dataset.age == '65'
