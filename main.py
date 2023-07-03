#!/usr/bin/env python3
import os
import re
import sys
from pathlib import Path

from packaging.version import Version

# taken verbatim from hatch/hatchling so the logic should match
DEFAULT_PATTERN = r'(?i)^(__version__|VERSION) *= *([\'"])v?(?P<version>.+?)\2'


def main() -> int:
    version_path = get_version_path()

    file_version = get_file_version(version_path)

    env_tag = get_env_version()

    if env_tag is None:
        return set_outputs('environment variable check skipped', file_version)
    elif env_tag == file_version:
        return set_outputs('✓ versions match', file_version)
    else:
        print(f'✖ versions do not match, "{env_tag}" != "{file_version}"')
        return 1


def get_version_path() -> Path:
    version_path = Path(get_env('INPUT_VERSION_FILE_PATH')[0])
    if version_path.is_file():
        return version_path
    else:
        raise RuntimeError(f'"{version_path}" is not a file')


def get_env_version() -> Version | None:
    """
    Get the version from the environment variable INPUT_TEST_GITHUB_REF or GITHUB_REF

    :return: the version or None if `skip_env_check=true`
    """
    skip_env_check_str = os.getenv('INPUT_SKIP_ENV_CHECK') or ''
    skip_env_check = skip_env_check_str.lower() in ('1', 'true')

    if skip_env_check:
        return None
    else:
        # INPUT_TEST_GITHUB_REF comes first so we can test with it even when GITHUB_REF is set
        github_ref, github_ref_env_var = get_env('INPUT_TEST_GITHUB_REF', 'GITHUB_REF')
        tag_str = re.sub('^refs/tags/', '', github_ref.lower())
        try:
            tag = Version(tag_str)
        except ValueError as e:
            raise RuntimeError(f'{github_ref_env_var}, {e}')
        print(f'{github_ref_env_var} environment variable version: "{github_ref}"')
        return tag


def get_file_version(version_path: Path) -> Version:
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
    else:
        print(f'"{version_path}" version: "{file_version_str}"\n')
        return file_version


def set_outputs(prefix: str, file_version: Version) -> int:
    is_prerelease = str(file_version.is_prerelease).lower()
    version_major_minor = f'{file_version.major}.{file_version.minor}'
    print(
        f'{prefix}, '
        f'is pre-release: {is_prerelease}, '
        f'pretty version: "{file_version}", '
        f'major.minor: "{version_major_minor}"'
    )

    github_output = os.getenv('ALT_GITHUB_OUTPUT') or os.getenv('GITHUB_OUTPUT')
    if github_output:
        print('Setting "IS_PRERELEASE" and "VERSION" environment variables for future use')
        with open(github_output, 'a') as f:
            f.write(f'IS_PRERELEASE={is_prerelease}\n')
            f.write(f'VERSION="{file_version}"\n')
            f.write(f'VERSION_MAJOR_MINOR="{version_major_minor}"\n')
    else:
        print(f'Warning: GITHUB_OUTPUT not set, cannot set environment variables')
    return 0


def get_env(*names: str) -> tuple[str, str]:
    for name in names:
        value = os.getenv(name)
        if value:
            return value, name
    names_str = ', '.join(f'"{name}"' for name in names)
    plural = '' if len(names) == 1 else 's'
    raise RuntimeError(f'{names_str} environment variable{plural} not found')


if __name__ == '__main__':
    try:
        sys.exit(main())
    except RuntimeError as exc:
        print(f'✖ {exc}')
        sys.exit(2)
