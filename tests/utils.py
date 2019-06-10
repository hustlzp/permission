from permission import Rule, Permission


class FailingCheckException(Exception):
    pass


def make_rule(check_result, base_rule=None, raising_exc=False):

    class MyRule(Rule):

        def check(self):
            return check_result

        def deny(self):
            if raising_exc:
                raise FailingCheckException('failed')
            return 'failed'

    class MyRuleWithBase(Rule):

        def check(self):
            return check_result

        def deny(self):
            if raising_exc:
                raise FailingCheckException('failed')
            return 'failed'

        def base(self):
            return base_rule

    if base_rule is None:
        return MyRule()
    return MyRuleWithBase()


def make_permission(use_rule):

    class MyPermission(Permission):

        def rule(self):
            return use_rule

    return MyPermission()
