from __future__ import absolute_import
import logging
from operator import or_


from sqlalchemy import Column, String, Integer, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import backref, relationship
from sqlalchemy.exc import IntegrityError
from sqlalchemy.sql.expression import and_
from sqlalchemy.sql.schema import UniqueConstraint


from werkzeug.security import check_password_hash

from backend import dbase, initializer

session = dbase.session


class DoctorSpeciality(dbase.Model):
    __tablename__ = "doctor_speciality"
    __table_args__ = {"extend_existing": True}
    __bind_key__ = "profiles"

    doctor_id = Column(
        Integer, ForeignKey("doctor.id", ondelete="CASCADE"), primary_key=True
    )
    speciality_id = Column(
        Integer, ForeignKey("speciality.id", ondelete="CASCADE"), primary_key=True
    )


# class DoctorLicense(dbase.Model):
#     __tablename__ = "doctor_license"
#     __table_args__ = {"extend_existing" : True}
#     __bind_key__ = "profiles"

#     doctor_id = Column("doctor_id", Integer, ForeignKey("doctor.id", ondelete="CASCADE"), primary_key=True)
#     license_id = Column("license_id",Integer, ForeignKey("license.id", ondelete="CASCADE"), primary_key=True)


class BeneficiaryMorada(dbase.Model):
    __tablename__ = "beneficiary_morada"
    __table_args__ = {"extend_existing": True}
    __bind_key__ = "profiles"

    beneficiary_id = Column(
        Integer, ForeignKey("beneficiary.id", ondelete="CASCADE"), primary_key=True
    )
    address_id = Column(
        Integer, ForeignKey("address.id", ondelete="CASCADE"), primary_key=True
    )


class DoctorMorada(dbase.Model):
    __tablename__ = "doctor_morada"
    __table_args__ = {"extend_existing": True}
    __bind_key__ = "profiles"

    doctor_id = Column(
        Integer, ForeignKey("doctor.id", ondelete="CASCADE"), primary_key=True
    )
    address_id = Column(
        Integer, ForeignKey("address.id", ondelete="CASCADE"), primary_key=True
    )


class Beneficiary(dbase.Model):
    __table_args__ = (UniqueConstraint("full_name", "nif"), {"extend_existing": True})
    __tablename__ = "beneficiary"
    __bind_key__ = "profiles"

    id = Column(Integer, primary_key=True)
    full_name = Column(String(55))
    birth_date = Column(Text)
    gender = Column(String(6))
    photo = Column(Text, default="/media/profiles/beneficiaries/foto.jpg")
    phone = Column(Text)
    nif = Column(Text, unique=True)  # unique=True

    addresses = relationship(
        "Address",
        secondary="beneficiary_morada",
        backref=backref("beneficiaries", lazy="dynamic"),
    )

    doctor_id = Column("doctor_id", ForeignKey("doctor.id"))

    def __init__(self, *args, **kwargs):
        self.full_name = initializer("fullname", kwargs)
        self.birth_date = initializer("birthdate", kwargs)
        self.gender = initializer("gender", kwargs)
        self.photo = initializer("photo", kwargs)
        self.phone = initializer("phone", kwargs)
        self.nif = initializer("taxid", kwargs)
        # self.address = initializer("addresses", kwargs)

    # @classmethod
    # def add_address(self, address):
    #     # print(address)
    #     return Address(
    #         street_name=address["street_name"],
    #         door_num=address["doornumber"],
    #         zipcode=address["zipcode"],
    #         city=address["city"],
    #         state=address["state"],
    #         country=address["country"],
    #     )

    def save(self):
        session.add(self)
        try:
            # new_address = self.add_address(address=self.addresses)
            # if new_address.save() is None:

            #     return None
            # else:

            #     self.addresses.append(new_address)
            session.commit()
            return self
        except RuntimeError as error:
            logging.exception(error)
            return None

    def find_all(self, criterion: any, *args, **kwargs):
        # criterion => speciality | location | mode | [speciality, location]
        # kwargs => id | location | city_name | beneficiary_name | all
        if criterion == "city":
            beneficiaries = self.collect_by(Address.city == kwargs["name"])
            return beneficiaries
        if criterion == "zipcode":
            beneficiaries = self.collect_by(Address.city == kwargs["zipcode"])
            return beneficiaries
        if criterion == "id":
            return self.query.get(kwargs["id"])

        if criterion == "all":
            return self.query.all()

    def collect_by(self, additional_criterion: any):
        return (
            self.query.from_self()
            .join(Beneficiary.addresses)
            .join(BeneficiaryMorada)
            .filter(
                and_(
                    Address.id == BeneficiaryMorada.address_id,
                    Beneficiary.id == BeneficiaryMorada.beneficiary_id,
                ),
                additional_criterion,
            )
        )

    def validate(self, full_name, phone, nif):
        valid = self.query.filter(
            and_(
                self.full_name.like(full_name) == self.phone.like(phone),
                self.nif.like(nif),
            )
        ).first()
        if valid:
            return valid
        return None

    def delete(self):
        session.delete(self)
        session.commit()


