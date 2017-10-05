"""Define DB tables.

PvConfiguration
PvConvigurationValue
"""
from sqlalchemy import Column, String, Integer, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship, backref
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class PvConfiguration(Base):
    """Define PvConfiguration table."""

    __tablename__ = "pv_configuration"

    id = Column(Integer, primary_key=True)
    name = Column(String(32), nullable=False, unique=True)
    config_type = Column(String(32), nullable=False)

    UniqueConstraint(name, config_type, "uc_2")

    @property
    def serialize(self):
        """Retrun object in easyly serializeable format."""
        return {
            'id': self.id,
            'name': self.name,
            'config_type': self.config_type
        }


class PvConfigurationValue(Base):
    """Define pv_configuration_value table."""

    __tablename__ = "pv_configuration_value"

    id = Column(Integer, primary_key=True)
    pv_name = Column(String(32), nullable=False)
    pv_type = Column(String(16), nullable=False)
    value = Column(String(255))
    pv_configuration_id = Column(Integer, ForeignKey('pv_configuration.id'))
    pv_configuration = relationship(PvConfiguration,
                                    backref=backref('values', uselist=True))

    UniqueConstraint(pv_configuration_id, pv_name, "uc_1")

    @property
    def serialize(self):
        """Retrun object in easyly serializeable format."""
        return {
            'id': self.id,
            'pv_name': self.pv_name,
            'pv_type': self.pv_type,
            'value': self.value,
            'config_id': self.pv_configuration_id
        }
