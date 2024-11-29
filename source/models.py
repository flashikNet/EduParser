from sqlalchemy.ext.declarative import DeclarativeMeta, declarative_base
from sqlalchemy import Column, Integer, String

Base: DeclarativeMeta = declarative_base()


class Sneaker(Base):
    __tablename__ = "sneakers"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    price = Column(String, nullable=False)
    brand = Column(String, nullable=False)
