from flask import Flask, render_template, request, redirect, url_for, flash
from wtforms import Form, StringField, TextAreaField, EmailField, validators, SelectField
from smtplib import SMTP
from sqlalchemy import create_engine
import pandas as pd
import mysql.connector

app = Flask(__name__)
app.secret_key = "CS210"
# Configure the database connection
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'cs210devam'

# Create a MySQL connection
mysql_conn = mysql.connector.connect(
    host=app.config['MYSQL_HOST'],
    user=app.config['MYSQL_USER'],
    password=app.config['MYSQL_PASSWORD'],
    database=app.config['MYSQL_DB']
)
if mysql_conn.is_connected():
    print("connected")

#Kullanıcı İletişim Formu
class ContactForm(Form): 
    fname = StringField(label="First Name", validators=[validators.DataRequired(message="Please enter your name")])
    lname = StringField(label = "Last Name", validators=[validators.DataRequired(message="Please enter your last name")])
    email = EmailField(label="Email", validators=[validators.DataRequired()])
    message = TextAreaField(label="Your message to us", validators=[validators.DataRequired(message="Please enter your message")])

class AnalysisForm(Form):
    years = [2006, 2007, 2008, 2009, 2010, 2011, 2012, 2013, 2014, 2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022]
    bigdata = ["Guilty Kids Based Reason of Arrive and Gender", "Guilty Kids Based Reason of Arrive Age and Gender", "Accused Kids Based Type of Accusation and Gender", "Gender of Kids Reason and Crime Grievance", "Judgements Based on the Education Level", "Number of Released People Based on the Education Level", "Judgements Based on the Year-Gender", "Judgements Based on the Type of the Crime-Race", "Released People Based on Type of Crime-Race", "Poorness Based On the Education Levels", "Poorness Rate Based on the Education Level"]
    subject = SelectField(choices=bigdata, label="Please select your main subject to search", validators=[validators.DataRequired()])
    year = SelectField(choices=years, label="Please select your year", validators=[validators.DataRequired()])

@app.route("/")
def home():
    alert_message = "This website is just an introduction for the team and project. If you want to analyze the all datasets, download and run XAMPP, start Apache and MySQL services, go to phpmyadmin page for MySQL, and then visit: 'https://github.com/kutluhaan/Analyze-Turkey.git' to download the files. Run all ipynb files and finally run 'page-control.py'."
    return render_template("index.html", alert_message=alert_message)

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/data_analysis", methods =["GET", "POST"])
def analysis():
    data = "No data selected"
    header= ""
    form =AnalysisForm(request.form)
    if request.method == "POST":
        subject = form.subject.data
        year = form.year.data
        header = f"{subject} {year}"
        subject = subject.replace(" ", "").lower()
        name = f"{subject}{year}" 
        query = f"SELECT * FROM {name}"
        try:
            result_df = pd.read_sql(query, con=mysql_conn)
            data = result_df.to_html(index=False)
        except: 
            data="No such table"
        flash("Success", "success")
    return render_template("data_analysis.html", form=form, data=data, header=header)

@app.route("/contact", methods =["GET", "POST"])
def contact():
    form = ContactForm(request.form)
    if request.method == "POST":
        first_name = form.fname.data
        last_name = form.lname.data
        email = form.email.data
        message  = form.message.data
        print(f"Your name is {str(first_name)} {str(last_name)} {str(message)} {str(email)}")
        flash("Success", "success")
        name = "{0} {1}".format(first_name, last_name)
        sendmail(name = name, subject="Yeni İletişim İsteği", message=message)
        return redirect(url_for("home"))
    else:
        return render_template("contact.html", form=form)

def sendmail(name, subject, message):
    content = "Subject: {0} \n\n {1} \n\n {2}".format(subject, message, name)
    myaddress = "kutluhan@sabanciuniv.edu"
    mypassword = "1453Kutlu52"
    
    toemail = "kayguzel255@gmail.com"
    try:
        mail = SMTP("smtp.gmail.com", 587)
        mail.ehlo()
        mail.starttls()
        mail.login(myaddress, mypassword)
        mail.sendmail(myaddress, toemail, content.encode("utf-8"))
        print("Mail sent")
    except Exception as e:
        print("Something went wrong! \n {0}".format(e))
if __name__ == "__main__":
    app.run(debug=True)