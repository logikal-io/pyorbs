import subprocess
import shutil


def test_build():
    shutil.rmtree('dist', ignore_errors=True)
    assert subprocess.run(['./setup.py', 'sdist', 'bdist_wheel']).returncode == 0
    assert subprocess.run(['twine', 'check', 'dist/*']).returncode == 0
