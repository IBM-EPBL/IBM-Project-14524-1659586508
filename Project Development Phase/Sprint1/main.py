import hashlib
import ibm_db
from flask import Flask, redirect, render_template, request, url_for, session, jsonify
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
import os
#from dotenv import load_dotenv
from pathlib import Path

dotenv_path = Path('secrets.env')
#load_dotenv(dotenv_path=dotenv_path)
"""
try: 
    conn = conn=ibm_db.connect("DATABASE=bludb;\
                            HOSTNAME=6667d8e9-9d4d-4ccb-ba32-21da3bb5aafc.c1ogj3sd0tgtu0lqde00.databases.appdomain.cloud;\
                            PORT=30376;\
                            PROTOCOL=TCPIP;\
                            SECURITY=SSL;\
                            SSLServerCertificate=DigiCertGlobalRootCA.crt;\
                            UID=vnl94634;\
                            PWD=lVyCE6QOmmkmnsbw;", "", "")
        
    print("Connected to IBM DB2, Server Details:")
    server = ibm_db.server_info(conn)

    print ("DBMS_NAME: ", server.DBMS_NAME)
    print ("DBMS_VER:  ", server.DBMS_VER)
    print ("DB_NAME:   ", server.DB_NAME)
except Exception as err:
    print("Error: Cannot connect with IBM DB2", err)"""

app = Flask(__name__)
app.secret_key = os.urandom(16)

@app.route('/')
def home():
    if not session or not session['USERID']:
        return render_template("mainpage.html")
    else:
        sql = "select * from user where userid=?"
        stmt = ibm_db.prepare(conn, sql)
        ibm_db.bind_param(stmt, 1, session['USERID'])
        ibm_db.execute(stmt)
        res = ibm_db.fetch_assoc(stmt)
        if res:
            session['ROLE'] = res['ROLE']
            session['USERID'] = res['USERID']
            return render_template('dashboard.html', username=res['USERNAME'], role=res['ROLE'])
        else:
            return render_template('mainpage.html')


@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method=='POST':
        username = request.form['username']
        password = request.form['password']
        password = bytes(password,'utf-8')
        password = hashlib.sha256(password).hexdigest()
        
        sql = "select * from user where username=? and password=?"
        stmt = ibm_db.prepare(conn, sql)
        ibm_db.bind_param(stmt, 1, username)
        ibm_db.bind_param(stmt, 2, password)
        ibm_db.execute(stmt)
        res = ibm_db.fetch_assoc(stmt)
        if res:
            session['ROLE'] = res['ROLE']
            session['USERID'] = res['USERID']
            return render_template('dashboard.html', username=username, role=res['ROLE'])
        else:
            msg = "Credentials not found! Please Check the Credentials you have entered."
            return render_template('error.html',err_msg=msg)
    else:
       return render_template('login.html')


