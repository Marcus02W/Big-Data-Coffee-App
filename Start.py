from sqlalchemy import Column, Integer, String, ForeignKey, Time
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class CoffeeShop(Base):
    __tablename__ = 'coffee_shops'
    shop_id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    city = Column(String, nullable=False)
    adress = Column(String, nullable=False)
    owner_firstname = Column(String, nullable=False)
    owner_lastname = Column(String, nullable=False)


class CoffeeType(Base):
    __tablename__ = 'coffee_types'
    type_id = Column(Integer, primary_key=True)
    coffee_type = Column(String)
    size = Column(String)


class CoffeeShopCoffeeType(Base):
    __tablename__ = 'coffee_shops_coffee_types'
    shop_id = Column(Integer, ForeignKey('coffee_shops.shop_id'), primary_key=True)
    type_id = Column(Integer, ForeignKey('coffee_types.type_id'), primary_key=True)


class Customer(Base):
    __tablename__ = 'customers'
    customer_id = Column(Integer, primary_key=True)
    customer_firstname = Column(String)
    customer_lastname = Column(String)


class CustomerLogin(Base):
    __tablename__ = 'customer_login'
    customer_id = Column(Integer, ForeignKey('customers.customer_id'), primary_key=True)
    customer_password = Column(String)


class Order(Base):
    __tablename__ = 'order'
    order_id = Column(Integer, primary_key=True)
    shop_id = Column(Integer, ForeignKey('coffee_shops.shop_id'))
    customer_id = Column(Integer, ForeignKey('customers.customer_id'))
    time = Column(Time)


class OrderItem(Base):
    __tablename__ = 'orderitem'
    type_id = Column(Integer, ForeignKey('coffee_types.type_id'), primary_key=True)
    number = Column(Integer)
    order_id = Column(Integer, ForeignKey('order.order_id'))


class Rating(Base):
    __tablename__ = 'ratings'
    rating_id = Column(Integer, primary_key=True)
    customer_id = Column(Integer, ForeignKey('customers.customer_id'))
    shop_id = Column(Integer, ForeignKey('coffee_shops.shop_id'))
    score = Column(Integer)


class ShopLogin(Base):
    __tablename__ = 'shop_login'
    shop_password = Column(String)
    shop_id = Column(Integer, ForeignKey('coffee_shops.shop_id'))
