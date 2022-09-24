#!/usr/bin/env python3
import os
import re
import sys
from pathlib import Path

from packaging.version import parse as parse_version

# taken verbatim from hatch/hatchling so the logic should match
DEFAULT_PATTERN = r'(?i)^(__version__|VERSION) *= *([\'"])v?(?P<version>.+?)\2'
GITHUB_REF = 'GITHUB_REF'


def main() -> int:
    version_path = Path(get_env('INPUT_VERSION_FILE_PATH'))
    if not version_path.is_file():
        raise RuntimeError(f'"{version_path}" is not a file')

    git_ref = get_env(GITHUB_REF)
    tag = re.sub('^refs/tags/', '', git_ref.lower())
    p_tag = parse_version(tag)

    version_pattern = os.getenv('INPUT_VERSION_PATTERN', DEFAULT_PATTERN)
    version_content = version_path.read_text()
    m = re.search(version_pattern, version_content, flags=re.M)
    if m is None:
        raise RuntimeError(
            f'version not found with regex {version_pattern!r} in {version_path}, content:\n{version_content}'
        )
    version = m.group('version')
    p_version = parse_version(version)
    if p_tag == p_version:
        is_prerelease = p_version.is_prerelease
        print(
            f'✓ {GITHUB_REF} environment variable {git_ref!r} matches package version: {version!r}, '
            f'is pre-release: {is_prerelease}'
        )
        print('(setting "IS_PRERELEASE" and "VERSION" environment variables for future use)')
        print(f'::set-output name=IS_PRERELEASE::{str(is_prerelease).lower()}')
        print(f'::set-output name=VERSION::{version}')
        return 0
    else:
        print(f'✖ {GITHUB_REF} environment variable {git_ref!r} does not match package version: {tag!r} != {version!r}')
        return 1


def get_env(name: str) -> str:
    version_path = os.getenv(name)
    if not version_path:
        raise RuntimeError(f'"{name}" environment variable not found')
    return version_path


if __name__ == '__main__':
    try:
        sys.exit(main())
    except RuntimeError as exc:
        print(f'✖ {exc}')
        sys.exit(2)
