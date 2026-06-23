from sqlalchemy import create_engine, text
from dotenv import load_dotenv
import os

load_dotenv()

engine = create_engine(os.getenv("DATABASE_URL"))

with engine.connect() as conn:
    result = conn.execute(text("SELECT 1"))
    print("Jarvis says connection completed!", result.fetchone())

########################################################################
# Got code from https://docs.sqlalchemy.org/en/20/orm/quickstart.html#declare-models
# Remember to convert from SQL Lite for tmrw
from typing import List
from typing import Optional
from sqlalchemy import ForeignKey
from sqlalchemy import String
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship

class Base(DeclarativeBase):
    pass

class restaurants(Base):
    __tablename__ = "restaurants"
    restaurant_id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(30))
    location: Mapped[str] = mapped_column(String(30))
    region: Mapped[str]= mapped_column(String(30))
    menu_items: Mapped[List["menu_items"]] = relationship(
        back_populates="restaurant", cascade="all, delete-orphan"
    )
    transactions: Mapped[List["transactions"]] = relationship(
        back_populates="restaurant", cascade="all, delete-orphan"
    )
    def __repr__(self) -> str:
        return f"restaurant(id={self.restaurant_id!r}, name={self.name!r}, location={self.location!r}, region={self.region})"

class menu_items(Base):
    __tablename__ = "menu_items"
    name: Mapped[str] = mapped_column(String(30))
    PLU: Mapped[int] = mapped_column(primary_key=True)
    restaurant_id: Mapped[int] = mapped_column(ForeignKey("restaurants.restaurant_id"))
    base_cost: Mapped[int] 
    food_type: Mapped[str] = mapped_column(String(30))
    restaurant: Mapped["restaurants"] = relationship(back_populates="menu_items")
    transaction_items: Mapped[List["transaction_items"]] = relationship(
        back_populates="menu_item", cascade="all, delete-orphan"
    )
    price_history: Mapped[List["price_history"]] = relationship(
        back_populates="menu_item", cascade="all, delete-orphan"
    )
    def __repr__(self) -> str:
        return f"name(id={self.name!r}, PLU={self.PLU!r}, restaurant_id={self.restaurant_id}, base_cost={self.base_cost}, food_type={self.food_type})"

class transactions(Base):
    __tablename__ = "transactions"
    transaction_id: Mapped[int] = mapped_column(primary_key=True)
    restaurant_id: Mapped[int] = mapped_column(ForeignKey("restaurants.restaurant_id"))
    amount: Mapped[int] 
    day: Mapped[int] 
    year: Mapped[int] 
    TOT: Mapped[int] 
    restaurant: Mapped["restaurants"] = relationship(back_populates="transactions")
    transaction_items: Mapped[List["transaction_items"]] = relationship(
        back_populates="transaction", cascade="all, delete-orphan"
    )
    def __repr__(self) -> str:
        return f"transaction_id(id={self.transaction_id!r}, restaurant_id={self.restaurant_id!r}, amount={self.amount}, amount={self.amount}, day={self.day}, year={self.year}, TOT={self.TOT})"

class transaction_items(Base):
    __tablename__ = "transaction_items"
    id: Mapped[int] = mapped_column(primary_key=True)
    restaurant_id: Mapped[int] = mapped_column(ForeignKey("restaurants.restaurant_id"))
    transaction_id: Mapped[int] = mapped_column(ForeignKey("transactions.transaction_id"))
    PLU: Mapped[int] = mapped_column(ForeignKey("menu_items.PLU"))
    price_ats: Mapped[int] 
    quantity: Mapped[int] 
    transaction: Mapped["transactions"] = relationship(back_populates="transaction_items")
    menu_item: Mapped["menu_items"] = relationship(back_populates="transaction_items")
    def __repr__(self) -> str:
        return f"id={self.id!r}, restaurant_id={self.restaurant_id!r}, transaction_id={self.transaction_id}, PLU={self.PLU}, price_ats={self.price_ats}, quantity={self.quantity})"

class price_history(Base):
    __tablename__ = "price_history"
    price_id: Mapped[int] = mapped_column(primary_key=True)
    PLU: Mapped[int] = mapped_column(ForeignKey("menu_items.PLU"))
    price: Mapped[int] 
    effective_date: Mapped[str] 
    change_reason: Mapped[str]
    menu_item: Mapped["menu_items"] = relationship(back_populates="price_history")
    def __repr__(self) -> str:
        return f"price_id={self.restaurant_id!r}, PLU={self.PLU}, price={self.price}, effective_date={self.effective_date}, change_reason={self.change_reason})"

Base.metadata.create_all(engine)
print("Jarvis - TABLES HAVE BEEN CREATED!!")