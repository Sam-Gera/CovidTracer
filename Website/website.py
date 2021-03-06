from flask import Flask, redirect, url_for, render_template, request, flash, session
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, TextAreaField
from wtforms.validators import InputRequired, Email, Length
from flask_googlemaps import GoogleMaps, Map
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import requests

app = Flask(__name__)
app.config["SECRET_KEY"] = "test"
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///users.sqlite3"
Bootstrap(app)
db = SQLAlchemy(app)
db_s = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

list_of_markers = []

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(), unique=True)
    email = db.Column(db.String(50), unique=True)
    password = db.Column(db.String(80))

class Survey(db_s.Model):
    __tablename__ = "survey_table"

    name = db_s.Column(db.String(50), unique=True, primary_key=True)
    age = db_s.Column(db.String(3), primary_key=True)
    sex = db_s.Column(db.String(8), primary_key=True)
    pgph = db_s.Column(db.String(1000), primary_key=True)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class LoginForm(FlaskForm):
    username = StringField("Username", validators=[InputRequired(), Length(min=4, max=15)])
    password = PasswordField("Password", validators=[InputRequired(), Length(min=8, max=80)])
    remember = BooleanField("Remember me")

class RegisterForm(FlaskForm):
    email = StringField("Email", validators=[InputRequired(), Email(message="Invalid email"), Length(max=50)])
    username = StringField("Username", validators=[InputRequired(), Length(min=4, max=15)])
    password = PasswordField("Password", validators=[InputRequired(), Length(min=8, max=80)])

class SurveyInput(FlaskForm):
    name = StringField("Name (first and last)", validators=[InputRequired(), Length(min=1, max=30)])
    age = StringField("Age", validators=[InputRequired(), Length(min=1, max=2)])
    sex = StringField("Biological sex (m or f)", validators=[InputRequired(), Length(min=1, max=1)])
    pgph = TextAreaField("-->")
# Google Maps
app.config['GOOGLEMAPS_KEY'] = "AIzaSyCoMJFQnPrxQf4Y4XBmJIYmd0_ER0lncV4"

#Initialize etension
GoogleMaps(app)

@app.route("/home")
def home():
    return render_template("home.html")

@app.route('/')
def index():
    return render_template("index.html")

@app.route("/login", methods=["POST", "GET"])
def login():
    form = LoginForm()

    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user:
            if check_password_hash(user.password, form.password.data):
                login_user(user, remember=form.remember.data)
                return redirect(url_for("dashboard"))
        return "<h1>Invalid username or password</h1>"

    return render_template("login.html", form=form)

@app.route('/signup', methods=["POST", "GET"])
def signup():
    form = RegisterForm()

    if form.validate_on_submit():
        hashed_password = generate_password_hash(form.password.data, method='sha256')
        new_user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        return '<h1>New user has been created!</h1>'
    return render_template("signup.html", form=form)

@app.route("/dashboard", methods=["POST", "GET"])
@login_required
def dashboard():
    form = SurveyInput()

    if form.validate_on_submit():
        new_survey = Survey(name=form.name.data, age=form.age.data, sex=form.sex.data, pgph=form.pgph.data)
        db.session.add(new_survey)
        db.session.commit()
        return '<h1>New survey has been submitted!</h1>'

    return render_template("dashboard.html", form=form)

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))

@app.route("/maps")
def mapview():

    def extract_lat_long_via_address(address_or_zipcode):
        lat, lng = None, None
        api_key = 'AIzaSyCoMJFQnPrxQf4Y4XBmJIYmd0_ER0lncV4'
        base_url = "https://maps.googleapis.com/maps/api/geocode/json"
        endpoint = f"{base_url}?address={address_or_zipcode}&key={api_key}"
        # see how our endpoint includes our API key? Yes this is yet another reason to restrict the key
        r = requests.get(endpoint)
        if r.status_code not in range(200, 299):
            return None, None
        try:
            '''
            This try block incase any of our inputs are invalid. This is done instead
            of actually writing out handlers for all kinds of responses.
            '''
            results = r.json()['results'][0]
            lat = results['geometry']['location']['lat']
            lng = results['geometry']['location']['lng']
        except:
            pass
        return lat, lng

    # Creating map
    sndmap = Map(
        identifier="sndmap",
        lat=40.760648,
        lng=-111.871201,
        zoom=15,
        style="height:900px;width:900px;margin:30;",
        markers=[
          {
             'icon': 'http://maps.google.com/mapfiles/ms/icons/green-dot.png',
             'lat': 40.759805,
             'lng': -111.875865,
             'infobox': "<b>Risk Rating: 20<br>Address: 455 S 500 E, Salt Lake City, UT 84102</b>"
          },
          {
             'icon': 'http://maps.google.com/mapfiles/ms/icons/yellow-dot.png',
             
             'lat': 40.761186,
             'lng': -111.878751,
             'infobox': "<b>Risk Rating: 52<br>Address: 421 E 400 S, Salt Lake City, UT 84111</b>"
          },
          {
             'icon': 'http://maps.google.com/mapfiles/ms/icons/green-dot.png',
             
             'lat': 40.765543,
             'lng': -111.880104,
             'infobox': "<b>Risk Rating: 4<br>Address: 377 E 200 S, Salt Lake City, UT 84111</b>"
          },
          {
             'icon': 'http://maps.google.com/mapfiles/ms/icons/green-dot.png',
             
             'lat': 40.763966,
             'lng': -111.876278,
             'infobox': "<b>Risk Rating: 28<br>Address: 241 500 E, Salt Lake City, UT 84102</b>"
          },
          {
             'icon': 'http://maps.google.com/mapfiles/ms/icons/red-dot.png',
             
             'lat': 40.764129,
             'lng': -111.883091,
             'infobox': "<b>Risk Rating: 74<br>Address: 250 S 300 E, Salt Lake City, UT 84111</b>"
          }
        ]
    )
    return render_template('maps.html', sndmap=sndmap)

if __name__=="__main__":
    db.create_all()
    app.run(debug=True)
