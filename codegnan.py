 
from flask import Flask, request
import pandas as pd
import flasgger
from flasgger import Swagger
from flask_ngrok import run_with_ngrok
import sqlite3 as sql
from flask import jsonify
from flask import Response
import json
import hashlib
import smtplib 
from random import randint
import configparser
import sys

#Intializing the config file through the commandline argument
config = configparser.ConfigParser()
config.read('config.ini')
mail_id=config.get('mail','UserName')
mail_Password=config.get('mail','Password')
admin_name=config.get('admin','admin')


#Intializing FLASK App
app=Flask(__name__)
#Intializing flasgger which helps to creating the better interaction between enduser and Flask API 
Swagger(app)
#run_with_ngrok(app)

def create_database():
    """This function will be used for intializing Database and
       create the table 
    """
    try:
        conn = sql.connect('database.db')
        conn.execute('CREATE TABLE  IF NOT EXISTS users1(UserName TEXT PRIMARY KEY, Password TEXT, FullName TEXT, Email TEXT ,otp INT)')
        msg="Database connected."
    except:
        msg="Database Connection issue ."

    finally:
        conn.close()
    return msg 

def admin_access(UserName):
    """ This function can used by only ADMIN (vennam)
    """

    try:
        dict1={}
        print(UserName)
        conn = sql.connect('database.db')
        cur = conn.cursor()
        query="select * from users1"
        result = cur.execute(query)
        column_names = []
        return_list = []
        for row in result.description:
            column_names.append(row[0])
        result = result.fetchall()
        print(result)
        for res in range(len(result)):
            temp_dict = {}
            for col in range(len(column_names)):
                temp_dict.update({column_names[col]:result[res][col]})
            return_list.append(temp_dict)
            msg="fetched details successfully."
    except:
        msg="Error while fetchind details"

    finally:
        conn.close()
    return return_list


def otp_access(UserName):
    """This function can be used for validating OTP
       while changing Password
    """

    try:
        dict1={}
        print(UserName)
        conn = sql.connect('database.db')
        cur = conn.cursor()
        query=f"select * from users1 where UserName='{UserName}'"
        result = cur.execute(query)
        column_names = []
        return_list = []
        for row in result.description:
            column_names.append(row[0])
        result = result.fetchall()
        print(result)
        for res in range(len(result)):
            temp_dict = {}
            for col in range(len(column_names)):
                temp_dict.update({column_names[col]:result[res][col]})
            return_list.append(temp_dict)
            msg="fetched details successfully."
    except:
        msg="Error while fetchind details"
    finally:
        conn.close()
    return return_list



def fetch_details(UserName):
    """ This function fetch all details of enduser based on UserName and \
        returns the details as list
    """
    try:
        dict1={}
        print(UserName)
        conn = sql.connect('database.db')
        cur = conn.cursor()
        query=f"select UserName,Password,FullName,Email from users1 where UserName='{UserName}'"
        result = cur.execute(query)
        column_names = []
        return_list = []
        for row in result.description:
            column_names.append(row[0])
        result = result.fetchall()
        print(result)
        for res in range(len(result)):
            temp_dict = {}
            for col in range(len(column_names)):
                temp_dict.update({column_names[col]:result[res][col]})
            return_list.append(temp_dict)
            msg="fetched details successfully."
    except:
        msg="Error while fetchind details"

    finally:
        conn.close()
    return return_list


def update_otp(UserName,otp):

    """ This function will update OTP before sending mail to enduser 
        for validation purpose
    """

    try:
        conn = sql.connect('database.db')
        cur = conn.cursor()
        update_query=f"update users1 set otp={otp} where UserName='{UserName}'"
        update = cur.execute(update_query)
        conn.commit()
        msg="OTP updated in the database based on UserName."
    except:
        msg="OTP Updation problem exists"
    finally:
        conn.close()
    return msg



def del_user(UserName):

    """ This function will Delete userdetails 
        based on UserName
    """

    try:
        conn = sql.connect('database.db')
        cur = conn.cursor()
        delete_query=f"Delete from users1 where UserName='{UserName}'"
        update = cur.execute(delete_query)
        conn.commit()
        msg="Deleted UserName from database based on UserName."
    except:
        msg="UserName deletion problem exists"
    finally:
        conn.close()
    return msg

