from pytest import raises


def test_reqs_invalid(reqs):
    with raises(ValueError):
        reqs('invalid')


def test_reqs_invalid_requirements(reqs):
    with raises(RuntimeError):
        reqs('invalid/invalid')


def test_reqs(reqs):
    assert reqs('changed').changed
    assert str(reqs('changed')) == reqs('changed', raw=True)
    assert reqs('new').changed
    assert str(reqs('new')) == reqs('new', raw=True)
    assert reqs('request_changed').changed
    assert str(reqs('request_changed')) == reqs('request_changed', raw=True)
    assert not reqs().changed
    assert str(reqs()) == reqs().locked


def test_reqs_lock(mocker, reqs):
    write_text = mocker.patch('pyorbs.reqs.Path.write_text')
    reqs().lock('test')
    assert write_text.called
