# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/en/1.0.0/)
and this project adheres to [Semantic Versioning](http://semver.org/spec/v2.0.0.html).

## [Unreleased]
- Nothing as of now.

## [1.0.0] - 2017-06-23
### Added
- Alert management support via the `Incident` model
- Alert models for some functionality for Alerts
- Version 2 Event support via the EventV2 model, the next major release will
  move the EventV2 model to the Event name and the current Event model will be
  moved to EventV1. Going forward new versioned models will follow this, but
  a minor release will happen for the new version and a major for the swapping.
- Added the `examples/incident_demo.py` file to show some more advanced usage
  of the package for those who want to see something work. This file will
  need to have access to a text file containing the API key for your account.
  See the code for more details.
- Alert model unit tests added with sample data.
- Incident method unit tests added with sample data.
- `set_api_key_from_file` added to the package to make it slightly easier to
  use file-based API keys. Do so at your own risk and please use appropriate
  permissions for your files.

### Changed
- The method signatures for Incident methods have been changed where the first
  argument for all the methods is now `from_email`. This is a non-compatible
  change that requires a major version increase. In general, trying to keep
  major version updates as sane as possible.