class Doctor(dbase.Model):
    __table_args__ = (
        UniqueConstraint("full_name", "phone", "nif"),
        {"extend_existing": True},
    )
    __tablename__ = "doctor"
    __bind_key__ = "profiles"

    id = Column(Integer, primary_key=True)
    full_name = Column(String(55))  # unique=True
    gender = Column(String(6))
    phone = Column(Text, unique=True)  # unique=True
    nif = Column(Text, unique=True)  # unique=True
    photo = Column(Text, default="/media/profiles/doctors/foto.jpg")
    mode = Column(String(55), default="present")
    birth_date = Column(String(55))

    specialities = relationship(
        "Speciality",
        backref=backref("doctors", lazy="dynamic"),
        secondary="doctor_speciality",
        cascade="delete",
    )

    licences = relationship(
        "License",
        backref=backref("doctors", lazy="joined"),
        cascade="delete, delete-orphan",
    )

    addresses = relationship(
        "Address",
        backref=backref("doctors", lazy="dynamic"),
        secondary="doctor_morada",
        cascade="delete",
    )

    # added when practitioner start create a patient's profile
    beneficiaries = relationship("Beneficiary", backref="doctors", lazy="select")

    def __init__(self, **kwargs):
        self.full_name = initializer("fullname", kwargs)
        self.phone = initializer("phone", kwargs)
        self.birth_date = initializer("birthdate", kwargs)
        self.nif = initializer("taxid", kwargs)
        self.photo = initializer("photo", kwargs)
        self.mode = initializer("mode", kwargs)
        self.gender = initializer("gender", kwargs)

    def save(self):
        session.add(self)
        try:
            session.commit()
            return self

        except RuntimeError as error:
            logging.exception(error)
            return None
        except IntegrityError as error:
            logging.exception(error)
            return None

    def check_uniqueness(self, phone, taxid):
        doctor = self.query.filter(
            and_(
                Doctor.full_name.like(self.full_name),
                Doctor.gender.ilike(self.gender),
                Doctor.birth_date.ilike(self.birth_date),
            )
        ).one_or_none()
        if doctor:
            if check_password_hash(doctor.phone, phone) or check_password_hash(
                doctor.nif, taxid
            ):
                return doctor
            return None

    def delete(self):
        session.delete(self)
        session.commit()

    def find_all(self, criteria: any, *args, **kwargs):
        # criterion => speciality | location | mode | [speciality, location]
        # args => speciality_name | location | doctor_name | all
        doctors = self.query.all()
        if len(doctors) == 0:
            return None
        if criteria == "speciality-only":
            speciality = Speciality().getby_title(title=kwargs["title"])
            if speciality:
                return speciality.doctors
            return None
        if criteria == "location-only":
            address = Address().getby_city(name=kwargs["city"], entity=self)
            if address:
                return address.doctors
            return None
        if criteria == "mode-only":
            doctors = self.query.filter(Doctor.mode == kwargs["mode"])
            if doctors:
                return doctors
            return None
        if criteria.__contains__("speciality-location"):
            doctors = self.query.filter(
                and_(Doctor.addresses.city == kwargs["city"]),
                and_(Doctor.specialities.title == kwargs["title"]),
            ).all()
            if doctors:
                return doctors
            return None

        if criteria == "speciality-location-mode":
            doctors = self.query.filter(
                and_(Doctor.addresses.city == kwargs["city"]),
                and_(Doctor.specialities.title == kwargs["title"]),
                and_(Doctor.mode.contains(kwargs["mode"])),
            ).all()
            if doctors:
                return doctors
            return None

        if criteria == "none":
            return self.query

    #
