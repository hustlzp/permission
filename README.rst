Permission
==========

Simple and flexible permission control for Flask app.

Features
--------

* **Simple**: all you need to do is subclassing ``Role`` and ``Permission`` class.
* **Flexible**: support role inheritance and bitwise operations(``&`` and ``|``) to build your own roles.

Installation
------------

::

    $ pip install permission

Role and Permission
-------------------

``Role`` has 3 methods which can be overrided:

* base(): define base role.
* check(): determine whether this role should be passed or not.
* deny(): will be executed when ``check()`` failed.

You should always override ``check()`` and ``deny()`` while overriding ``base()``
as needed.

``Permission`` has 1 method which can be overrided:

* role(): define role needed by this permission

You should always override ``role()``.

``Permission`` has 2 instance methods you can use in codes:

* check(): call this to check role of this permission
* deny(): call this to execute codes when ``check()`` failed

Usage
-----

First you need to define your own roles by subclassing ``Role`` then
override ``check()`` and ``deny()``::

    # roles.py
    from flask import session, abort, flash
    from permission import Role

    class UserRole(Role):
        def check(self):
            """Check if there is a user signed in."""
            return 'user_id' in session

        def deny(self):
            """When no user signed in, redirect to signin page."""
            flash('This action need the login')
            return redirect(url_for('signin'))

Then you define permissions by subclassing ``Permission`` and override
``role()``::

    # permissions.py
    from permission import Permission
    from .roles import UserRole

    class UserPermission(Permission):
        """Only signin user has this permission."""
        def role(self):
            return UserRole()

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
inheritance, it's just means you can use RoleA as the base role of RoleB.

We achieve this by overriding ``base()``.

Examples
~~~~~~~~

Let's say an administrator user should always be a user::

    # roles.py
    from flask import session, abort, flash
    from permission import Role


    class UserRole(Role):
        def check(self):
            return 'user_id' in session

        def deny(self):
            flash('This action need the login')
            return redirect(url_for('signin'))


    class AdminRole(Role):
        def base(self):
            return UserRole()

        def check(self):
            user_id = int(session['user_id'])
            user = User.query.filter(User.id == user_id).first()
            return user and user.is_admin

        def deny(self):
            abort(403)

Bitwise operations
------------------

* ``RoleA & RoleB`` means it will be passed when both RoleA and RoleB are passed.
* ``RoleA | RoleB`` means it will be passed either RoleA or RoleB is passed.

Examples
~~~~~~~~

Let's say we need to build a forum with Flask.
Only the topic creator and administrator user can edit a topic:

First let's define roles::

    # roles.py
    from flask import session, abort, flash
    from permission import Role
    from .models import User, Topic


    class UserRole(Role):
        def check(self):
            """Check if there is a user signed in."""
            return 'user_id' in session

        def deny(self):
            """When no user signed in, redirect to signin page."""
            flash('This action need the login')
            return redirect(url_for('signin'))


    class AdminRole(Role):
        def base(self):
            return UserRole()

        def check(self):
            user_id = int(session['user_id'])
            user = User.query.filter(User.id == user_id).first()
            return user and user.is_admin

        def deny(self):
            abort(403)


    class TopicCreatorRole(Role):
        def __init__(self, topic_id):
            self.topic_id = topic_id
            super(TopicCreatorRole, self).__init__()

        def base(self):
            return UserRole()

        def check(self):
            topic = Topic.query.filter(Topic.id == self.topic_id).first()
            return topic and topic.user_id == session['user_id']

        def deny(self):
            abort(403)

Then define permissions::

    # permissions.py
    from permission import Permission


    class UserPermission(Permission):
        def role(self):
            return UserRole()


    class AdminPermission(Permission):
        def role(self):
            return AdminRole()


    class TopicAdminPermission(Permission):
        def __init__(self, topic_id):
            self.topic_id = topic_id
            super(TopicAdminPermission, self).__init__()

        def role(self):
            return AdminRole() | TopicCreatorRole(self.topic_id)


So we can use ``TopicAdminPermission`` in ``edit_topic`` view::

    from .permissions import TopicAdminPermission

    @app.route('topic/<int:topic_id>/edit')
    def edit_topic(topic_id):
        topic = Topic.query.get_or_404(topic_id)
        permission = TopicAdminPermission(topic_id)
        if not permission.check():
            return permission.deny()
        ...
