# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [v2] - 2023-05-19

### Added
- Added `limit` parameter to `searchPapersRequest` schema in OpenAPI specification. The parameter is optional and defaults to 10. It allows users to limit the number of papers returned by the `search_arxiv` function.
- Implemented `limit` parameter in `search_papers` function in `main.py`. The function now accepts an optional `limit` parameter in the request data and uses it to limit the number of papers returned by the `arxiv.Search` function.
- Added tests for `limit` parameter in `search_papers` function in `test_main.py`. The tests check that the function correctly limits the number of papers returned when the `limit` parameter is provided and defaults to returning 10 papers when no `limit` parameter is provided.

## [v1] - 2023-05-16

### Added
- Initial release of the Arxiv ChatGPT Plugin.