# @classmethod
    # def link_speciality(self, specialities: any):

    #     for speciality in specialities:

    #         check = Speciality(
    #             title=speciality["title"], description=speciality["description"]
    #         ).save()
    #         try:
    #             if check:
    #                 return check.doctors.append(self)

    #             else:
    #                 new_speciality = Speciality(
    #                     title=speciality["title"], description=speciality["description"]
    #                 ).save()
    #                 # new_speciality.save()
    #                 return new_speciality.doctors.append(self)

    #         except RuntimeError as error:

    #             return None

    # @classmethod
    # def link_addresses(self, address: any):

    #     member_address = Address(
    #         street_name=address["streetname"],
    #         door_number=address["doornumber"],
    #         zipcode=address["zipcode"],
    #         city=address["city"],
    #         state=address["state"],
    #         country=address["country"],
    #     )
    #     try:
    #         if member_address.save() is not None:
    #             return member_address
    #         else:
    #             return None
    #     except RuntimeError as e:
    #         print(e)
    #         return None

    # @classmethod
    # def link_licenses(self, licenses: dict):
    #     results = []
    #     session.bulk_insert_mappings(License, licenses)
    #     session.commit()

    #     for license in licenses:
    #         check_create = License().findby_code(license["code"])

    #         try:
    #             if check_create is not None:
    #                 # check_create.doctors.append(self)
    #                 results.append(check_create)
    #         except RuntimeError as e:
    #             print(e)
    #             return None
    #     return results

    def retrieve_profile(self, identity):
        return self.query.filter(Doctor.nif.like(identity)).one_or_none()

    def associate_beneficiary(self, beneficiary: Beneficiary):
        session.add(self)
        try:
            self.beneficiaries.append(beneficiary)
            session.commit()
            return True
        except RuntimeError as error:
            return False

    def disassociate_beneficiary(self, beneficiary: dict):
        session.add(self)

        try:
            for ben in self.beneficiaries:
                if check_password_hash(ben.phone, beneficiary.get("phone")):
                    self.beneficiaries.remove(ben)
                    session.add(ben)
                    ben.delete()
            session.flush()
            # self.beneficiaries.remove(beneficiary)
            return True
        except RuntimeError as error:
            logging.exception(error, stack_info=True)
            return False


class Speciality(dbase.Model):
    __tablename__ = "speciality"
    __bind_key__ = "profiles"
    __table_args__ = {"extend_existing": True}

    id = Column(Integer, primary_key=True)
    title = Column(String(55), unique=True, nullable=False)
    description = Column(Text)
    # doctor_id = Column(Integer, ForeignKey("doctor.id", ondelete="CASCADE"))

    def __init__(self, **kwargs):
        self.title = initializer("title", kwargs)
        self.description = initializer("description", kwargs)
        self.doctor_id = initializer("doctor_id", kwargs)

    def save(self):
        speciality = self.getby_title(self.title)
        if speciality is None:
            session.add(self)
            try:
                session.commit()
                return self
            except RuntimeError as error:
                logging.exception(e, stack_info=True)
                session.rollback()
                return None
        else:
            return speciality

    def save_with_practitioner(self, practitioner=None):
        speciality = self.save()
        if practitioner and speciality:
            try:
                session.add(practitioner)
                speciality.doctors.append(practitioner)
                session.add(speciality)
                session.commit()
                return speciality
            except RuntimeError as error:
                logging.exception(error, exc_info=True)
                return None

    def getby_title(self, title):
        return self.query.filter(Speciality.title.like(title)).first()

    def getby_id(self, spec_id: any):
        return self.query.get(spec_id).all()

    def get_all(self):
        specialities = self.query
        return specialities.count(), specialities.all()


class License(dbase.Model):
    __tablename__ = "license"
    __bind_key__ = "profiles"
    __table_args__ = {"extend_existing": True}

    id = Column(Integer, primary_key=True)
    code = Column(String(128), unique=True, nullable=False)  # Encrypted
    issue_date = Column(String(55))
    end_date = Column(String(55))
    issuingorg = Column(Text, nullable=False, default="Office LLC")
    issuingcountry = Column(Integer, ForeignKey("country.id"), nullable=False)
    certificate = Column(
        Text, default="/media/profiles/licenses/certificate.pdf", nullable=False
    )  # Image path Encrypted
    doctor_id = Column(Integer, ForeignKey("doctor.id", ondelete="CASCADE"))

    def __init__(self, **kwargs):
        self.code = initializer("code", kwargs)
        self.issue_date = initializer("issuedate", kwargs)
        self.end_date = initializer("enddate", kwargs)
        self.issuingorg = initializer("issuingorg", kwargs)
        self.country = initializer("issuingcountry", kwargs)
        self.certificate = initializer("certificate", kwargs)
        self.doctor_id = initializer("doctor_id", kwargs)

    def save(self):
        license = self.findby_code(self.code)
        if license is None:
            country = Country(name=self.country).find_by(criterion="name")
            if country is None:
                country_id = country.save()
                if country_id:
                    self.issuingcountry = country_id
            else:
                self.issuingcountry = country.id
            session.add(self)
            try:
                session.commit()
                return self
            except RuntimeError as error:
                logging.exception(error, stack_info=True)
                return None
        else:
            return license

    def save_with_licensee(self, licensee=None):
        license = self.save()
        if licensee:
            licensee.licences.append(license)
            session.commit()
            return license
        return license

    def getby_doctid(self, id):
        return self.query.filter(self.doct_id == id)

    def findby_code(self, code):
        return self.query.filter(License.code.like(code)).first()


