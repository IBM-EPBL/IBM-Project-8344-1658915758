from flask import Flask, request, render_template,url_for,session
from flask_session import Session
from flask_session_captcha import FlaskSessionCaptcha
from flask import flash
from flask_sqlalchemy import SQLAlchemy
import mysql.connector
import pickle
import requests
import re


API_KEY = "R5J30FLYA5TDQOMfOB-GJY8_aaMH_SjellNkZXd8qQbW"
token_response = requests.post('https://iam.cloud.ibm.com/identity/token', data={"apikey":
API_KEY, "grant_type": 'urn:ibm:params:oauth:grant-type:apikey'})
mltoken = token_response.json()["access_token"]

header = {'Content-Type': 'application/json', 'Authorization': 'Bearer ' + mltoken}


db = mysql.connector.connect(host="127.0.0.1",
                             port="3307",
                             user="root",
                             password="Shansk@12",
                             database="lpsystem")


flask_app = Flask(__name__)
model = pickle.load(open("ml_model.pkl", "rb"))

flask_app.secret_key='R5J30FLYA5TDQOMfOB-GJY8_aaMH_SjellNkZXd8qQbW'



@flask_app.route('/')
def index():

    return render_template("index.html")

@flask_app.route('/login', methods =['GET', 'POST'])
def login():
    if (request.method == 'POST'):
        name = request.form.get('name')
        password = request.form.get('password')
        cursor = db.cursor(buffered=True)
        sql='SELECT * FROM users'
        cursor.execute(sql)
        account = cursor.fetchone()
        if account:
            session["loggedin"] = True
            session['id'] = account[1]
            return render_template("predict.html")
            
        flash('Wrong username or password', 'error')
        return render_template("login.html")

    return render_template("login.html")

@flask_app.route('/register', methods =['GET', 'POST'])
def register():
    if (request.method == 'POST'):
        name = request.form.get('name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        password = request.form.get('password')
        repassword = request.form.get('confirmpassword')
        
        if (password!=repassword):
            flash("Passwords don't match", 'error')
        else:
            cursor = db.cursor()
            cursor.execute('SELECT * FROM users WHERE email= % s', (email, ))
            account = cursor.fetchone()
            if account:
                flash('User already registered', 'error')
                return render_template("register.html")
            else:  
                cursor.execute('INSERT INTO users VALUES (% s, % s, % s, % s)', (name, email, phone, password, ))
                db.commit()
                return render_template("login.html")

    return render_template("register.html")


@flask_app.route('/predict', methods=["GET", "POST"])
def predict():
    if request.method == "POST":
        name = request.form['name']
        gender = request.form['gender']
        married = request.form['married']
        dependents = request.form['dependents']
        education = request.form['education']
        employment = request.form['employment']
        applicant_income = request.form['applicant_income']
        coapplicant_income = request.form['coapplicant_income']
        loan_amount = request.form['loan_amount']
        loan_amount_term = request.form['loan_amount_term']
        credit_history = request.form['credit_history']
        prop_area = request.form['prop_area']

        if gender == 'Male':
            gender = 1
        else:
            gender = 0

        if married == 'Yes':
            married = 1
        else:
            married = 0

        if dependents == '0':
            dependents = 0
        elif dependents == '1':
            dependents = 1
        elif dependents == '2':
            dependents = 2
        else:
            dependents = 3

        if education == 'Graduate':
            education = 0
        else:
            education = 1

        if employment == 'Yes':
            employment = 1
        else:
            employment = 0

        if prop_area == 'Rural':
            prop_area = 0
        elif prop_area == 'Semiurban':
            prop_area = 1
        else:
            prop_area = 2

        applicant_income = float(applicant_income)
        coapplicant_income = float(coapplicant_income)
        loan_amount = float(loan_amount)
        loan_amount_term = float(loan_amount_term)

        prediction = model.predict([[gender, married, dependents, education, employment, applicant_income,
                                     coapplicant_income, loan_amount, loan_amount_term, credit_history, prop_area]])

        if prediction == 'Y':
            prediction = "Congrats {}, You are eligible to apply for loan".format(name)
        else:
            prediction = "Sorry {}, You are ineligible to apply for loan".format(name)

        return render_template('result.html', prediction_text='{}'.format(prediction))

    else:
        return render_template('predict.html')

if __name__ == "__main__":
    flask_app.run(debug=True)
