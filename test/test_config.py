import yaml
from indexfile.config import config, set_index_format, set_config_defaults

with open('test/data/format.json') as js:
	test_format = yaml.load(js)


def test_set_format_dict():
	"""Test set format with JSON string"""
	new_format = {
	    "id": "labExpId",
	    "colsep": "\\t",
	    "fileinfo": [
	        "path",
	        "size",
	        "md5"
	    ],
	    "kw_sep": " ",
	    "sep": "=",
	    "trail": ";"
	}
	set_index_format(new_format)
	assert config.format
	for k in new_format:
		assert config.format[k] == new_format[k]


def test_set_format_path():
  """Test set format with file path"""
  set_index_format('test/data/format.json')
  assert config.format
  for k in test_format:
  	assert config.format[k] == test_format[k]


def test_set_format_file():
  """Test set format with file path"""
  fh = open('test/data/format.json', 'r')
  set_index_format('test/data/format.json')
  assert config.format
  for k in test_format:
  	assert config.format[k] == test_format[k]
    