def update_Password(UserName,Password):
    """ This function can be update Password of enduser based on UserName 
    after validating OTP 
    """

    try:
        conn = sql.connect('database.db')
        cur = conn.cursor()
        update_query=f"update users1 set Password='{Password}' where UserName='{UserName}'"
        update = cur.execute(update_query)
        conn.commit()
        msg="Password updated successfully in the database based on UserName."
    except:
        msg="Password Updation problem exists"
    finally:
        conn.close()
    return msg


def send_mail(Email_id,OTP):
    """ This function will be sending the OTP mails to enduser's registered mail id  
    NOTE: The Mail id should be valid 
    """
    try :     
        s = smtplib.SMTP('smtp.gmail.com', 587) 
        s.ehlo()
        # start TLS for security 
        s.starttls() 
        # Authentication 
        s.login(mail_id,mail_Password) 
        message = str(OTP)
        # sending the mail 
        s.sendmail(mail_id, Email_id, message) 
        # terminating the session 
        s.quit() 
        msg="Mail has been sent to Registered mail id."
    except :
        msg="UserName and Password not accepted kindly provide correct UserName and Password."
    return msg

@app.route('/')
def welcome():
    return "Welcome All"

@app.route('/UserNameAvailabity',methods=["GET"])
def UserName_availabity():

        
    """Let's Check the UserName available or not
    This is used for cheching avaliablity of UserName
    ---
    parameters:  
      - name: UserName
        in: query
        type: string
        required: true
    responses:
        200:
            description: This will be showing UserName avaliabilty as Output 
        
    """
    try:
    
        UserName=request.args.get("UserName")
        user_details=fetch_details(UserName)
        user_name=user_details[0]['UserName']
        if str(UserName)==str(user_name):
            msg="UserName is already taken kindly choose another one"
    except IndexError:
        msg="UserName is available."
    return msg
    

@app.route('/Signup',methods=["POST"])
def signup():
    
    """Sign Up Page
    This is using for signup
    ---
    parameters:  
      - name: UserName
        in: query
        type: string
        required: true
      - name: Password
        in: query
        type: string
        required: true
      - name: FullName
        in: query
        type: string
        required: true
      - name: Email
        in: query
        type: string
        required: true
    responses:
        200:
            description: The output returns whether the user details successfully added or not
        
    """

    
    try:
        UserName=request.args.get("UserName")
        Password=request.args.get("Password")
        hashed_Password = hashlib.md5(Password.encode()).hexdigest() 
        FullName=request.args.get("FullName")
        Email=request.args.get("Email")
        with sql.connect("database.db") as con:
            cur = con.cursor()
            cur.execute("INSERT INTO users1 (UserName,Password,FullName,Email,otp) VALUES (?,?,?,?,NULL)",(UserName,hashed_Password,FullName,Email) )
            con.commit()
            msg = f"{UserName} details are stored successfully"
    except:
        msg = f"kindly go and check UserName_availabity end_point for current {UserName}."
    finally:
        con.close()
    
    return msg

@app.route('/Login',methods=["GET"])
def login():
    """Let's Login Now 
    This is using for Login 
    ---
    parameters:  
      - name: UserName
        in: query
        type: string
        required: true
      - name: Password
        in: query
        type: string
        required: true
    responses:
        200:
            description: The output returns the end user details
        
    """ 
    try:
        UserName=request.args.get("UserName")
        Password=request.args.get("Password")
        user_details=fetch_details(UserName)
        hashed=user_details[0]['Password']
        UserName_key=user_details[0]['UserName']

        if UserName==UserName_key and hashed==hashlib.md5(Password.encode()).hexdigest():
            user_details=fetch_details(UserName)
            dict1 = {'result':user_details}
            print(dict1)
        else:
            dict1={"Error":"Invalid  UserName or Password , kindly check ."}
    except IndexError:
        dict1={"Error":"Invalid  UserName and UserName not available in Database."}

    return Response(json.dumps(dict1),  mimetype='application/json')


@app.route('/Admin',methods=["GET"])
def extract():
    """Admin Page
    This can be used by only ADMIN
    ---
    parameters:  
      - name: UserName
        in: query
        type: string
        required: true
      - name: Password
        in: query
        type: string
        required: true
    responses:
        200:
            description: The output returns as all user details
        
    """ 
    try:

        UserName=request.args.get("UserName")
        Password=request.args.get("Password")
        user_details=fetch_details(UserName)
        hashed=user_details[0]['Password']
        UserName_key=user_details[0]['UserName']

        if UserName==admin_name:
            if UserName==UserName_key and hashed==hashlib.md5(Password.encode()).hexdigest():
                user_details=admin_access(UserName)
                dict1 = {'result':user_details}
    
            else:
                dict1={"Error":"Invalid admin UserName or admin Password , kindly check ."}
        else:
            dict1={"Error":"You are not admin for this API ."}
    except IndexError:
        dict1={"Error":"Kindly enter correct  admin UserName or admin Password ."}

        
    return Response(json.dumps(dict1),  mimetype='application/json')
    
    
