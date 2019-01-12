#!/usr/bin/env python2.7

import datetime
from sqlalchemy import Column, ForeignKey, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy import create_engine


Base = declarative_base()


class Category(Base):
    __tablename__ = 'category'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(250), nullable=False)

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {
            'id': self.id,
            'name': self.name
        }


class Item(Base):
    __tablename__ = 'item'

    id = Column(Integer, primary_key=True, autoincrement=True)
    category_id = Column(Integer, ForeignKey('category.id'))
    user_email = Column(String(250), nullable=False)
    title = Column(String(250), nullable=False)
    description = Column(String(500))
    price = Column(Integer)
    date_posted = Column(DateTime, default=datetime.datetime.now())

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {
            'id': self.id,
            'user_email': self.user_email,
            'title': self.title,
            'description': self.description,
            'price': self.price,
            'date_posted': self.date_posted
        }


engine = create_engine('sqlite:///catalog.db')


Base.metadata.create_all(engine)
