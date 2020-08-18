"""Test the integration test cases

Each case file in the cases/ directory has these sections,
separated by scissor lines:

- "OK" or "FAIL", the expected return code
- The BASE file contents, or merged ancestors
- The MAIN file contents
- The NEW file contents
- The expected result (with conflict markers, if the merge should fail)
"""
from pathlib import Path
import re
import sys
import subprocess

import pytest

TOOL = Path(__file__).parent.parent / 'rpm-spec-merge-driver'

SCISSORS_RE = re.compile('-* 8< -*')

CASES_PATH = Path(__file__).parent / 'cases'

case_filenames = sorted(CASES_PATH.glob('*'))


def run(*argv, **kwargs):
    print(argv, file=sys.stderr)
    kwargs.setdefault('check', True)
    env = kwargs.setdefault('env', {})
    env.setdefault('GIT_AUTHOR_DATE', '2020-08-13 12:34')
    env.setdefault('GIT_CONFIG_NOSYSTEM', '1')
    env.setdefault('HOME', CASES_PATH)
    env.setdefault('XDG_CONFIG_HOME', CASES_PATH)
    return subprocess.run(argv, **kwargs)


@pytest.mark.parametrize(
    'case_filename', (str(p.relative_to(CASES_PATH)) for p in case_filenames),
)
def test_case(case_filename, tmp_path):
    source = CASES_PATH.joinpath(case_filename).read_text()
    ok, base, main, new, expected = SCISSORS_RE.split(source)

    repo_path = tmp_path / 'repo'
    repo_path.mkdir()

    file_path = repo_path / 'test.spec'
    attrs_path = repo_path / '.gitattributes'

    run('git', 'init', cwd=repo_path)

    run('git', 'config', 'merge.rpm-spec.name', 'RPM spec file merge driver', cwd=repo_path)
    run('git', 'config', 'merge.rpm-spec.driver', f'{TOOL} %O %A %B %L %P', cwd=repo_path)
    run('git', 'config', 'merge.rpm-spec.recursive', 'text', cwd=repo_path)
    run('git', 'config', 'merge.verbosity', '5', cwd=repo_path)
    run('git', 'config', 'merge.conflictStyle', 'diff3', cwd=repo_path)
    run('git', 'config', 'user.name', 'Merge Driver 💁', cwd=repo_path)
    run('git', 'config', 'user.email', 'merger@example.org', cwd=repo_path)
    run('cat', '.git/config', cwd=repo_path)

    attrs_path.write_text('*.spec  merge=rpm-spec\n')
    file_path.write_text(base.strip())
    run('git', 'add', '.gitattributes', 'test.spec', cwd=repo_path)
    run('git', 'commit', '-m', 'Base', cwd=repo_path)

    run('git', 'branch', 'base', cwd=repo_path)

    run('git', 'switch', '-c', 'new', 'base', cwd=repo_path)
    file_path.write_text(new.strip())
    run('git', 'commit', '-m', 'New', 'test.spec', cwd=repo_path)

    run('git', 'switch', '-c', 'main', 'base', cwd=repo_path)
    file_path.write_text(main.strip())
    run('git', 'commit', '-m', 'Main', 'test.spec', cwd=repo_path)

    proc = run('git', 'merge', 'new', cwd=repo_path, check=False)

    result = file_path.read_text()

    assert result == expected.strip()
    if ok.strip() == 'OK':
        assert proc.returncode == 0
    else:
        assert proc.returncode != 0
