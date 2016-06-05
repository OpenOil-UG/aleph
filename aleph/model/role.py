from uuid import uuid4
from flask import current_app

from aleph.core import db, url_for
from aleph.model.schema_model import SchemaModel
from aleph.model.common import SoftDeleteModel, IdModel
from flask.ext.security.utils import get_hmac


class Role(db.Model, IdModel, SoftDeleteModel, SchemaModel):
    """A user, group or other access control subject."""

    _schema = 'role.json#'
    __tablename__ = 'role'

    USER = 'user'
    GROUP = 'group'
    SYSTEM = 'system'
    TYPES = [USER, GROUP, SYSTEM]

    SYSTEM_GUEST = 'guest'
    SYSTEM_USER = 'user'

    foreign_id = db.Column(db.Unicode(2048), nullable=False, unique=True)
    name = db.Column(db.Unicode, nullable=False)
    email = db.Column(db.Unicode, nullable=False, unique=True)
    api_key = db.Column(db.Unicode, nullable=True)
    is_admin = db.Column(db.Boolean, nullable=False, default=False)
    type = db.Column(db.Enum(*TYPES, name='role_type'), nullable=False)
    permissions = db.relationship("Permission", backref="role")
    
    confirmed_at = db.Column(db.DateTime())
    password = db.Column(db.String(255), nullable=False, server_default='')
    reset_password_token = db.Column(db.String(100), nullable=False, server_default='')
 
    def update(self, data):
        self.schema_update(data)

    def check_pw(self, pw):
        return self.password == get_hmac(pw)        

    @classmethod
    def notifiable(cls):
        return cls.all_ids().filter(cls.email != None)  # noqa

    @classmethod
    def by_foreign_id(cls, foreign_id):
        if foreign_id is not None:
            return cls.all().filter_by(foreign_id=foreign_id).first()

    @classmethod
    def by_api_key(cls, api_key):
        if api_key is not None:
            return cls.all().filter_by(api_key=api_key).first()

    @classmethod
    def load_or_create(cls, foreign_id, type, name, email=None,
                       is_admin=None):
        role = cls.by_foreign_id(foreign_id)
        if role is None:
            role = cls()
            role.foreign_id = foreign_id
            role.type = type
            role.is_admin = False

        if role.api_key is None:
            role.api_key = uuid4().hex
        role.name = name
        role.email = email

        if is_admin is not None:
            role.is_admin = is_admin

        db.session.add(role)
        db.session.flush()
        return role

    @classmethod
    def system(cls, foreign_id):
        if not hasattr(current_app, '_authz_roles'):
            current_app._authz_roles = {}
        if foreign_id not in current_app._authz_roles:
            role = cls.by_foreign_id(foreign_id)
            if role is None:
                return
            current_app._authz_roles[foreign_id] = role.id
        return current_app._authz_roles[foreign_id]

    @classmethod
    def by_email(cls, email):
        q = db.session.query(cls).filter_by(email=email)
        return q.first()

    @classmethod
    def create_by_email(cls, email, pw):
        src = cls(
            email = email,
            password = get_hmac(pw)) 
        db.session.add(src)
        db.session.commit()
        
    @classmethod
    def create(cls, data, user=None):
        src = cls()
        data = SourceCreateForm().deserialize(data)
        src.slug = data.get('slug')
        src.crawler = data.get('crawler')
        src.update_data(data, user)
        db.session.add(src)
        return src

    def __repr__(self):
        return '<Role(%r,%r)>' % (self.id, self.foreign_id)

    def __unicode__(self):
        return self.name

    def to_dict(self):
        data = super(Role, self).to_dict()
        data['api_url'] = url_for('roles_api.view', id=self.id)
        data['foreign_id'] = self.foreign_id
        data['is_admin'] = self.is_admin
        data['email'] = self.email
        data['type'] = self.type
        return data
