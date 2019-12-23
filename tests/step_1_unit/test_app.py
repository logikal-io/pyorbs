from pyorbs.app import main


def test_keyboard_interrupt(mocker):
    mocker.patch('pyorbs.orbs.Orbs.list', side_effect=KeyboardInterrupt)
    assert main(args=['-l']) == 1
