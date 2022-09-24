#!/usr/bin/env python3
import os
import re
import sys
from pathlib import Path

from packaging.version import Version

# taken verbatim from hatch/hatchling so the logic should match
DEFAULT_PATTERN = r'(?i)^(__version__|VERSION) *= *([\'"])v?(?P<version>.+?)\2'


def main() -> int:
    version_path = Path(get_env('INPUT_VERSION_FILE_PATH'))
    if not version_path.is_file():
        raise RuntimeError(f'"{version_path}" is not a file')

    github_ref_env_var = os.getenv('GH_REF_ENV_VAR') or 'GITHUB_REF'
    github_ref = get_env(github_ref_env_var)
    tag_str = re.sub('^refs/tags/', '', github_ref.lower())
    try:
        tag = Version(tag_str)
    except ValueError as e:
        raise RuntimeError(f'{github_ref_env_var}, {e}')

    version_pattern = os.getenv('INPUT_VERSION_PATTERN') or DEFAULT_PATTERN
    version_content = version_path.read_text()
    m = re.search(version_pattern, version_content, flags=re.M)
    if m is None:
        raise RuntimeError(
            f'version not found with regex {version_pattern!r} in {version_path}, content:\n{version_content}'
        )
    try:
        file_version_str = m.group('version')
    except IndexError:
        raise RuntimeError(f'Group "version" not found in with regex {version_pattern!r}')

    try:
        file_version = Version(file_version_str)
    except ValueError as e:
        raise RuntimeError(f'{version_path}, {e}')
    print(f'{github_ref_env_var} environment variable version: "{github_ref}"')
    print(f'"{version_path}" version: "{file_version_str}"\n')
    if tag == file_version:
        is_prerelease = str(file_version.is_prerelease).lower()
        print(f'✓ versions match, is pre-release: {is_prerelease}, pretty version: "{file_version}"')
        print('(setting "IS_PRERELEASE" and "VERSION" environment variables for future use)')
        print(f'::set-output name=IS_PRERELEASE::{is_prerelease}')
        print(f'::set-output name=VERSION::{file_version}')
        return 0
    else:
        print(f'✖ versions do not match, "{tag}" != "{file_version}"')
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
