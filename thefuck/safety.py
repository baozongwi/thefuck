# -*- encoding: utf-8 -*-
"""Safety helpers for commands that may be executed by shell aliases."""

import re
import shlex
from collections import namedtuple


RISK_SAFE = 'safe'
RISK_SIDE_EFFECT = 'side-effect'
RISK_DANGEROUS = 'dangerous'

SafetyInfo = namedtuple('SafetyInfo', ['level', 'reasons'])

_DANGEROUS_RULES = set([
    'rm_root',
    'rm_dir',
    'git_rebase_merge_dir',
    'dirty_unzip',
    'dirty_untar',
    'port_already_in_use',
    'sudo',
    'sudo_command_from_user_path',
    'apt_get',
    'apt_upgrade',
    'pip_install',
    'python_module_error',
    'pacman',
    'nixos_cmd_not_found',
    'chmod_x',
    'git_push_force',
    'git_tag_force',
    'git_hook_bypass',
    'git_branch_delete',
    'git_branch_delete_checked_out',
    'git_branch_exists',
    'git_branch_0flag',
    'git_branch_list',
    'git_rm_local_modifications',
    'git_rm_staged',
    'git_rm_recursive',
    'git_commit_reset',
    'git_stash_pop',
    'git_commit_amend',
    'git_add_force',
    'docker_image_being_used_by_container',
    'brew_uninstall',
    'django_south_ghost',
    'rails_migrations_pending',
])

_DANGEROUS_RE = [
    (re.compile(r'(^|[;&|]\s*)sudo\b'), 'sudo'),
    (re.compile(r'(^|[;&|]\s*)(kill|pkill|killall)\b'), 'kill'),
    (re.compile(r'(^|[;&|]\s*)chmod\s+777\b'), 'chmod 777'),
    (re.compile(r'(^|[;&|]\s*)chown\b'), 'chown'),
    (re.compile(r'(^|[;&|]\s*)chmod\s+\+x\b'), 'chmod +x'),
    (re.compile(r'(^|[;&|]\s*)dd\b'), 'dd'),
    (re.compile(r'(^|[;&|]\s*)mkfs(\.|\s|$)'), 'mkfs'),
    (re.compile(r'(^|[;&|]\s*)git\s+push\b[^;&|]*(--force|-f)\b'),
     'git push --force'),
    (re.compile(r'(^|[;&|]\s*)git\s+clean\b[^;&|]*-[^;&|]*f'),
     'git clean -f'),
    (re.compile(r'(^|[;&|]\s*)git\s+branch\b[^;&|]*\s-d\b'),
     'git branch -D'),
    (re.compile(r'(^|[;&|]\s*)git\s+rm\b[^;&|]*-[^;&|]*f'),
     'git rm -f'),
    (re.compile(r'(^|[;&|]\s*)git\s+reset\b'), 'git reset'),
    (re.compile(r'(^|[;&|]\s*)git\s+commit\b[^;&|]*--amend\b'),
     'git commit --amend'),
    (re.compile(r'\b--no-verify\b'), '--no-verify'),
    (re.compile(r'(^|[;&|]\s*)docker\s+(rm|rmi)\b'), 'docker remove'),
    (re.compile(r'(^|[;&|]\s*)docker\s+container\s+rm\b'),
     'docker remove'),
    (re.compile(r'(^|[;&|]\s*)pip\s+install\b'), 'pip install'),
    (re.compile(r'(^|[;&|]\s*)apt(-get)?\s+(install|upgrade)\b'),
     'apt package mutation'),
    (re.compile(r'(^|[;&|]\s*)pacman\s+-S\b'), 'pacman install'),
    (re.compile(r'(^|[;&|]\s*)nix-env\s+-i'), 'nix install'),
    (re.compile(r'(^|[;&|]\s*)brew\s+uninstall\b[^;&|]*--force'),
     'brew uninstall --force'),
    (re.compile(r'(^|[;&|]\s*)kubectl\s+delete\b'), 'kubectl delete'),
    (re.compile(r'\bdrop\s+database\b'), 'drop database'),
]


def _safe_split(script):
    try:
        return shlex.split(script)
    except (ValueError, TypeError):
        return []


def assess_command(script, side_effect=None, rule_name=None):
    """Returns SafetyInfo for a corrected or rerun command."""
    reasons = []
    normalized = (script or '').lower()

    for pattern, reason in _DANGEROUS_RE:
        if pattern.search(normalized):
            reasons.append(reason)

    # Token fallback catches common forms that are awkward as regexes.
    parts = [part.lower() for part in _safe_split(script or '')]
    if parts:
        if parts[0] == 'rm' and any(
                part.startswith('-') and 'r' in part and 'f' in part
                for part in parts[1:]):
            reasons.append('rm -rf')
        if parts[0] in ('kill', 'pkill', 'killall') and 'kill' not in reasons:
            reasons.append('kill')
        if parts[:2] == ['git', 'push'] and (
                '--force' in parts or '-f' in parts):
            if 'git push --force' not in reasons:
                reasons.append('git push --force')

    if rule_name in _DANGEROUS_RULES:
        reasons.append('rule:{}'.format(rule_name))

    if reasons:
        return SafetyInfo(RISK_DANGEROUS, reasons)
    elif side_effect:
        return SafetyInfo(RISK_SIDE_EFFECT, ['side effect'])
    else:
        return SafetyInfo(RISK_SAFE, [])


def is_safe_to_rerun(script):
    """Returns False for commands that should not be rerun for output."""
    return assess_command(script).level == RISK_SAFE
