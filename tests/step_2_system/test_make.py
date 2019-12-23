import subprocess


def test_dist():
    subprocess.run(['make', 'dist'], check=True)
    subprocess.run(['make', 'clean_dist'], check=True)


def test_docs():
    subprocess.run(['make', 'docs'], check=True)
