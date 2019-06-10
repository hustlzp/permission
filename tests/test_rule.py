import pytest

from permission import Rule

from .utils import make_rule


def test_run_ok():
    rule = make_rule(check_result=True)
    ret = rule.run()
    assert ret == (True, None)


def test_show_single(mocker):
    fake_print = mocker.MagicMock()
    mocker.patch('builtins.print', fake_print)
    rule = make_rule(check_result=True)
    rule.show()
    fake_print.assert_called_once_with(str(rule.check))


def test_show_multiple(mocker):
    fake_print = mocker.MagicMock()
    mocker.patch('builtins.print', fake_print)
    rule_a = make_rule(check_result=True)
    rule_b = make_rule(check_result=True, base_rule=rule_a)
    rule_b.show()
    rr = (str(rule_a.check), str(rule_b.check))
    fake_print.assert_called_once_with(', '.join(rr))


def test_run_fail():
    rule = make_rule(check_result=False)
    ret = rule.run()
    assert ret == (False, rule.deny)


def test_base_simple():
    rule = make_rule(check_result=True)
    assert rule.base() is None


def test_base_extending():
    rule_a = make_rule(check_result=True)
    rule_b = make_rule(check_result=True, base_rule=rule_a)
    assert rule_b.base() == rule_a


def test_with_base_all_pass():
    rule_a = make_rule(check_result=True)
    rule_b = make_rule(check_result=True, base_rule=rule_a)
    ret = rule_b.run()
    assert ret == (True, None)


def test_with_base_base_fails():
    rule_a = make_rule(check_result=False)
    rule_b = make_rule(check_result=True, base_rule=rule_a)
    ret = rule_b.run()
    assert ret == (False, rule_a.deny)


def test_with_base_rule_fails():
    rule_a = make_rule(check_result=True)
    rule_b = make_rule(check_result=False, base_rule=rule_a)
    ret = rule_b.run()
    assert ret == (False, rule_b.deny)


def test_with_base_all_fail():
    rule_a = make_rule(check_result=False)
    rule_b = make_rule(check_result=False, base_rule=rule_a)
    ret = rule_b.run()
    assert ret == (False, rule_a.deny)


def test_and_all_pass():
    rule_a = make_rule(check_result=True)
    rule_b = make_rule(check_result=True)
    combined_rule = rule_a & rule_b
    ret = combined_rule.run()
    assert ret == (True, None)


def test_and_1st_fail():
    rule_a = make_rule(check_result=False)
    rule_b = make_rule(check_result=True)
    combined_rule = rule_a & rule_b
    ret = combined_rule.run()
    assert ret == (False, rule_a.deny)


def test_and_2nd_fail():
    rule_a = make_rule(check_result=True)
    rule_b = make_rule(check_result=False)
    combined_rule = rule_a & rule_b
    ret = combined_rule.run()
    assert ret == (False, rule_b.deny)


def test_and_all_fail():
    rule_a = make_rule(check_result=False)
    rule_b = make_rule(check_result=False)
    combined_rule = rule_a & rule_b
    ret = combined_rule.run()
    assert ret == (False, rule_a.deny)


@pytest.mark.parametrize('a_ok,b_ok', [
    (True, True),
    (True, False),
    (False, True),
], ids=['all-ok', '1st-ok', '2nd-ok'])
def test_or_passing(a_ok, b_ok):
    rule_a = make_rule(check_result=a_ok)
    rule_b = make_rule(check_result=b_ok)
    combined_rule = rule_a | rule_b
    ret = combined_rule.run()
    assert ret == (True, None)


def test_or_failing():
    rule_a = make_rule(check_result=False)
    rule_b = make_rule(check_result=False)
    combined_rule = rule_a | rule_b
    ret = combined_rule.run()
    assert ret == (False, rule_b.deny)


def test_not_implemented_check():
    rule = Rule()
    with pytest.raises(NotImplementedError):
        rule.check()


def test_not_implemented_deny():
    rule = Rule()
    with pytest.raises(NotImplementedError):
        rule.deny()
