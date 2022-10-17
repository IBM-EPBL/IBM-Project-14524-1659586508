from flask import Flask,render_template,request,redirect,url_for

import ibm_db

try:
    conn = ibm_db.connect("DATABASE=bludb;HOSTNAME=125f9f61-9715-46f9-9399-c8177b21803b.c1ogj3sd0tgtu0lqde00.databases.appdomain.cloud;PORT=30426;SECURITY=SSL;SSLServerCertificate=DigiCertGlobalRootCA.crt;PROTOCOL=TCPIP;UID=str00116;PWD=fpvVNC88XonuES12;", "", "")
    print("Connected to database")
except:
    print("Failed to connect: ", ibm_db.conn_errormsg())

app = Flask(__name__)

loggedIn = False
# username='pramodhv'
# password='pv103554'

# sql = "SELECT * from User where Username='{}' and password='{}'".format(username,password)
# stmt = ibm_db.exec_immediate(conn,sql)
# dict = ibm_db.fetch_assoc(stmt)
# if(dict==False):
#     print("Error")
# print(dict)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login',methods=["GET","POST"])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        try:
            sql = "SELECT * from user where username='{0}' and password='{1}'".format(username,password)
            print(sql)
            stmt = ibm_db.exec_immediate(conn, sql)
            res = ibm_db.fetch_assoc(stmt)
            print(res['USERNAME'])

            if len(res) == 0 :
                return render_template('login.html',message="Incorrect Username/Password")
            else:
                loggedIn = True
                return render_template('dashboard.html',user=res['USERNAME'])

        except:
            print("Error: ",ibm_db.stmt_errormsg())

    return render_template('login.html',message="")

@app.route('/register',methods=["GET","POST"])
def register():
    if request.method == 'POST':
        name = request.form['username']
        email = request.form['email']
        rollno = request.form['rollno']
        password = request.form['password']
        cp = request.form['confirmpassword']

        if password!=cp:
            return render_template('register.html')

        try:
            sql = "INSERT into User values ('{}', '{}','{}', '{}')".format( name, email,rollno, password)
            stmt = ibm_db.exec_immediate(conn,sql)
            print("No of Affected rows: ",ibm_db.num_rows(stmt))
        except:
            print("Error: ",ibm_db.stmt_errormsg())
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/dashboard')
def dashboard():
    if loggedIn==False:
        return redirect(url_for('login'))
    return render_template('dashboard.html')

if __name__ == '__main__':
    app.run(debug=True)