from functools import wraps
import flask
from flask.ext.security import signals as security_signals
from flask.ext.mail import Message
from art17 import models
from art17.common import admin_perm, HOMEPAGE_VIEW_NAME
from art17.auth import zope_acl_manager


@security_signals.user_confirmed.connect
def put_in_activation_queue(app, user, **extra):
    user.waiting_for_activation = True
    models.db.session.commit()

    msg = Message(
        subject="User has registered",
        sender=app.extensions['security'].email_sender,
        recipients=[app.config['AUTH_ADMIN_EMAIL']],
    )
    msg.body = flask.render_template(
        'auth/email_admin_new_user.txt',
        user=user,
        activation_link=flask.url_for(
            'auth.admin_user',
            user_id=user.id,
            _external=True,
        ),
    )
    app.extensions['mail'].send(msg)


def require_admin(view):
    @wraps(view)
    def wrapper(*args, **kwargs):
        admin_perm.test()
        return view(*args, **kwargs)
    return wrapper


def get_ldap_user_info(user_id):
    from eea.usersdb import UsersDB
    ldap_server = flask.current_app.config['EEA_LDAP_SERVER']
    users_db = UsersDB(ldap_server=ldap_server)
    return users_db.user_info(user_id)


def notify_user_account_activated(user):
    app = flask.current_app
    msg = Message(
        subject="Account has been activated",
        sender=app.extensions['security'].email_sender,
        recipients=[user.email],
    )
    msg.body = flask.render_template(
        'auth/email_user_activated.txt',
        user=user,
        home_url=flask.url_for(HOMEPAGE_VIEW_NAME),
    )
    app.extensions['mail'].send(msg)


def set_user_active(user, new_active):
    was_active = user.active
    user.active = new_active
    if user.waiting_for_activation and not was_active and new_active:
        user.waiting_for_activation = False
        notify_user_account_activated(user)
    models.db.session.commit()
    if not user.is_ldap:
        if was_active and not new_active:
            zope_acl_manager.delete(user)
        if new_active and not was_active:
            zope_acl_manager.create(user)