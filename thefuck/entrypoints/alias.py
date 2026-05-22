import re
import sys
from ..conf import settings
from ..logs import warn, failed
from ..shells import shell
from ..utils import which


_ALIAS_RE = re.compile(r'^[A-Za-z_][A-Za-z0-9_-]*$')


def is_valid_alias_name(alias_name):
    return bool(alias_name and _ALIAS_RE.match(alias_name))


def _get_alias(known_args):
    if not is_valid_alias_name(known_args.alias):
        raise ValueError('Unsafe alias name: {}'.format(known_args.alias))

    alias = shell.app_alias(known_args.alias)

    if known_args.enable_experimental_instant_mode:
        if not which('script'):
            warn("Instant mode requires `script` app")
        else:
            return shell.instant_mode_alias(known_args.alias)

    return alias


def print_alias(known_args):
    settings.init(known_args)
    try:
        print(_get_alias(known_args))
    except ValueError as exc:
        failed(str(exc))
        sys.exit(1)
