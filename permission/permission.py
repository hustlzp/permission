# coding: utf-8
from functools import wraps


class Permission(object):
    def __init__(self):
        role = self.role()
        if not role:
            raise AttributeError()
        self.role = role

    def __call__(self, func):
        """Give Permission instance the ability to be used as view decorator."""

        @wraps(func)
        def decorator(*args, **kwargs):
            if not self.check():
                return self.deny()
            return func(*args, **kwargs)

        return decorator

    def role(self):
        """Add role to this permission.

        Must be overrided."""
        raise NotImplementedError

    def check(self):
        """Check role."""
        result, self.deny = self.role.run()
        return result

    def show(self):
        """Show the structure of role, only for debug."""
        self.role.show()


class Role(object):
    def __init__(self):
        self.roles_list = [[(self.check, self.deny)]]
        # if subclass override base(), serial merge the return role's
        # roles_list to self.roles_list.
        base_role = self.base()
        if base_role:
            self.roles_list = Role._and(base_role.roles_list, self.roles_list)

    def __and__(self, other):
        """& bitwise operation.

        Serial merge self.roles_list to other.roles_list and return self.
        """
        self.roles_list = Role._and(self.roles_list, other.roles_list)
        return self

    def __or__(self, other):
        """| bitwise operation.

        Parallel merge self.roles_list to other.roles_list and return self.
        """
        for role in other.roles_list:
            self.roles_list.append(role)
        return self

    def show(self):
        """Show the structure of self.roles_list, only for debug."""
        for role in self.roles_list:
            result = ", ".join([str(check) for check, deny in role])
            print(result)

    def base(self):
        """Add base role."""
        return None

    def run(self):
        """Run self.roles_list.

        Return True if one role channel has been passed.
        Otherwise return False and the deny() method of the last failed role.
        """
        failed_result = None
        for role in self.roles_list:
            for check, deny in role:
                if not check():
                    failed_result = (False, deny)
                    break
            else:
                return (True, None)
        return failed_result

    def check(self):
        """Codes to determine whether this role is passed.

        Must be overrided.
        """
        raise NotImplementedError()

    def deny(self):
        """Codes to be execute when check() failed.

        Must be overrided.
        """
        raise NotImplementedError()

    @staticmethod
    def _and(roles_list_pre, roles_list_pro):
        """Serial merge role_list_pre to role_list_pro."""
        return [role_pre + role_pro
                for role_pre in roles_list_pre
                for role_pro in roles_list_pro]
