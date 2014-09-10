# coding: utf-8
from functools import wraps


class Permission(object):
    def __init__(self):
        rule = self.rule()
        if not rule:
            raise AttributeError()
        self.rule = rule

    def __call__(self, func):
        """提供view装饰器能力"""

        @wraps(func)
        def decorator(*args, **kwargs):
            if not self.check():
                return self.deny()
            return func(*args, **kwargs)

        return decorator

    def rule(self):
        """为当前permission装配rule"""
        raise NotImplementedError

    def check(self):
        """运行规则"""
        result, self.deny = self.rule.run()
        return result

    def show(self):
        """显示self.rule的规则结构，调试用"""
        self.rule.show()


class Rule(object):
    def __init__(self):
        self.rules_list = [[(self.check, self.deny)]]
        # 若子类实现了base方法，则将其返回的rule实例的rules_list串联到self.rules_list上游
        base_rule = self.base()
        if base_rule:
            self.rules_list = Rule._and(base_rule.rules_list, self.rules_list)

    def __and__(self, other):
        """逻辑与操作（&）

        即将other.rules_list串联到self.rules_list的下游，
        并返回当前实例。"""
        self.rules_list = Rule._and(self.rules_list, other.rules_list)
        return self

    def __or__(self, other):
        """逻辑或操作（|）

        将self.rules_list与other.rules_list并联起来，
        并返回当前实例"""
        for rule in other.rules_list:
            self.rules_list.append(rule)
        return self

    def show(self):
        """显示rules_list的结构，调试用"""
        for rule in self.rules_list:
            result = ", ".join([str(check) for check, deny in rule])
            print(result)

    def base(self):
        """提供rule规则继承能力（串联）"""
        return None

    def run(self):
        """运行rules_list。

        若某一通道check通过，则返回成功状态
        若所有通道都无法check通过，则返回失败状态（包含最后运行失败的rule的deny方法）"""
        failed_result = None
        for rule in self.rules_list:
            for check, deny in rule:
                if not check():
                    failed_result = (False, deny)
                    break
            else:
                return (True, None)
        return failed_result

    def check(self):
        """当前rule的测试方法，强制子类overload"""
        raise NotImplementedError()

    def deny(self):
        """当前rule测试失败后需要执行的方法，强制子类overload"""
        raise NotImplementedError()

    @staticmethod
    def _and(rules_list_pre, rules_list_pro):
        """将rule_list_pre串联到rule_list_pro上游"""
        return [rule_pre + rule_pro
                for rule_pre in rules_list_pre
                for rule_pro in rules_list_pro]
