from flask_sqlalchemy import SQLAlchemy
import enum

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.Text(), nullable=False)
    subscriptions = db.relationship("Subscription")

    def __repr__(self):
        return '<User %r>' % self.full_name

class Recurrence(enum.Enum):
    weekly = 1
    monthly = 2
    yearly = 3

class Subscription(db.Model):
    __tablename__ = "subscriptions"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text, nullable=False)
    subscribed_on = db.Column(db.DateTime, nullable=False)
    price = db.Column(db.Numeric(precision=2), nullable=False)
    recurrence = db.Column(db.Enum(Recurrence), nullable=False)
    icon = db.Column(db.Text)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    def __repr__(self):
        return  '<Subscription id={id} name={name} subscribed_on={subscribed_on} price={price} recurrence={recurrence} icon={icon} user_id={user_id}>'.format(id=id, name=name, subscribed_on=subscribed_on, price=price, recurrence=recurrence, icon={icon}, user_id=user_id )

