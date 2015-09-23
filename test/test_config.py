import os
import yaml
import pytest
from indexfile.config import config

env = os.environ

with open('test/data/config.json') as js:
  test_config = yaml.load(js)


def test_update_config_dict():
  """Test set format with JSON string"""
  new_config = {
      "id_desc": "labExpId",
      "fileinfo": [
          "path",
          "size",
          "md5"
      ],
      "format": {
        "col_sep": "\t",
        "kw_sep": " ",
        "tag_sep": "=",
        "kw_trail": ";"
      }
  }
  config.update(new_config)
  assert config
  for k in new_config:
    if k == 'format':
      for j in new_config[k]:
        assert config[k][j] == new_config[k][j]
    else:
      assert config[k] == new_config[k]


def test_update_config_path():
  """Test set format with file path"""
  config.update('test/data/config.json')
  assert config
  for k in test_config:
    if k == 'format':
      for j in test_config[k]:
        assert config[k][j] == test_config[k][j]
    else:
      assert config[k] == test_config[k]


def test_update_config_file():
  """Test set format with file path"""
  fh = open('test/data/config.json', 'r')
  config.update(fh)
  assert config
  for k in test_config:
    if k == 'format':
      for j in test_config[k]:
        assert config[k][j] == test_config[k][j]
    else:
      assert config[k] == test_config[k]
