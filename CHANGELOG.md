v0.4.0 (in development)
-----------------------
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