class Country(dbase.Model):
    __tablename__ = "country"
    __bind_key__ = "profiles"
    __table_args__ = {"extend_existing": True}

    id = Column(Integer, primary_key=True)
    name = Column(String(128), nullable=False, unique=True)
    country_code = Column(String(2))
    addresses = relationship("Address", back_populates="country")

    def __init__(self, **kwargs):
        self.name = initializer("name", kwargs)
        self.country_code = initializer("ccode", kwargs)

    def save(self):
        country = self.query.filter(Country.name.ilike(self.name)).one_or_none()
        if country:
            return country.id
        session.add(self)
        try:
            session.commit()
            return self.id
        except RuntimeError as error:
            logging.exception(error)
            session.rollback()
            return None

    def delete(self):
        session.delete(self)
        try:
            session.flush(self)
            return 1
        except:
            return 0

    def find_by(self, criterion: any):
        if criterion == "id":
            country = Country.query.filter(Country.id == self.id).first()
        if criterion == "code":
            country = Country.query.filter(
                Country.country_code.like(self.country_code)
            ).first()

        if criterion == "name":
            country = Country.query.filter(Country.name.like(self.name)).first()

        if country is None:
            self.save()
            return self

        return country

    def bind_address(self, address):
        country = self.find_by(criterion="name")
        if country is None:
            return None
        country.addresses.append(address)
        return country


class Address(dbase.Model):
    __tablename__ = "address"
    __bind_key__ = "profiles"
    __table_args__ = {"extend_existing": True}

    id = Column(Integer, primary_key=True)
    street_name = Column(String(128))
    door_num = Column(String(55))
    state = Column(String(55))
    zipcode = Column(String(55))
    city = Column(String(55))
    country_id = Column(Integer, ForeignKey("country.id"))
    country = relationship(Country, foreign_keys=[country_id])

    def __init__(self, **kwargs) -> None:
        self.street_name = initializer("streetname", kwargs)
        self.door_num = initializer("doornumber", kwargs)
        self.zipcode = initializer("zipcode", kwargs)
        self.state = initializer("state", kwargs)
        self.city = initializer("city", kwargs)
        self.country_ = initializer("country", kwargs)

    def save(self):
        check = self.getby_number_zipcode_street()
        if check:
            return check

        session.add(self)
        try:
            country = Country(name=self.country_).bind_address(address=self)
            if country is not None:
                self.country = country
            session.commit()
            return self
        except RuntimeError as error:
            # logging.exception(error, stack_info=True)
            print(error)

            return None

    def save_with_resident(self, resident=None):
        address = self.save()
        if resident and address:
            try:
                session.add(address)
                if isinstance(resident, Doctor):
                    address.doctors.append(resident)
                if isinstance(resident, Beneficiary):
                    address.beneficiaries.append(resident)
                session.commit()
                return address
            except:
                return None

    def getby_number_zipcode_street(self):
        return self.query.filter(
            and_(
                Address.door_num.ilike(self.door_num),
                Address.zipcode.ilike(self.zipcode),
                Address.street_name.ilike(self.street_name),
            )
        ).one_or_none()

    def getby_city(self, name, entity: None):
        addresses = self.query.filter(Address.city.like(name)).all()
        if entity is None:
            return addresses
        else:
            return self.fetch_by(entity, addresses)

    def getby_zipcode(self, code, entity=None):
        addresses = self.query.filter(Address.zipcode.like(code))
        if entity is None:
            return addresses
        else:
            return self.fetch_by(entity, addresses)

    def fetch_by(self, entity, addresses):
        if entity.role == "doctor":
            addresses = (
                addresses.from_self()
                .join(addresses.doctors)
                .join(DoctorMorada)
                .filter(
                    and_(
                        addresses.id == DoctorMorada.address_id,
                        Doctor.id == DoctorMorada.doctor_id,
                    )
                )
            )
            return addresses

        if entity.role == "beneficiary":
            addresses = (
                addresses.from_self()
                .join(addresses.beneficiaries)
                .join(BeneficiaryMorada)
                .filter(
                    and_(
                        addresses.id == BeneficiaryMorada.address_id,
                        Beneficiary.id == BeneficiaryMorada.beneficiary_id,
                    )
                )
            )
            return addresses

    def delete(self):
        session.delete(self)
        try:
            session.flush(self)
            return 1
        except:
            return 0
