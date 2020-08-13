from pathlib import Path
import re
import sys
import subprocess

import pytest

TOOL = Path(__file__).parent.parent / 'spec-merge-driver'

SCISSORS_RE = re.compile('-* 8< -*')

case_filenames = list(Path(__file__).parent.glob('cases/*'))


def run_driver(*argv):
    argv = [sys.executable, TOOL, *argv]
    subprocess.run(argv, check=True)


@pytest.mark.parametrize('case_filename', case_filenames)
def test_case(case_filename, tmp_path):
    source = Path(case_filename).read_text()
    base, main, new, expected = SCISSORS_RE.split(source)

    base_path = tmp_path / 'base'
    main_path = tmp_path / 'main'
    new_path = tmp_path / 'new'
    expected_path = tmp_path / 'new'

    base_path.write_text(base.strip())
    main_path.write_text(main.strip())
    new_path.write_text(new.strip())

    run_driver(base_path, main_path, new_path, '20', 'placeholder')

    result = main_path.read_text()

    assert result == expected.strip()
