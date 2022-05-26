import requests
import string
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy

DB_NAME = 'weather.db'

app = Flask(__name__)

app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_NAME}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'webuildthistown'


db = SQLAlchemy(app)

class City(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)




@app.route('/')
def index_get():
    cities = City.query.all()
    weather_data = []

    for city in cities:  # select city from cities from db.
        req = get_weather_data(city.name)  # getting data from json

        weather = {
            'city': city.name,
            'temperature': req['main']['temp'],
            'description': req['weather'][0]['description'],
            'icon': req['weather'][0]['icon'],
        }

        weather_data.append(weather)
    return render_template('index.html', weather_data=weather_data)


@app.route('/', methods=['POST'])
def index_post():
    err_msg = ''
    new_city = request.form.get('city')
    new_city = new_city.lower()
    new_city = string.capwords(new_city)

    if new_city:
        existing_city = City.query.filter_by(name=new_city).first()  # filtracia ci to existuje

        if not existing_city:
            new_city_data = get_weather_data(new_city)
            if new_city_data['cod'] == 200:
                new_city_object = City(name=new_city)

                db.session.add(new_city_object)
                db.session.commit()
            else:
                print('this is not a valid city')
        else:
            print('City already exists in the database!')

    if err_msg:
        print('error', err_msg)
    else:
        print('City added successfully!')
    return redirect(url_for('index_get'))


#################################FUNCTIONS#############################################

def get_weather_data(city):
    weather_link = f"http://api.openweathermap.org/data/2.5/weather?q={city}&units=metric&appid=b21a2633ddaac750a77524f91fe104e7"
    req = requests.get(weather_link).json()
    return req


@app.route('/delete/<name>')
def delete_city(name):
    city = City.query.filter_by(name=name).first()
    db.session.delete(city)
    db.session.commit()
    print('City deleted successfully!' + city.name)
    return redirect(url_for('index_get'))
