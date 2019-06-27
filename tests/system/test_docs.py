import subprocess
import shutil


def test_docs():
    shutil.rmtree('docs/_build', ignore_errors=True)
    assert subprocess.run('make', cwd='docs').returncode == 0
