def mailConfig():
    SENDGRID_API_KEY= "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"
    MAIL_DEFAULT_SENDER= "sparklingvishnu@gmail.com"

    app.config['SECRET_KEY'] = 'top-secret!'
    app.config['MAIL_SERVER'] = 'smtp.sendgrid.net'
    app.config['MAIL_PORT'] = 587
    app.config['MAIL_USE_TLS'] = True
    app.config['MAIL_USERNAME'] = 'apikey'
    app.config['MAIL_PASSWORD'] = SENDGRID_API_KEY
    app.config['MAIL_DEFAULT_SENDER'] = MAIL_DEFAULT_SENDER

    mail = Mail(app)

    sql = 'SELECT EMAIL FROM REGISTER WHERE USER_ID={}'.format(session['id'])
    df = pd.read_sql(sql,pd_conn)
    row = df.values.tolist()
    msg = Message('Personal Expense Tracker', recipients=[row[0][0]])
    msg.body = report_type + ' Report'
    
    
    sql = 'SELECT * FROM EXPENSES WHERE USER_ID={} AND MONTH(DATE(DATE)) = MONTH(CURRENT_DATE) ORDER BY DATE DESC, AMOUNT'.format(session['id'])
    df = pd.read_sql(sql,pd_conn)
    df.drop(columns=['EXPENSE_ID','USER_ID'],inplace=True)

    rep = generateReport(report_type)
    del rep['texpense']
    df1 = pd.DataFrame(rep)
    df1.rename(columns={"t_food": "Food", "t_entertainment": "Entertainment","t_business": "Business","t_rent": "Rent","t_EMI": "EMI","t_other":"Other","total":"TOTAL"}, inplace=True)


    html = """\
    <html>
      <head></head>
      <body>
        <p>Hi!<br>
           <b>Monthly Expenses:<b><br>
           {0}
           <br><b>Total Categorized Expenses:<b><br>
           {1}

           Regards,
        </p>
      </body>
    </html>

    """.format(df.to_html(), df1.to_html())

    msg.html = html
    mail.send(msg)

    print("mail sent successfully")
    flash("Mail sent successfully!")

    rep = generateReport(report_type)
    return render_template("report.html", type=report_type, texpense = rep['texpense'],  total = rep['total'][0] ,
                           t_food = rep['t_food'][0],t_entertainment =  rep['t_entertainment'][0],
                           t_business = rep['t_business'][0],  t_rent =  rep['t_rent'][0], 
                           t_EMI = rep['t_EMI'][0],  t_other =  rep['t_other'][0] )