@app.route('/ForgotPassword',methods=["POST"])
def forgot_Password():
    """ Forgot Password
    This is using for forgot Password.
    ---
    parameters: 
      - name: UserName
        in: query
        type: string
        required: true
      - name: API_KEY
        in: header
        description: an authorization header
        required: true
        type: string
    responses:
        200:
            description: The output returns message whether mail has been sent or not
    
    """ 
    OTP=randint(10000,100000)
    UserName=request.args.get("UserName")
    try:

        with open('api.key', 'r') as apikey:
            key=apikey.read().replace('\n', '')
        if request.headers.get('API_KEY') == key:
            user_details=fetch_details(UserName)
            Email_id=user_details[0]['Email']
            update_otp(UserName,OTP)
            msg=send_mail(Email_id,OTP)
            logging.info("sendmail function called. ")
            
        else:
            msg="Enter correct API KEY for Authentication."
    except IndexError:
        msg=f"{UserName} details not found kindly enter valid UserName."

    return msg

@app.route('/ChangePassword',methods=["POST"])
def change_Password():
    """Let's Change Password 
    This is using for Changing Password based on UserName and validation of OTP
    ---
    parameters: 
      - name: UserName
        in: query
        type: string
        required: true
      - name: OTP
        in: query
        type: number
        required: true
      - name: NewPassword
        in: query
        type: string
        required: true
      - name: API_KEY
        in: header
        description: an authorization header
        required: true
        type: string
    responses:
        200:
            description: The output returns whether the Password changed sucessfully or not
        
    """ 
    try:

        UserName=request.args.get("UserName")
        validate_otp=request.args.get("OTP")    
        NewPassword=request.args.get("NewPassword")
        hashed_Password = hashlib.md5(NewPassword.encode()).hexdigest() 
        user_details=otp_access(UserName)
        otp=user_details[0]['otp']
        with open('api.key', 'r') as apikey:
            key=apikey.read().replace('\n', '')
        if request.headers.get('API_KEY') == key:
            if str(otp)==str(validate_otp):
                    msg=update_Password(UserName,hashed_Password)
                    #This function calling makes the user use OTP until Password gets changed after that validity of OTP will be expired.
                    new_otp=randint(10000,100000)
                    # This will checks the new generated OTP and old OTP
                    if str(otp)==str(new_otp):
                        new_otp=randint(10000,100000)
                        update_otp(UserName,new_otp)
                    else:
                        update_otp(UserName,new_otp)
            else:
                msg="Something went wrong check the OTP or UserName!!!!"
        else:
            msg="Enter correct API KEY for Authentication."
    except IndexError:
        msg=f"{UserName} does not exist , kindly enter correct UserName."
    return msg

@app.route('/DeleteUserName',methods=["POST"])
def delete_UserName():
    """Let's Change Password 
    This is using for Changing Password based on UserName and validation of OTP
    ---
    parameters: 
      - name: UserName
        in: query
        type: string
        required: true
      - name: Password
        in: query
        type: string
        required: true
      - name: API_KEY
        in: header
        description: an authorization header
        required: true
        type: string
    responses:
        200:
            description: The output returns whether the Password changed sucessfully or not
        
    """ 

    try:

        UserName=request.args.get("UserName")
        Password=request.args.get("Password")
        user_details=fetch_details(UserName)
        hashed=user_details[0]['Password']
        UserName_key=user_details[0]['UserName']

        with open('api.key', 'r') as apikey:
            key=apikey.read().replace('\n', '')
        if request.headers.get('API_KEY') == key:
            if UserName==UserName_key and hashed==hashlib.md5(Password.encode()).hexdigest():
               msg=del_user(UserName)
               dict1={"Message":msg}
                
            else:
                dict1={"Message":"Invalid  UserName or Password , kindly check ."}
        else:
            dict1={"Message":"Enter API KEY for Authentication ."}
    except IndexError:
        dict1={"Message":"UserName not available ."}
    return Response(json.dumps(dict1),  mimetype='application/json')


if __name__=='__main__':
    create_database() #Intializing Database 
    app.run(debug=True) #Running our FLASK APP
    
    