import sys
import os
from .conf import settings
from .types import Rule
from .system import Path
from . import logs


_APP_PREFIXES = set([
    'adb', 'ag', 'apt', 'aws', 'az', 'brew', 'cargo', 'cat', 'cd',
    'choco', 'composer', 'conda', 'cp', 'dnf', 'docker', 'django',
    'fab', 'gem', 'git', 'go', 'gradle', 'grep', 'grunt', 'gulp',
    'heroku', 'hostscli', 'ifconfig', 'java', 'javac', 'lein', 'ln',
    'ls', 'man', 'mercurial', 'mkdir', 'mvn', 'nixos', 'npm',
    'omnienv', 'pacman', 'php', 'python', 'rails', 'rm', 'sed',
    'ssh', 'systemctl', 'terraform', 'tmux', 'tsuru', 'vagrant',
    'whois', 'workon', 'yarn', 'yum'
])

_REQUIRES_OUTPUT_CACHE = {}


def _rule_requires_output(rule_path):
    """Cheaply detects whether a rule can run before command output exists."""
    key = str(rule_path)
    if key not in _REQUIRES_OUTPUT_CACHE:
        try:
            with rule_path.open() as rule_file:
                source = rule_file.read()
        except OSError:
            _REQUIRES_OUTPUT_CACHE[key] = True
        else:
            _REQUIRES_OUTPUT_CACHE[key] = 'requires_output = False' not in source
    return _REQUIRES_OUTPUT_CACHE[key]


def _command_prefixes(command):
    if not command.script_parts:
        return None

    app = os.path.basename(command.script_parts[0]).lower()
    app = app.replace('-', '_')
    prefixes = set([app])

    if app in ('apt_get', 'apt_cache'):
        prefixes.add('apt')
    elif app in ('pip2', 'pip3'):
        prefixes.add('pip')
    elif app in ('python2', 'python3'):
        prefixes.add('python')
    elif app == 'gradlew':
        prefixes.add('gradle')

    return prefixes


def _rule_prefix(rule_name):
    return rule_name.split('_', 1)[0]


def _should_load_rule(rule_path, command=None):
    """Cheap rule prefilter based on filename and command application."""
    if command is None or rule_path.name == '__init__.py':
        return True

    rule_name = rule_path.name[:-3]
    if command.output is None and _rule_requires_output(rule_path):
        return False

    prefix = _rule_prefix(rule_name)
    if prefix not in _APP_PREFIXES:
        return True

    prefixes = _command_prefixes(command)
    return not prefixes or prefix in prefixes


def get_loaded_rules(rules_paths, command=None):
    """Yields all available rules.

    :type rules_paths: [Path]
    :rtype: Iterable[Rule]

    """
    for path in rules_paths:
        if path.name != '__init__.py' and _should_load_rule(path, command):
            rule = Rule.from_path(path)
            if rule and rule.is_enabled:
                yield rule


def get_rules_import_paths():
    """Yields all rules import paths.

    :rtype: Iterable[Path]

    """
    # Bundled rules:
    yield Path(__file__).parent.joinpath('rules')
    # Rules defined by user:
    yield settings.user_dir.joinpath('rules')
    # Packages with third-party rules:
    for path in sys.path:
        for contrib_module in Path(path).glob('thefuck_contrib_*'):
            contrib_rules = contrib_module.joinpath('rules')
            if contrib_rules.is_dir():
                yield contrib_rules


def get_rules(command=None):
    """Returns all enabled rules.

    :rtype: [Rule]

    """
    paths = [rule_path for path in get_rules_import_paths()
             for rule_path in sorted(path.glob('*.py'))]
    return sorted(get_loaded_rules(paths, command),
                  key=lambda rule: rule.priority)


def organize_commands(corrected_commands):
    """Yields sorted commands without duplicates.

    :type corrected_commands: Iterable[thefuck.types.CorrectedCommand]
    :rtype: Iterable[thefuck.types.CorrectedCommand]

    """
    try:
        first_command = next(corrected_commands)
        yield first_command
    except StopIteration:
        return

    without_duplicates = {
        command for command in sorted(
            corrected_commands, key=lambda command: command.priority)
        if command != first_command}

    sorted_commands = sorted(
        without_duplicates,
        key=lambda corrected_command: corrected_command.priority)

    logs.debug(u'Corrected commands: {}'.format(
        ', '.join(u'{}'.format(cmd) for cmd in [first_command] + sorted_commands)))

    for command in sorted_commands:
        yield command


def get_corrected_commands(command):
    """Returns generator with sorted and unique corrected commands.

    :type command: thefuck.types.Command
    :rtype: Iterable[thefuck.types.CorrectedCommand]

    """
    corrected_commands = (
        corrected for rule in get_rules(command)
        if rule.is_match(command)
        for corrected in rule.get_corrected_commands(command))
    return organize_commands(corrected_commands)
