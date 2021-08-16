from __future__ import absolute_import
import logging

import pickle
from sqlalchemy.orm import relationship
from sqlalchemy.sql.elements import and_

from sqlalchemy.sql.schema import Column, ForeignKey
from sqlalchemy.sql.sqltypes import PickleType, String, Integer, Text
from werkzeug.security import check_password_hash, generate_password_hash


from openhcs import dbase, initializer
from openhcs import Doctor


session = dbase.session


class Subscriber(dbase.Model):
    __tablename__ = "subscriber"
    __bind_key__ = "subscribers"
    __table_args__ = {"extend_existing": True}

    id = Column(Integer, primary_key=True)
    user_name = Column(String(55), unique=True)
    password = Column(Text)
    role = Column(String(55))
    public_id = Column(String(128), nullable=False, unique=True)
    owner_ref = Column(PickleType)
    country = Column(String(55))
    birth_date = Column(String(55))
    status = Column(String(55))

    access_keys = relationship(
        "AuthenticationKey", backref="subscriber", lazy="select", cascade="delete"
    )

    def __init__(self, **kwargs):
        # super().__init__(**kwargs["data"])
        if "data" in kwargs:
            self.user_name = initializer("username", kwargs["data"])
            self.password = initializer("password", kwargs["data"])
            self.role = initializer("role", kwargs["data"])
            self.public_id = initializer("publicid", kwargs["data"])
            self.owner_ref = pickle.dumps(
                dict(
                    phone=initializer("phone", kwargs["data"]),
                    full_name=initializer("fullname", kwargs["data"]),
                    gender=initializer("gender", kwargs["data"]),
                )
            )
            self.country = initializer("country", kwargs["data"])
            self.birth_date = initializer("birthdate", kwargs["data"])

    def save(self):

        try:
            self.status = "Pending"
            session.add(self)
            session.commit()
            return self
        except RuntimeError as error:
            print(error)
            return None

    def validate(self):
        try:
            subscriber = self.query.filter(
                and_(
                    Subscriber.role.in_(["doctor", "beneficiary", "caregiver"]),
                    Subscriber.user_name.like(self.user_name),
                    Subscriber.public_id.like(self.public_id),
                )
            ).one_or_none()
            if subscriber:
                return True, subscriber
            return False, None
        except RuntimeError as error:
            logging.exception(error)
            return False, None

    def get_one(self, userid: str, role: str):
        # print(userid)
        return (
            session.query(Subscriber)
            .filter(Subscriber.role.like(role), Subscriber.user_name.like(userid))
            .first()
        )

    def getby_publicid(self):
        return self.query.filter(
            Subscriber.public_id.like(self.public_id)
        ).one_or_none()

    def retrieve_profile_owner(self):
        access_keys = self.access_keys[0].private_key

        if self.role == "doctor":

            owner = Doctor().retrieve_profile(access_keys)

            return owner

    def retrieve_subscriber(self, public_id: str, user_name: str):
        return self.query.filter(
            and_(
                Subscriber.public_id.like(public_id),
                Subscriber.user_name.like(user_name),
            )
        ).first()


class AuthenticationKey(dbase.Model):

    """Store registered users hashed nif as private_key
    and public_id as public_key.
    """

    __tablename__ = "authenticationkey"
    __bind_key__ = "subscribers"
    __table_args__ = {"extend_existing": True}

    id = Column(Integer, primary_key=True)
    private_key = Column(Text, nullable=False)
    subscriber_id = Column(ForeignKey(Subscriber.id))

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)

    def save(self, subscriber=None):
        try:
            check = self.query.filter(
                AuthenticationKey.private_key.ilike(self.private_key)
            ).first()

            if check:

                return True, check

            session.add(self)
            subscriber.access_keys.append(self)
            session.commit()
            return True, self

        except RuntimeError as error:
            print(error)
            return False, None

    def link_keys_to_subscriber(self, current_user: Subscriber):
        try:
            status, keys = self.save(current_user)
            if status:

                return True, keys
            return False, keys
        except RuntimeError as error:
            print(error)
            return False, None

    def check_keys_link_to_subscriber(self, public_key):
        return Subscriber(public_id=public_key).getby_publicid()

    def update(self, private_key, public_key):
        session.query(AuthenticationKey).update(
            private_key=private_key, public_key=public_key
        )
