# -*- coding: utf-8 -*-

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy import Column, Integer, String, Date, ForeignKey

Base = declarative_base()

class Key(Base):
    __tablename__ = 'keys'

    id = Column(Integer, primary_key=True)
    fingerprint = Column(String, unique=True)
    algo = Column(String)
    created = Column(Date)
    usage = Column(String)
    expiry = Column(Date)
    email = Column(String)
    name = Column(String)
    description = Column(String)

    def __repr__(self):
        return 'pub   {} {} [{}]{}\n      {}\nuid           {} {}<{}>'.format(
            self.algo, self.created, self.usage,
            ' [expires: {}]'.format(self.expiry) if self.expiry else '',
            self.fingerprint, self.name,
            '({}) '.format(self.description) if self.description else '',
            self.email
        )

class Signature(Base):
    __tablename__ = 'signatures'

    id = Column(Integer, primary_key=True)
    key_id = Column(Integer, ForeignKey('keys.id'))
    signer_key = Column(String)
    sign_date = Column(Date)
    signer_name = Column(String)
    signer_email = Column(String)

    key = relationship('Key', backref='sigs')

    def __repr__(self):
        return 'sig          {} {}  {}'.format(
            self.signer_key, self.sign_date,
            '{} <{}>'.format(self.signer_name, self.signer_email) if self.signer_name else '[User ID not found]'
        )

def init_db():
    engine = create_engine('sqlite:///gpg.db', echo=False)
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    return Session()
