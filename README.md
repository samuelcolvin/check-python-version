# Check Python Version

[![CI](https://github.com/samuelcolvin/check-python-version/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/samuelcolvin/check-python-version/actions/workflows/ci.yml)

Check the release tag matches the library version before deploy.

This is designed to be used in deploy jobs to check that GitHub release tag matches the version in your code.

## Usage

A minimal example:

```yaml

jobs:
  deploy:
    steps:
      - ...
      - uses: samuelcolvin/check-python-version@v1
        id: check-python-version
        with:
          version_file_path: mypackage/version.py

      - run: ...

      # optionally you can use the environment variables set by the action later
      - name: publish docs
        if: '!fromJSON(steps.check-python-version.outputs.IS_PRERELEASE)'
        uses: ...
```

### Inputs

* **`version_file_path`**: Path to python file containing the version number string (**required**)
* **`version_pattern`**: Custom regular expression to find version with,
  defaults to `(?i)^(__version__|VERSION) *= *([\'"])v?(?P<version>.+?)\2` 
  (which matches [hatchling](https://hatch.pypa.io/latest/plugins/build-hook/version/))
