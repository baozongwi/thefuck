"""Package with shell specific actions, each shell class should
implement `from_shell`, `to_shell`, `app_alias`, `put_to_history` and
`get_aliases` methods.
"""
import os
from psutil import Process
from .bash import Bash  # noqa: F401
from .fish import Fish  # noqa: F401
from .generic import Generic
from .tcsh import Tcsh  # noqa: F401
from .zsh import Zsh
from .powershell import Powershell  # noqa: F401

# The optimized runtime path is intentionally zsh-only.  The legacy shell
# classes remain importable for compatibility/tests, but automatic detection
# only selects zsh; all other shells fall back to Generic.
shells = {'zsh': Zsh}


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
