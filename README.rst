Permission
==========

Simple and flexible permission control for Flask app.

Features
--------

* **Simple**: all you need to do is subclassing ``Rule`` and ``Permission`` class.
* **Flexible**: support rule inheritance and bitwise operations(``&`` and ``|``) to build your own rules.

Installation
------------

::

    $ pip install permission

Rule and Permission
-------------------

``Rule`` has 3 methods which can be overrided:

* base(): define base rule.
* check(): determine whether this rule should be passed or not.
* deny(): will be executed when ``check()`` failed.

You should always override ``check()`` and ``deny()`` while overriding ``base()``
as needed.

``Permission`` has 1 methods which can be overrided:

* rule(): define rules needed by this permission

You should always override ``rule()``.

``Permission`` has 2 instance methods you can used in codes:

* check(): call this to check rules of this permission
* deny(): call this to execute codes when ``check()`` failed

Usage
-----

First you need to define your own rules by subclassing ``Rule`` then
override ``check()`` and ``deny()``::

    # rules.py
    from flask import session, abort, flash
    from permission import Rule

    class UserRule(Rule):
        def check(self):
            """Check if there is a user signed in."""
            return 'user_id' in session

        def deny(self):
            """When no user signed in, redirect to signin page."""
            flash('This action need the login')
            return redirect(url_for('signin'))

Then you define permissions by subclassing ``Permission`` and override
``rule()``::

    # permissions.py
    from permission import Permission
    from .rules import UserRule

    class UserPermission(Permission):
        """Only signin user has this permission."""
        def rule(self):
            return UserRule()

Use as view decorator::

    from .permissions import UserPermission

    @app.route('/settings')
    @UserPermission()
    def settings():
        """User settings page, only accessable for sign-in user."""
        return render_template('settings.html')

Use in view codes::

    from .permissions import UserPermission

    @app.route('/settions')
    def settings():
        permission = UserPermission()
        if not permission.check()
            return permission.deny()
        return render_template('settings.html')

Use in Jinja2 templates, first you need to inject your defined
permissions to template context::

    from .permissions import UserPermission

    @app.context_processor
    def inject_vars():
        return dict(
            permissions=permissions
        )

Then in templates::

    {% if permissions.UserPermission().check() %}
        <a href="{{ url_for('new') }}">New</a>
    {% endif %}

Inheritance
-----------

Need to say, inheritance here is not the same thing as Python class
inheritance, it's just means you can use RuleA as the base rule of RuleB.

We achieve this by overriding ``base()``.

Examples
~~~~~~~~

Let's say an administrator user should always be a user::

    # rules.py
    from flask import session, abort, flash
    from permission import Rule


    class UserRule(Rule):
        def check(self):
            return 'user_id' in session

        def deny(self):
            flash('This action need the login')
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

Bitwise operations
------------------

* ``RuleA & RuleB`` means it will be passed when both RuleA and RuleB are passed.
* ``RuleA | RuleB`` means it will be passed either RuleA or RuleB is passed.

Examples
~~~~~~~~

Let's say we need to build a forum with Flask.
Only the topic creator and administrator user can edit a topic:

First let's define rules::

    # rules.py
    from flask import session, abort, flash
    from permission import Rule
    from .models import User, Topic


    class UserRule(Rule):
        def check(self):
            """Check if there is a user signed in."""
            return 'user_id' in session

        def deny(self):
            """When no user signed in, redirect to signin page."""
            flash('This action need the login')
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
        def __init__(self, topic_id):
            self.topic_id = topic_id
            super(TopicCreatorRule, self).__init__()

        def base(self):
            return UserRule()

        def check(self):
            topic = Topic.query.filter(Topic.id == self.topic_id).first()
            return topic and topic.user_id == session['user_id']

        def deny(self):
            abort(403)

Then define permissions::

    # permissions.py
    from permission import Permission


    class UserPermission(Permission):
        def rule(self):
            return UserRule()


    class AdminPermission(Permission):
        def rule(self):
            return AdminRule()


    class TopicAdminPermission(Permission):
        def __init__(self, topic_id):
            self.topic_id = topic_id
            super(TopicAdminPermission, self).__init__()

        def rule(self):
            return AdminRule() | QuestionOwnerRule(self.topic_id)


So we can use ``TopicAdminPermission`` in ``edit_topic`` view::

    from .permissions import TopicAdminPermission

    @app.route('topic/<int:topic_id>/edit')
    def edit_topic(topic_id):
        topic = Topic.query.get_or_404(topic_id)
        permission = TopicAdminPermission(topic_id)
        if not permission.check():
            return permission.deny()
        ...
