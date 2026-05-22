"""Package with shell specific actions, each shell class should
implement `from_shell`, `to_shell`, `app_alias`, `put_to_history` and
`get_aliases` methods.
"""
import os
from psutil import Process
from .generic import Generic
from .zsh import Zsh

# The optimized runtime path is intentionally zsh-only.  The legacy shell
# classes remain importable for compatibility/tests, but automatic detection
# only selects zsh; all other shells fall back to Generic.
shells = {'zsh': Zsh}


def __getattr__(name):
    """Lazily expose legacy shell classes without loading them at startup."""
    if name == 'Bash':
        from .bash import Bash
        return Bash
    elif name == 'Fish':
        from .fish import Fish
        return Fish
    elif name == 'Tcsh':
        from .tcsh import Tcsh
        return Tcsh
    elif name == 'Powershell':
        from .powershell import Powershell
        return Powershell
    raise AttributeError(name)


def _get_shell_from_env():
    name = os.environ.get('TF_SHELL')

    if name in shells:
        return shells[name]()


def _get_shell_from_proc():
    proc = Process(os.getpid())

    while proc is not None and proc.pid > 0:
        try:
            name = proc.name()
        except TypeError:
            name = proc.name

        name = os.path.splitext(name)[0]

        if name in shells:
            return shells[name]()

        try:
            proc = proc.parent()
        except TypeError:
            proc = proc.parent

    return Generic()


shell = _get_shell_from_env() or _get_shell_from_proc()
