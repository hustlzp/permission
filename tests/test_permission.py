import pytest

from permission import Permission, PermissionDeniedException

from .utils import FailingCheckException, make_permission, make_rule


@pytest.mark.parametrize('rule_result', [True, False], ids=['ok', 'fail'])
def test_check_result(rule_result):
    rule = make_rule(check_result=rule_result)
    permission = make_permission(rule)
    ret = permission.check()
    assert ret is rule_result


def test_rule_not_implemented():
    with pytest.raises(NotImplementedError):
        Permission()


def test_rule_invalid():
    with pytest.raises(AttributeError):
        make_permission(None)


def test_show(mocker):
    fake_print = mocker.MagicMock()
    mocker.patch('builtins.print', fake_print)
    rule = make_rule(check_result=True)
    permission = make_permission(rule)
    permission.show()
    fake_print.assert_called_once_with(str(rule.check))


def test_as_decorator_pass():
    rule = make_rule(check_result=True)
    permission = make_permission(rule)

    @permission
    def fun():
        return 'x'

    ret = fun()
    assert ret == 'x'


def test_as_decorator_fail():
    rule = make_rule(check_result=False)
    permission = make_permission(rule)

    @permission
    def fun():
        return 'x'

    ret = fun()
    assert ret == rule.deny()


def test_as_ctxmanager_pass():
    rule = make_rule(check_result=True, raising_exc=True)
    permission = make_permission(rule)

    def fun():
        return 'x'

    with permission:
        ret = fun()
        assert ret == 'x'


def test_as_ctxmanager_fail_not_raising():
    rule = make_rule(check_result=False)
    permission = make_permission(rule)

    def fun():
        return 'x'

    with pytest.raises(PermissionDeniedException):
        with permission:
            fun()


def test_as_ctxmanager_fail_raising():
    rule = make_rule(check_result=False, raising_exc=True)
    permission = make_permission(rule)

    def fun():
        return 'x'

    with pytest.raises(FailingCheckException):
        with permission:
            fun()
