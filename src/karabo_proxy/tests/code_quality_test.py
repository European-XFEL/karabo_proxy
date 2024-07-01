import os
import os.path as op
import subprocess
from typing import List

import karabo_proxy

IGNORE_LIST = ['setup.py', '__init__.py']


def get_python_files() -> List[str]:
    """Get all python files from this package
    """
    common_dir = op.abspath(op.dirname(karabo_proxy.__file__))
    flake_check = []
    for dirpath, _, filenames in os.walk(common_dir):
        for fn in filenames:
            if op.splitext(fn)[-1].lower() == '.py' and fn not in IGNORE_LIST:
                path = op.join(dirpath, fn)
                flake_check.append(path)

    return flake_check


def test_code_quality_flake8():
    files = get_python_files()
    command = ['flake8', *[op.abspath(py_file) for py_file in files]]
    subprocess.check_call(command)
