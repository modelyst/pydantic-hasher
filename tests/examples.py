from typing import Optional
from pydantic import BaseModel


class Address(BaseModel):
    number: str
    street: str


class Person(BaseModel):
    first_name: str
    last_name: str
    nickname: Optional[str]
    address: Optional[Address]


class Book(BaseModel):
    title: str
    author: Person
    publication_year: int


class BookWithPrice(BaseModel):
    _hashexclude_ = {"price"}
    title: str
    author: Person
    publication_year: int
    price: float
