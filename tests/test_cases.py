from pathlib import Path
import re
import sys
import subprocess

import pytest

TOOL = Path(__file__).parent.parent / 'spec-merge-driver'

SCISSORS_RE = re.compile('-* 8< -*')

CASES_PATH = Path(__file__).parent / 'cases'

# Filenames as string (so they
case_filenames = sorted(CASES_PATH.glob('*'))


def run_driver(*argv, **kwargs):
    argv = [sys.executable, TOOL, *argv]
    env = kwargs.setdefault('env', {})
    env.setdefault('GIT_AUTHOR_NAME', 'Merge Driver User')
    env.setdefault('GIT_AUTHOR_EMAIL', 'merger@example.org')
    env.setdefault('GIT_AUTHOR_DATE', '2020-08-13 12:34')
    return subprocess.run(argv, **kwargs)


@pytest.mark.parametrize(
    'case_filename', (str(p.relative_to(CASES_PATH)) for p in case_filenames),
)
def test_case(case_filename, tmp_path):
    source = CASES_PATH.joinpath(case_filename).read_text()
    ok, base, main, new, expected = SCISSORS_RE.split(source)

    ok = ok.strip()

    base_path = tmp_path / 'base'
    main_path = tmp_path / 'main'
    new_path = tmp_path / 'new'
    expected_path = tmp_path / 'new'

    base_path.write_text(base.strip())
    main_path.write_text(main.strip())
    new_path.write_text(new.strip())

    proc = run_driver(base_path, main_path, new_path, '20', 'placeholder')

    result = main_path.read_text()

    assert result == expected.strip()
    if ok == 'OK':
        assert proc.returncode == 0
    else:
        assert proc.returncode != 0
