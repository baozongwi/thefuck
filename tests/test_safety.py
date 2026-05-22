# -*- coding: utf-8 -*-

from thefuck import safety


def test_assess_safe_command():
    info = safety.assess_command('git status')
    assert info.level == safety.RISK_SAFE
    assert info.reasons == []


def test_assess_side_effect_command():
    info = safety.assess_command('ssh example.com', side_effect=lambda *_: None)
    assert info.level == safety.RISK_SIDE_EFFECT
    assert 'side effect' in info.reasons


def test_assess_dangerous_rm_command():
    info = safety.assess_command('rm -rf /tmp/project')
    assert info.level == safety.RISK_DANGEROUS
    assert 'rm -rf' in info.reasons


def test_assess_dangerous_rule_name():
    info = safety.assess_command('echo ok', rule_name='port_already_in_use')
    assert info.level == safety.RISK_DANGEROUS
    assert 'rule:port_already_in_use' in info.reasons


def test_assess_dangerous_package_and_git_mutation():
    assert safety.assess_command(
        'pip install requests').level == safety.RISK_DANGEROUS
    info = safety.assess_command('git branch -D production')
    assert info.level == safety.RISK_DANGEROUS
    assert 'git branch -D' in info.reasons


def test_assess_dangerous_rule_catalog():
    info = safety.assess_command('chmod +x ./deploy.sh', rule_name='chmod_x')
    assert info.level == safety.RISK_DANGEROUS
    assert 'rule:chmod_x' in info.reasons


def test_is_safe_to_rerun():
    assert safety.is_safe_to_rerun('git status')
    assert not safety.is_safe_to_rerun('sudo rm -rf /')
