Changelog
=========

Version 0.12.0:
    - Re-add support for IDX_FILE and IDX_FORMAT environment variables. Close #12 (`view commit <http://github.com/emi80/idxtools/commit/870b820e21f34ff58763e415690d914b65d6c176)>`_
    - Update _load_index. Load first regular dataset entries, then replicates entries to avoid missing ids. Fixes #13 (`view commit <http://github.com/emi80/idxtools/commit/369ecdeab4f7169f2ec62e345c954452f72cddab)>`_
    - Fix issue adding file to existing dataset (`view commit <http://github.com/emi80/idxtools/commit/ad5465a2ee5052a5962cb8f9bf57985f0a21ba54)>`_
    - Update command line parsing. Use Schema for validation. (`view commit <http://github.com/emi80/idxtools/commit/a507a0ef3b3e55f89014e0db1add74b0c603b370)>`_
    - Finish command line improvement and add tests. Closes #16 (`view commit <http://github.com/emi80/idxtools/commit/64a1630bc40e99b45f7753802469f78bd953ae0b)>`_
    - Implement multiple files insertion from command line and add test. Closes #15 (`view commit <http://github.com/emi80/idxtools/commit/d0b71f6e91a8bda14352d8338c46148a9c98d665)>`_
    - Update config file name and set global constants for default values (`view commit <http://github.com/emi80/idxtools/commit/53137cb76acb4c1db337d10b2cbb48bd6f8ba1d0)>`_
    - 'show' command: Support 'attrs' keyword for '--tags' option to only print attribute names (`view commit <http://github.com/emi80/idxtools/commit/a60c4ee50ed4635b9411cbf89221196356d07b6a)>`_
    - Allow deletion of files based on metadata (`view commit <http://github.com/emi80/idxtools/commit/cae1d67c11fa458a644ccf0869d9271b53e85cfd)>`_
    - Add template formatting for path (`view commit <http://github.com/emi80/idxtools/commit/ea6df9fa4356aa0ee2f44ed264424473fa225be9)>`_
    - Implement dynamic command resolution and update help messages and usages (`view commit <http://github.com/emi80/idxtools/commit/c0d5500eda5b3e3da5607c13624b3413a53ad902)>`_
    - Use type attribute as optional when importing files from metadata in tsv/csv format. Autodetect type from path extension if not given. (`view commit <http://github.com/emi80/idxtools/commit/8839d16b1bd996608b30285df7ff0d007a59176d)>`_
    - Test for non-empty path while inserting files (`view commit <http://github.com/emi80/idxtools/commit/83c843c7ea09c1da4e8b1b485a11606c1f569d33)>`_
    - Add ability to load format from YAML too (`view commit <http://github.com/emi80/idxtools/commit/870b322b5dfc7b18688f417083ff43ad76c912d0)>`_
    - Automatically add header fields to format map when importing data from tsv/csv files (`view commit <http://github.com/emi80/idxtools/commit/22902fec0fd0ea69a94f351b43ecf27ed42a85ac)>`_
    - Always flush output buffer to avoid 'sys.excepthook is missing' error (`view commit <http://github.com/emi80/idxtools/commit/adb6030b41dbf5aa0cf13c812e3f2de174217bee)>`_
    - Rename 'add' command file to 'update'. (`view commit <http://github.com/emi80/idxtools/commit/a9eaccbb9621a05e386f6c2dcb4ded12f26e30c4)>`_
    - Finalize implementation of 'update' command. Keep 'add' as command alias for backward compatibility (`view commit <http://github.com/emi80/idxtools/commit/71e4b26019f5c0f75d292cdd6376bd655471b274)>`_
    - Sort by tags order in table output or by path (`view commit <http://github.com/emi80/idxtools/commit/af05ad11c400a4be4ff6495a7ffc162b71d5bdb0)>`_

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
