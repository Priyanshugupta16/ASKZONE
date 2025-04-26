from scripts.db import cursor, conn
from scripts.sendEmail import sendMail
import bcrypt
import datetime
import random
import string

def isUserExists(email):
    query = "SELECT * FROM `user` WHERE `Email` = %s"
    cursor.execute(query, (email,))
    result = cursor.fetchall()
    user = len(result)
    if user > 0:
        return True
    else:
        return False

def registerUser(name, email, branch, specialization, semester, bestSubject, cgpa, password):
    if specialization == None:
        specialization = "NA"

    checkUser = isUserExists(email=email)
    if checkUser != True:
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

        date_str = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        random_str = ''.join(random.choices(string.ascii_letters + string.digits, k=6))
        token = f"S{semester}_{date_str}_{random_str}"
        
        query = "INSERT INTO `user` (`Id`, `Name`, `Email`, `Branch`, `Specialization`, `Semester`, `Subject`, `CGPA`, `Password`, `Activation`, `Token`, `Picture`, `Date`) VALUES (NULL, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,current_timestamp())"
        values = (name, email, branch, specialization, semester, bestSubject, cgpa, hashed_password, 'Inactive', token, 'None')

        try:
            activation_link = f"http://localhost:5000/activate/{token}"
            subject = "Activate Your ASKZONE Account"
            body = f"""
                <!DOCTYPE html>
                <html>
                <head>
                <style>
                    body {{
                    font-family: 'Poppins', sans-serif;
                    background: linear-gradient(135deg, #00c9ff, #92fe9d);
                    color: #fff;
                    text-align: center;
                    padding: 40px;
                    }}
                    .container {{
                    background-color: rgba(0, 0, 0, 0.25);
                    padding: 40px;
                    border-radius: 25px;
                    max-width: 600px;
                    margin: auto;
                    box-shadow: 0 20px 50px rgba(0, 0, 0, 0.3);
                    }}
                    h1 {{
                    color: #ffeb3b;
                    }}
                    a.button {{
                    display: inline-block;
                    padding: 15px 30px;
                    background-color: #ff4081;
                    color: white;
                    border-radius: 30px;
                    text-decoration: none;
                    font-size: 18px;
                    margin-top: 20px;
                    }}
                    a.button:hover {{
                    background-color: #f50057;
                    }}
                </style>
                </head>
                <body>
                <div class="container">
                    <h1>Welcome to ASKZONE, {name}!</h1>
                    <p>You're almost ready to start using ASKZONE. Please activate your account by clicking the button below:</p>
                    <a href="{activation_link}" class="button">Activate Account</a>
                    <p style="margin-top:20px; color:#e0f7fa;">If you did not sign up for ASKZONE, you can ignore this email.</p>
                </div>
                </body>
                </html>
                """
            message, isSend = sendMail(to=email, subject=subject, body=body)
            if isSend:
                cursor.execute(query, values)
                conn.commit()
                return "User registered successfully. Login now.", True
            else:
                return message, False
        except Exception as e:
            return "Error occured while registering. Try again.", False
    else:
        return "User already exists", False

def loginUser(email, password):
    userExists = isUserExists(email=email) 
    if userExists:
        query = "SELECT * FROM `user` WHERE `Email` = %s AND `Activation` = %s"
        try:
            cursor.execute(query, (email, 'Active'))
            result = cursor.fetchall()
            if len(result) == 0:
                return "Account not verified, check your email for email verification.", False, None
            else:
                name = result[0][1]
                hashPass = result[0][8]
                isPasswordCorrect = bcrypt.checkpw(password.encode('utf-8'), hashPass.encode('utf-8'))
                if isPasswordCorrect:
                    return "Password Matched Successfully.", True, name
                else:
                    return "Passwords do not match. Try again", False, None
        except Exception as e:
            return "Some error occured, try again after some time.", False, None

def activate(token):
    query = "SELECT * FROM `user` WHERE `Token` = %s AND `Activation` = 'Inactive'"
    value = (token,)
    try:
        cursor.execute(query, value)
        result = cursor.fetchall()
        user = len(result)
        if user > 0:
            query = "UPDATE `user` SET `Activation` = 'Active' WHERE `user`.`Token` = %s"
            value = (token,)
            try:
                cursor.execute(query,value)
                conn.commit()
                return "Account activated successfully, Login now.", True
            except Exception as e:
                return "Some error occured, try again after some time.", False
    except Exception as e:
        return "Some error occured, try again after some time.", False 
    
def fetchUser(email):
    query = "SELECT * FROM `user` WHERE `Email` = %s"
    value = (email,)
    try:
        cursor.execute(query, value)
        result = cursor.fetchone()
        print(result)
        name = result[1]
        branch = result[3]
        picture = result[11]
        return "User Found", True, [name, email, branch, picture]
    except Exception as e:
        return f"Some error occured, try again after some time. {e}", False, None

def updateProfile(name, email, branch, avatar):
    query = "UPDATE `user` SET `Name` = %s, `Branch` = %s, `Picture` = %s WHERE `user`.`Email` = %s"
    values = (name, branch, avatar, email)
    try:
        cursor.execute(query, values)
        conn.commit()
        return "Profile updated.", True
    except Exception as e:
        return "Some error occured, try again after some time.", False

def sendPasswordResetMail(email):
    userExists = isUserExists(email=email)
    if userExists:
        query = "SELECT * FROM `user` WHERE `Email` = %s"
        values = (email,)
        try:
            cursor.execute(query, values)
            result = cursor.fetchone()
            token = result[10]
            name = result[1]
            activation_link = f"http://localhost:5000/resetpass/{token}"
            subject = "Reset Your ASKZONE Account Password"
            body = f"""
                <!DOCTYPE html>
                <html>
                <head>
                <style>
                    body {{
                    font-family: 'Poppins', sans-serif;
                    background: linear-gradient(135deg, #00c9ff, #92fe9d);
                    color: #fff;
                    text-align: center;
                    padding: 40px;
                    }}
                    .container {{
                    background-color: rgba(0, 0, 0, 0.25);
                    padding: 40px;
                    border-radius: 25px;
                    max-width: 600px;
                    margin: auto;
                    box-shadow: 0 20px 50px rgba(0, 0, 0, 0.3);
                    }}
                    h1 {{
                    color: #ffeb3b;
                    }}
                    a.button {{
                    display: inline-block;
                    padding: 15px 30px;
                    background-color: #ff4081;
                    color: white;
                    border-radius: 30px;
                    text-decoration: none;
                    font-size: 18px;
                    margin-top: 20px;
                    }}
                    a.button:hover {{
                    background-color: #f50057;
                    }}
                </style>
                </head>
                <body>
                <div class="container">
                    <h1>Welcome to ASKZONE, {name}!</h1>
                    <p>Reset your account password by clicking the button below:</p>
                    <a href="{activation_link}" class="button">Reset Password</a>
                    <p style="margin-top:20px; color:#e0f7fa;">If you did not request for password reset, you can ignore this email.</p>
                </div>
                </body>
                </html>
                """
            message, isSend = sendMail(to=email, subject=subject, body=body)
            if isSend:
                return "Reset email sent successfully.", True
            else:
                return message, False
        except Exception as e:
            return "Error occured while registering. Try again.", False
    else:
        return "User does not exists. Register now.", False

def resetPassword(token, password):
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

    query = "UPDATE `user` SET `Password` = %s WHERE `user`.`Token` = %s"
    values = (hashed_password, token)

    try:
        cursor.execute(query, values)
        conn.commit()
        return "Password changed successfully.", True
    except Exception as e:
        return "Failed to change the password.", False

