import os
from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from helpers import predict_1
import threading
from datetime import datetime, timedelta
import pause
import json
import plotly.express as px
import plotly.utils as pu


STOCKS = ['AAPL', 'MSFT', 'AMZN', 'NVDA', 'TSLA', 'GOOGL', 'META', 'GOOG', 'BRK-B', 'UNH']

basedir = os.path.abspath(os.path.dirname(__file__))

application = Flask(__name__)

application.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'database.db')

db = SQLAlchemy(application)


class Price(db.Model):
    __tablename__ = 'prices'

    id = db.Column(db.Integer, primary_key=True)
    day = db.Column(db.Date)
    price = db.Column(db.Double)
    model = db.Column(db.Integer)
    ticker = db.Column(db.String)
    predday = db.Column(db.Date)


def update_preds():
    with application.app_context():
        for stock in STOCKS:
            days, prices, today = predict_1(stock)
            for i, price in enumerate(prices):
                priceobj = Price(day=days[i], price=price, model=1, ticker=stock, predday=today - timedelta(days=1))
                db.session.add(priceobj)

        db.session.commit()


def update_thread():
    day = datetime.today().replace(hour=16, minute=30, second=0, microsecond=0)
    while True:
        update_preds()
        day = day + timedelta(days=1)
        pause.until(day)


@application.route('/')
def index():
    return render_template('index.html')


@application.route('/models/<model>')
def models(model):
    today = datetime.today().strftime('%Y-%m-%d')
    day = datetime.today() - timedelta(days=1)
    day = day.strftime('%Y-%m-%d')
    returnobj = {}
    for stock in STOCKS:
        returnobj[stock] = {'preds': {day: []}, 'graphs': {}}
        predictions = Price.query.filter_by(model=model, predday=day, ticker=stock).all()
        days, prices = [], []
        for pred in predictions:
            returnobj[stock]['preds'][day].append({'day': pred.day.strftime('%Y-%m-%d'), 'price': pred.price})
            days.append(pred.day.strftime('%Y-%m-%d'))
            prices.append(pred.price)
        fig = px.line(x=days, y=prices, labels=dict(x='Day', y='Price (USD)'), markers=True)
        returnobj[stock]['graphs'][day] = json.dumps(fig, cls=pu.PlotlyJSONEncoder)
    returnobj = json.dumps(returnobj)

    return returnobj


if __name__ == "__main__":
    thread = threading.Thread(target=update_thread)
    thread.start()
    with application.app_context():
        db.create_all()
    application.run()
