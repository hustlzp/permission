Permission
==========
[![Latest Version](http://img.shields.io/pypi/v/permission.svg)](https://pypi.python.org/pypi/permission)
[![The MIT License](http://img.shields.io/badge/license-MIT-blue.svg)](https://github.com/hustlzp/permission/blob/master/LICENSE)

Simple and flexible permission control for Flask app.

## Features

* **Simple**: all you need to do is subclassing `Rule` and `Permission` class.
* **Flexible**: support rule inheritance and bitwise operations(`&` and `|`) to build your own rules.

## Installation

```
$ pip install permission
```

## Rule

`Rule` has 3 methods which can be overrided:

* base(): define base rule.
* check(): determine whether this rule should be passed or not.
* deny(): will be executed when `check()` failed.

You should always override `check()` and `deny()` while overriding `base()` as needed.

## Permission

`Permission` has 1 method which can be overrided:

* rule(): define rule needed by this permission

You should always override `rule()`.

`Permission` has 2 instance methods you can use in codes:

* check(): call this to check rule of this permission
* deny(): call this to execute codes when `check()` failed

## Usage

First you need to define your own rules by subclassing `Rule` then
override `check()` and `deny()`:

```py
# rules.py
from flask import session, flash, redirect, url_for
from permission import Rule


class UserRule(Rule):
    def check(self):
        """Check if there is a user signed in."""
        return 'user_id' in session

    def deny(self):
        """When no user signed in, redirect to signin page."""
        flash('Sign in first.')
        return redirect(url_for('signin'))
```

Then you define permissions by subclassing `Permission` and override `rule()`:


```py
# permissions.py
from permission import Permission
from .rules import UserRule


class UserPermission(Permission):
    """Only signin user has this permission."""
    def rule(self):
        return UserRule()
```

There are 4 ways to use the `UserPermission` defined above:

**1. Use as view decorator**

```py
from .permissions import UserPermission


@app.route('/settings')
@UserPermission()
def settings():
    """User settings page, only accessable for sign-in user."""
    return render_template('settings.html')
```

**2. Use in view codes**

```py
from .permissions import UserPermission


@app.route('/settions')
def settings():
    permission = UserPermission()
    if not permission.check()
        return permission.deny()
    return render_template('settings.html')
```

**3. Use in view codes (using `with` statement)**

```py
from .permissions import UserPermission


@app.route('/settions')
def settings():
    with UserPermission():
        return render_template('settings.html')
```

**Note**: if you don't raise an exception when the permission check failed (in other words,
a rule's ``deny()`` will be called), ``PermissionDeniedException`` will be raised in order to stop the execution
of the with-body codes. By the way, you can import this exception as needed:

```py
from permission import PermissionDeniedException
```

**4. Use in Jinja2 templates**

First you need to inject your defined permissions to template context:

```py
from . import permissions


@app.context_processor
def inject_vars():
    return dict(
        permissions=permissions
    )
```

then in templates:

```html
{% if permissions.UserPermission().check() %}
    <a href="{{ url_for('new') }}">New</a>
{% endif %}
````

## Rule Inheritance

Need to say, inheritance here is not the same thing as Python class
inheritance, it's just means you can use RuleA as the base rule of RuleB.

We achieve this by overriding `base()`.

Let's say an administrator user should always be a user:

```py
# rules.py
from flask import session, abort, flash, redirect, url_for
from permission import Rule


class UserRule(Rule):
    def check(self):
        return 'user_id' in session

    def deny(self):
        flash('Sign in first.')
        return redirect(url_for('signin'))


class AdminRule(Rule):
    def base(self):
        return UserRule()

    def check(self):
        user_id = int(session['user_id'])
        user = User.query.filter(User.id == user_id).first()
        return user and user.is_admin

    def deny(self):
        abort(403)
```

## Rule Bitwise Operations

* `RuleA & RuleB` means it will be passed when both RuleA and RuleB are passed.
* `RuleA | RuleB` means it will be passed either RuleA or RuleB is passed.

Let's say we need to build a forum with Flask.
Only the topic creator and administrator user can edit a topic:

First define rules:

```py
# rules.py
from flask import session, abort, flash, redirect, url_for
from permission import Rule
from .models import User, Topic


class UserRule(Rule):
    def check(self):
        """Check if there is a user signed in."""
        return 'user_id' in session

    def deny(self):
        """When no user signed in, redirect to signin page."""
        flash('Sign in first.')
        return redirect(url_for('signin'))


class AdminRule(Rule):
    def base(self):
        return UserRule()

    def check(self):
        user_id = int(session['user_id'])
        user = User.query.filter(User.id == user_id).first()
        return user and user.is_admin

    def deny(self):
        abort(403)


class TopicCreatorRule(Rule):
    def __init__(self, topic):
        self.topic = topic
        super(TopicCreatorRule, self).__init__()

    def base(self):
        return UserRule()

    def check(self):
        return topic.user_id == session['user_id']

    def deny(self):
        abort(403)
```

then define permissions:

```py
# permissions.py
from permission import Permission


class TopicAdminPermission(Permission):
    def __init__(self, topic):
        self.topic = topic
        super(TopicAdminPermission, self).__init__()

    def rule(self):
        return AdminRule() | TopicCreatorRule(self.topic)
```

so we can use `TopicAdminPermission` in `edit_topic` view:

```py
from .permissions import TopicAdminPermission


@app.route('topic/<int:topic_id>/edit')
def edit_topic(topic_id):
    topic = Topic.query.get_or_404(topic_id)
    permission = TopicAdminPermission(topic)
    if not permission.check():
        return permission.deny()
    ...
```

## License

MIT
