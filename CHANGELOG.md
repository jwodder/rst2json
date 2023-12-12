v0.5.1 (2023-12-12)
-------------------
- Drop support for Python 3.6
- Support Python 3.11
- Migrated from setuptools to hatch
- Declare the project unsupported going forwards

v0.5.0 (2022-01-26)
-------------------
- Support Python 3.10
- Update for Docutils 0.18.1, which is now the minimum required version

v0.4.0 (2021-06-06)
-------------------
- Added an `rst2json.core.get_docutils_config_files()` function for fetching
  the list of config files Docutils will read from based on the environment
- Support Python 3.9
- Updated test cases for Docutils 0.17 and pinned Docutils version in test
  environments to 0.17

v0.3.0 (2020-07-14)
-------------------
- **Breaking**: When not a string, the `format` argument to the `rst2json()`
  function must now be an instance of a writer class, not an actual class
- Added `content.document_classes` and `content.subtitle_classes` fields to
  output
- Added a `split_section_level` option for splitting the content body up by
  sections

v0.2.0.post1 (2020-07-11)
-------------------------
- Fix failing tests

v0.2.0 (2020-07-11)
-------------------
- Added a convenience function, `rst2json()`, for converting reStructuredText
  to JSON directly within Python
- Added information to the README on using the library's writer classes

v0.1.0 (2020-07-10)
-------------------
Initial release
