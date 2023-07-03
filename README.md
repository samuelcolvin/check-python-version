# Check Python Version

[![CI](https://github.com/samuelcolvin/check-python-version/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/samuelcolvin/check-python-version/actions/workflows/ci.yml)

Check the release tag matches the library version before deploy.

This is designed to be used in deploy jobs to check that GitHub release tag matches the version in your code.

The following output variables are set by the action for use in later steps:
* `IS_PRERELEASE`, either `'true'` or `'false'` whether the version is a pre-release, 
  uses [`packing.Version.is_prerelease`](https://packaging.pypa.io/en/latest/version.html#usage)
* `VERSION`, which is the "pretty" version string, 
  using [`str(packing.Version)`](https://packaging.pypa.io/en/latest/version.html#usage)
* `VERSION_MAJOR_MINOR`, major and minor version numbers, e.g. `1.2.3` would output `1.2`

See usage below for an example of how to access these values.

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
* **`test_github_ref`**: Version to check, defaults to using `GITHUB_REF` - this is mostly for testing
* **`skip_env_check`**: Set to "true" to skip environment variable (e.g. `GITHUB_REF`, or `input.test_github_ref`) 
  check, mostly useful when you want to use outputs in later steps
