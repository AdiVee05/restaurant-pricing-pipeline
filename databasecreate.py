from sqlalchemy import create_engine, text
from dotenv import load_dotenv
import os

load_dotenv()

engine = create_engine(os.getenv("DATABASE_URL"))

with engine.connect() as conn:
    result = conn.execute(text("SELECT 1"))
    print("Jarvis says connection completed!", result.fetchone())

########################################################################
from datetime import datetime   # NEW
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
    restaurant_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=False)   # CHANGED
    store_number: Mapped[int]
    name: Mapped[str] = mapped_column(String(30))
    location: Mapped[str] = mapped_column(String(30))
    region: Mapped[str] = mapped_column(String(30))
    menu_items: Mapped[List["menu_items"]] = relationship(
        back_populates="restaurant", cascade="all, delete-orphan"
    )
    transactions: Mapped[List["transactions"]] = relationship(
        back_populates="restaurant", cascade="all, delete-orphan"
    )

class menu_items(Base):
    __tablename__ = "menu_items"
    name: Mapped[str] = mapped_column(String(30))
    PLU: Mapped[int] = mapped_column(primary_key=True, autoincrement=False)   # CHANGED
    restaurant_id: Mapped[int] = mapped_column(ForeignKey("restaurants.restaurant_id"))
    base_cost: Mapped[float]   # CHANGED (was int)
    food_type: Mapped[str] = mapped_column(String(30))
    restaurant: Mapped["restaurants"] = relationship(back_populates="menu_items")
    transaction_items: Mapped[List["transaction_items"]] = relationship(
        back_populates="menu_item", cascade="all, delete-orphan"
    )
    price_history: Mapped[List["price_history"]] = relationship(
        back_populates="menu_item", cascade="all, delete-orphan"
    )

class transactions(Base):
    __tablename__ = "transactions"
    transaction_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=False)   # CHANGED
    restaurant_id: Mapped[int] = mapped_column(ForeignKey("restaurants.restaurant_id"))
    amount: Mapped[float]   # CHANGED (was int)
    day: Mapped[int]
    month: Mapped[int]   # NEW
    year: Mapped[int]
    TOT: Mapped[int]
    restaurant: Mapped["restaurants"] = relationship(back_populates="transactions")
    transaction_items: Mapped[List["transaction_items"]] = relationship(
        back_populates="transaction", cascade="all, delete-orphan"
    )

class transaction_items(Base):
    __tablename__ = "transaction_items"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=False)   # CHANGED
    restaurant_id: Mapped[int] = mapped_column(ForeignKey("restaurants.restaurant_id"))
    transaction_id: Mapped[int] = mapped_column(ForeignKey("transactions.transaction_id"))
    PLU: Mapped[int] = mapped_column(ForeignKey("menu_items.PLU"))
    price_ats: Mapped[float]   # CHANGED (was int)
    quantity: Mapped[int]
    transaction: Mapped["transactions"] = relationship(back_populates="transaction_items")
    menu_item: Mapped["menu_items"] = relationship(back_populates="transaction_items")

class price_history(Base):
    __tablename__ = "price_history"
    price_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=False)   # CHANGED
    PLU: Mapped[int] = mapped_column(ForeignKey("menu_items.PLU"))
    price: Mapped[float]   # CHANGED (was int)
    effective_date: Mapped[datetime]   # CHANGED (was str)
    end_date: Mapped[Optional[datetime]]   # NEW (Optional because the current price has no end date)
    change_reason: Mapped[str] = mapped_column(String(50))   # CHANGED (gives it a length)
    menu_item: Mapped["menu_items"] = relationship(back_populates="price_history")

Base.metadata.create_all(engine)
print("Jarvis - TABLES HAVE BEEN CREATED!!")