@app.route('/signup', methods=['POST', 'GET'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        cnf_password = request.form['confpassword']
        phone_no = request.form['phone_no']
        sex = request.form['sex']
        age = request.form['age']
        address = request.form['address']
        blood_group = request.form['blood_group']
        if password != cnf_password:
            msg = "Password and Confirm Password didn't Match. Please check the passwords and try again!"
            return render_template('error.html',err_msg=msg)
         
        password = bytes(password,'utf-8')
        password = hashlib.sha256(password).hexdigest()
        # password hashed

        ## case 1: check if user does exists already
        sql = "SELECT * FROM user WHERE email =?"
        stmt = ibm_db.prepare(conn, sql)
        ibm_db.bind_param(stmt,1,email)
        ibm_db.execute(stmt)
        acc = ibm_db.fetch_assoc(stmt)
        if acc:
            msg = "Account already Exists, Please login or register with a different email."
            return render_template('error.html',err_msg=msg)
        sql = "insert into user(username, email, password, phone, sex, age, role, address, bloodgroup) values(?,?,?,?,?,?,?,?,?)"
        prep_stmt = ibm_db.prepare(conn, sql)
        ibm_db.bind_param(prep_stmt, 1, username)
        ibm_db.bind_param(prep_stmt, 2, email)
        ibm_db.bind_param(prep_stmt, 3, password)
        ibm_db.bind_param(prep_stmt, 4, phone_no)
        ibm_db.bind_param(prep_stmt, 5, sex)
        ibm_db.bind_param(prep_stmt, 6, age)
        ibm_db.bind_param(prep_stmt, 7, "USER")
        ibm_db.bind_param(prep_stmt, 8, address)
        ibm_db.bind_param(prep_stmt, 9, blood_group)
        ibm_db.execute(prep_stmt)

        message = Mail(
        from_email=Email("aseera1105@gmail.com"),
        to_emails=email,
        subject='Confirmation Email From Plasma Donor Application.',
        html_content='''

        <h1>You are a Lifesaver, ''' +username+ '''!</h1><br>
        <h3> Thank you so much for registering with us </h3><br>
        <p> You are now registered user. Now, you can visit our website and login to your profile using the credentials you have registered with.</p>
        <p> You have made a very important step towards making earth a better place! Thank you.</p>
        '''
        )

        try:
            #sg = SendGridAPIClient(os.getenv("SENDGRIDAPIKEY"))
            SENDGRID_API_KEY = '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'  
            sg = sendgrid.SendGridAPIClient(api_key=SENDGRID_API_KEY)
            sg.send(message=message)
        except Exception as e:
            print(e)
        # db post operation
        return redirect(url_for('login'))
    elif request.method == 'GET':
        return render_template('signup.html')

@app.route('/logout', methods=['POST', 'GET'])
def logout():
    session.pop('USERID',None)
    session.pop('ROLE',None)
    return redirect(url_for('home'))

@app.route('/toggle', methods=['POST'])
def toggle_user():
    data = request.get_json(force=True)

    username = data['username']
    role = data['role']
    sql = "update user set role=? where username=?"
    prep_stmt = ibm_db.prepare(conn, sql)
    ibm_db.bind_param(prep_stmt, 1, role)
    ibm_db.bind_param(prep_stmt, 2, username)
    ibm_db.execute(prep_stmt)
    return jsonify(
        status="success",
        role=role
    )


@app.route('/requestPlasma', methods=['POST'])
def requestBloodPlasma():
    #fetch mail address of the donors
    data =  request.get_json(force=True) 
    name = data['name']
    age = data['age']      
    sex = data['sex']
    phone_number = data['phno']
    blood_type = data['blood']
    reqUserId = session['USERID']
    sql = "select email from user where bloodgroup=?"
    stmt = ibm_db.prepare(conn, sql)
    ibm_db.bind_param(stmt, 1, blood_type)
    ibm_db.execute(stmt)
    dic = ibm_db.fetch_assoc(stmt)
    
    #send mail
    email_list = []
    while dic != False:
        email_list.append(dic['EMAIL'])
        print(dic['EMAIL'])
        dic = ibm_db.fetch_assoc(stmt)
    # send mail
    print(email_list)
    message = Mail(
        from_email='2019ec0181@svce.ac.in',
        to_emails=email_list,
        subject='Plasma Needed! Your Help is Needed to Save Lives!',
        html_content='''
        <div style="font-family: sans-serif;text-align: left;">
            <style>
                td {
                    padding: 10px;
                }
                th {
                    padding: 10px;
                }
            </style>
            <table border="0" cellpadding="0" cellspacing="0" height="100%" width="100%" id="bodyTable">
                <tr>
                    <td align="center" valign="top">
                        <table border="0" cellpadding="20" cellspacing="0" width="600" id="emailContainer">
                            <tr>
                                <td align="center" valign="top">
                                    <table border="0" cellpadding="20" cellspacing="0" width="100%" id="emailHeader">
                                        <tr>
                                            <td align="center" valign="top">
                                                <h2 style="margin: 0;">Plasma Needed!<br></h2>
                                                <h3 style="margin: 0;">New Request has been Raised</h3>
                                            </td>
                                        </tr>
                                    </table>
                                </td>
                            </tr>
                            <tr>
                                <td align="center" valign="top">
                                    <table border="0" cellpadding="20" cellspacing="0" width="100%" id="emailBody">
                                        <tr>
                                            <td align="center" valign="top">
                                                <table style="border: black solid 1px;">
                                                    <tr>
                                                        <th>Name</th>
                                                        <th>:</th>
                                                        <th>''' + name + '''</th>
                                                    </tr>
                                                    <tr>
                                                        <th>Age</th>
                                                        <th>:</th>
                                                        <th>''' + age + '''</th>
                                                    </tr>
                                                    <tr>
                                                        <th>Sex</th>
                                                        <th>:</th>
                                                        <th>''' + sex + '''</th>
                                                    </tr>
                                                    <tr>
                                                        <th>Blood Group</th>
                                                        <th>:</th>
                                                        <th>''' + blood_type + '''</th>
                                                    </tr>
                                                    <tr>
                                                        <th>Phone Number</th>
                                                        <th>:</th>
                                                        <th>''' + phone_number + '''</th>
                                                    </tr>
                                                </table>
                                            </td>
                                        </tr>
                                    </table>
                                </td>
                            </tr>
                            <tr>
                                <td align="center" valign="top">
                                    <table border="0" cellpadding="20" cellspacing="0" width="100%" id="emailFooter">
                                        <tr>
                                            <td align="center" valign="top">
                                                <h5>You have a chance to save a life. Act quick! Every second a life is in
                                                    danger.</h5>
                                            </td>
                                        </tr>
                                    </table>
                                </td>
                            </tr>
                        </table>
                    </td>
                </tr>
            </table>
        </div>'''
    )
    try:
        sg = SendGridAPIClient(os.getenv("SENDGRIDAPIKEY"))
        response = sg.send(message=message)
        print(response.status_code)
        print(response.body)
        print(response.headers)
    except Exception as e:
        print(e)
    
    #insert data into requests table
    sql = "insert into requests(userid,recname,recage,recsex,recbloodgroup,recphone) values (?,?,?,?,?,?)"
    prep_stmt = ibm_db.prepare(conn, sql)
    ibm_db.bind_param(prep_stmt, 1, reqUserId)
    ibm_db.bind_param(prep_stmt, 2, name)
    ibm_db.bind_param(prep_stmt, 3, age)
    ibm_db.bind_param(prep_stmt, 4, sex)
    ibm_db.bind_param(prep_stmt, 5, blood_type)
    ibm_db.bind_param(prep_stmt, 6, phone_number)
    ibm_db.execute(prep_stmt)

    return jsonify(
        name=name,
        age=age,
        sex=sex,
        bloodtype=blood_type,
        phone=phone_number,
        status="yes"
    )


@app.route('/getrequests', methods=['POST'])
def getBloodRequests():
    data =  request.get_json(force=True) 
    
    sql = "select * from requests where userid=?"
    stmt = ibm_db.prepare(conn, sql)
    ibm_db.bind_param(stmt, 1, session["USERID"])
    ibm_db.execute(stmt)
    dic = ibm_db.fetch_assoc(stmt)
    requests = []
    while dic != False:
        single_request = {
            'name': dic['RECNAME'],
            'age': dic['RECAGE'],
            'sex': dic['RECSEX'],
            'blood_type': dic['RECBLOODGROUP']
        }
        requests.append(single_request)
        dic = ibm_db.fetch_assoc(stmt)
    return jsonify(
        username=data['username'],
        requests=requests
    )

@app.route('/form')
def form():
    return render_template("form.html")

if __name__=='__main__':
    app.run(host="0.0.0.0",debug = True)

