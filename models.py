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
        return '<User id={0} full_name={1} email={2} >'.format(self.id, self.full_name, self.email)

class Recurrence(enum.Enum):
    weekly = 1
    monthly = 2
    yearly = 3

class Subscription(db.Model):
    __tablename__ = "subscriptions"
    id = db.Column(db.Integer, primary_key=True)
    service = db.Column(db.String(120), nullable=False)
    subscribed_on = db.Column(db.Date, nullable=False)
    recurrence = db.Column(db.Enum(Recurrence), nullable=False)
    price = db.Column(db.Numeric, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    def __repr__(self):
        return  "<Subscription id={0} service={1} subscribed_on={2} price={3} recurrence={4} user_id={5}>".format(self.id, self.service, self.subscribed_on, self.price, self.recurrence, self.user_id)

