Changelog
=========

Version 0.11.0:
    - Fix bug: remove fileinfo from output
    - Refactor Dataset get method
    - Add config files support in command line tools
    - Improve arguments passing and index loading in command line tools

Version 0.10.0:
    - Improve index file lookup
    - Change some APIs
    - Use stdin when data is piped instead of IDX_FILE (`#9 <https://github.com/emi80/idxtools/issues/9>`_)
    - Implement removal of all files of a given type from a dataset (`#11 <https://github.com/emi80/idxtools/issues/11>`_)

Version 0.9.1:
    - Detect replicate id and create metadata for replicates (`#3 <https://github.com/emi80/idxtools/issues/3>`_)
    - Add support to remove whole dataset to the remove command (`#8 <https://github.com/emi80/idxtools/issues/8>`_)

Version 0.9:
    - Add option to remove command to clear metadata and modify cli to remove multiple files (`#1 <https://github.com/emi80/idxtools/issues/1>`_ and `#2 <https://github.com/emi80/idxtools/issues/2>`_)
    - Update show command to support ids for replicates (`#5 <https://github.com/emi80/idxtools/issues/5>`_)
    - Use logging module (`#6 https://github.com/emi80/idxtools/issues/6`_)
    - Update signal handler for SIGPIPE (`#7 https://github.com/emi80/idxtools/issues/7`_)

Version 0.9b1:
    - Initial release
