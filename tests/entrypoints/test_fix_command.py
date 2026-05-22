import pytest
from mock import Mock
from thefuck.entrypoints.fix_command import _get_raw_command, fix_command


class TestGetRawCommand(object):
    def test_from_force_command_argument(self):
        known_args = Mock(force_command='git brunch')
        assert _get_raw_command(known_args) == ['git brunch']

    def test_from_command_argument(self, os_environ):
        os_environ['TF_HISTORY'] = None
        known_args = Mock(force_command=None,
                          command=['sl'])
        assert _get_raw_command(known_args) == ['sl']

    @pytest.mark.parametrize('history, result', [
        ('git br', 'git br'),
        ('git br\nfcuk', 'git br'),
        ('git br\nfcuk\nls', 'ls'),
        ('git br\nfcuk\nls\nfuk', 'ls')])
    def test_from_history(self, os_environ, history, result):
        os_environ['TF_HISTORY'] = history
        known_args = Mock(force_command=None,
                          command=None)
        assert _get_raw_command(known_args) == [result]


def test_fix_command_exits_when_selected_command_run_fails(mocker):
    selected = Mock(run=Mock(return_value=False))
    mocker.patch('thefuck.entrypoints.fix_command.settings')
    mocker.patch('thefuck.entrypoints.fix_command._get_raw_command',
                 return_value=['echo ok'])
    mocker.patch('thefuck.types.Command.from_raw_script',
                 return_value=Mock())
    mocker.patch('thefuck.entrypoints.fix_command.get_corrected_commands',
                 return_value=[])
    mocker.patch('thefuck.entrypoints.fix_command.select_command',
                 return_value=selected)

    with pytest.raises(SystemExit) as excinfo:
        fix_command(Mock())

    assert excinfo.value.code == 1


def test_fix_command_uses_no_output_match_without_rerun(mocker):
    selected = Mock(run=Mock(return_value=True))
    command = Mock(read_output=Mock())
    mocker.patch('thefuck.entrypoints.fix_command.settings')
    mocker.patch('thefuck.entrypoints.fix_command._get_raw_command',
                 return_value=['git status'])
    from_raw_script = mocker.patch(
        'thefuck.types.Command.from_raw_script', return_value=command)
    mocker.patch('thefuck.entrypoints.fix_command.get_corrected_commands',
                 return_value=[selected])
    mocker.patch('thefuck.entrypoints.fix_command.select_command',
                 return_value=selected)

    fix_command(Mock())

    from_raw_script.assert_called_once_with(['git status'], read_output=False)
    assert not command.read_output.called


def test_fix_command_reads_output_when_no_output_rules_do_not_match(mocker):
    selected = Mock(run=Mock(return_value=True))
    command = Mock()
    command_with_output = Mock()
    command.read_output.return_value = command_with_output
    get_corrected_commands = mocker.patch(
        'thefuck.entrypoints.fix_command.get_corrected_commands',
        side_effect=[[], [selected]])
    mocker.patch('thefuck.entrypoints.fix_command.settings')
    mocker.patch('thefuck.entrypoints.fix_command._get_raw_command',
                 return_value=['git status'])
    mocker.patch('thefuck.types.Command.from_raw_script',
                 return_value=command)
    mocker.patch('thefuck.entrypoints.fix_command.select_command',
                 return_value=selected)

    fix_command(Mock())

    command.read_output.assert_called_once_with()
    assert get_corrected_commands.call_args_list[0][0][0] == command
    assert get_corrected_commands.call_args_list[1][0][0] == command_with_output
