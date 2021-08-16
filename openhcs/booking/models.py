from __future__ import absolute_import

import logging
from flask.globals import session

from sqlalchemy import Column, Integer, String, Text
from sqlalchemy.sql.schema import UniqueConstraint
from sqlalchemy.sql.sqltypes import Date, Time

from openhcs import dbase, initializer

session = dbase.session


class Appointment(dbase.Model):
    __tablename__ = "appointments"
    __table_args__ = {"extend_existing": True}
    __bind_key__ = "booking"

    id = Column(Integer, primary_key=True)
    date = Column(Date)
    time = Column(Time)
    doctor_name = Column(String(55))
    doctor_speciality = Column(String(55))
    doctor_identity = Column(Text)
    beneficiary_name = Column(String(55))
    beneficiary_phone = Column(String(55))
    beneficiary_identity = Column(Text)
    remarks = Column(Text)

    UniqueConstraint("beneficiary_id", "date", "time", name="unique_appointmt")

    def __init__(self, **kwargs):
        self.date = initializer("date", kwargs)
        self.time = initializer("time", kwargs)
        self.doctor_name = initializer("doctor_name", kwargs)
        self.doctor_speciality = initializer("doctor_speciality", kwargs)
        self.doctor_identity = initializer("doctor_id", kwargs)
        self.beneficiary_name = initializer("beneficiary_name", kwargs)
        self.beneficiary_phone = initializer("beneficiary_phone", kwargs)
        self.beneficiary_identity = initializer("beneficiary_id", kwargs)
        self.remarks = initializer("remarks", kwargs)

    def save(self):

        try:
            session.add(self)
            session.commit()
            return self
        except RuntimeError as error:
            logging.exception(error)

    def getby_beneficiaryId(self, identity: int = None):
        if identity is not None:
            beneficiary = self.query.filter(Appointment.beneficiary_id.ilike(identity))
            return beneficiary
        return None

    def getby_beneficiaryName(self, name: str = None):
        if name is not None:
            beneficiary = self.query.filter(Appointment.beneficiary_name.ilike(name))
            return beneficiary
        return None
