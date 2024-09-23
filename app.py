from flask import Flask,render_template,request
import pymysql
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import random
import razorpay
import os
app = Flask(__name__)
RAZORPAY_KEY_ID='rzp_test_l6aaUvlqLyWYJX'
RAZORPAY_KEY_SECRET='pMbtKYdbYA4oIueh9jfslglM'
client=razorpay.Client(auth=(RAZORPAY_KEY_ID,RAZORPAY_KEY_SECRET))
user=os.environ.get('RDS_USERNAME')
db=os.environ.get('RDS_DB_NAME')
password=os.environ.get('RDS_PASSWORD')
host=os.environ.get('RDS_HOSTNAME')
port=os.environ.get('RDS_PORT')
with pymysql.connect(host=host,password=password,db=db,user=user,port=port) as conn:
    cursor=conn.cursor()
    cursor.execute("CREATE TABLE if not exists users ( FNAME varchar(30) DEFAULT NULL, LNAME varchar(30) DEFAULT NULL, EMAIL varchar(40) NOT NULL, USERNAME varchar(40) DEFAULT NULL, PASSWORD varchar(40) DEFAULT NULL, PRIMARY KEY (EMAIL)) ")
    cursor.execute("CREATE TABLE if not exists cart ( PNAME varchar(20) DEFAULT NULL, PPRICE varchar(10) DEFAULT NULL, EMAIL varchar(40) DEFAULT NULL) ")
#db_config=pymysql.connect(host=host,user=user,password=password,db=db,port=port)
verifyotp = "0"
db_config = {
    'host': host,
    'user': user,
    'password': password,
    'db': db,
    'port': int(port)
}

'''
db_config = {
    'host': 'localhost',
    'database': 'ecom',
    'user': 'root',
    'password': 'root'
}
'''

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/verify")
def verify():
    return render_template("verifyemail.html")

@app.route("/login")
def login():
    return render_template("login.html")

@app.route("/verify1",methods=["POST","GET"])
def verify1():
    otp = random.randint(1111,9999)
    global verifyotp
    verifyotp = str(otp)
    print(verifyotp)
    x = False
    if request.method == "POST":
        email = request.form['email']
        x = True
    if x:
        print("Sending Email")
        smtp_server = 'smtp.gmail.com'
        smtp_port = 587
        mailusername = "saivardhan.thimmisetty@gmail.com"
        mailpassword = "xqmd vmwz ibqy ijii"
        from_email = "saivardhan.thimmisetty@gmail.com"
        to_email = email
        subject = 'OTP for Login'
        body = f"The OTP for verification is {otp}"

        msg = MIMEMultipart()
        msg['From'] = from_email
        msg['To'] = to_email
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))

        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(mailusername, mailpassword)
        server.send_message(msg)
        server.quit()
        print("email Sent")
        return render_template("enterotp.html",email = email)
    else:
        return "Try Again"
    
@app.route("/enterotp")
def enterotp():
    return render_template("enterotp.html")

@app.route("/verifyotp1",methods=["POST","GET"])
def verifyotp1():
    print("Verification started")
    print(verifyotp)
    print(type(verifyotp))
    x = False
    if request.method == "POST":
        otp = request.form['otp']
        email = request.form['mail']
        print(email)
        x = True
    else:
        return "Error Occured"
    if x:
        if otp == verifyotp:
            return render_template("register.html",email=email)
        else:
            return "try again"
@app.route("/register")
def register():
    return render_template("register.html")

@app.route("/register1",methods=["POST","GET"])
def register1():
    if request.method == "POST":
        fname = request.form['fname']
        lname = request.form['lname']
        mail = request.form['mail']
        username = request.form['username']
        password = request.form['password']
        try:
            conn = pymysql.connect(**db_config)
            cursor = conn.cursor()
            q1 = "INSERT INTO users VALUES (%s,%s,%s,%s,%s)"
            cursor.execute(q1,(fname,lname,mail,username,password))
            conn.commit()
        except Exception as e:
            return "Account Exists"
        else:
            return render_template("home.html")
    else:
        return "Error Occured"


@app.route("/login1",methods=["POST","GET"])
def login1():
    if request.method == "POST":
        username = request.form['username']
        password = request.form['password']
        try:
            conn = pymysql.connect(**db_config)
            cursor = conn.cursor()
            q1 = "SELECT * FROM users"
            cursor.execute(q1,)
            x = cursor.fetchall()
            conn.commit()
            unames = []
            passwords = []
            mails = []
            for i in x:
                unames.append(i[3])
                passwords.append(i[4])
                mails.append(i[2])
            if username in unames:
                ind = unames.index(username)
                if password == passwords[ind]:
                    return render_template("userhome.html",mail = mails[ind])
                else:
                    return "Invalid Password"
            else:
                return "Invalid Username"
        except Exception as e:
            return "Other error Occured"
    else:
        return "Error Occured"
    
@app.route('/storedata',methods=["POST","GET"])
def storedata():
    if request.method == "POST":
        details = request.form['gather']
        x = details.split(",")
        print(x)
        try:
            conn = pymysql.connect(**db_config)
            cursor = conn.cursor()
            q1 = "INSERT INTO cart VALUES (%s,%s,%s)"
            cursor.execute(q1,(x[0],x[1],x[2]))
            conn.commit()
        except Exception as e:
            return e
        else:
            return render_template("userhome.html",mail=x[2])
    else:
        return "Error Occured"
    
@app.route("/showcart",methods=["POST","GET"])
def showcart():
    if request.method == "POST":
        usermail = request.form['getcart']
        print(usermail)
        try:
            print("Connecting sql")
            conn = pymysql.connect(**db_config)
            cursor = conn.cursor()
            q1 = "select * from cart"
            cursor.execute(q1,)
            x = cursor.fetchall()
            conn.commit()
            data = []
            for i in x:
                if i[2] == usermail:
                    data.append(i)
            total = 0
            for i in data:
                total = total + int(i[1])
            amount=total*100
            print("Amount")
            print("Trying to create order")
            order=client.order.create({
                'amount':amount,
                'currency':'INR',
                'payment_capture':'1'
            })
            print("Order Created")
        except Exception as e:
            print(f'Error creating order: {str(e)}')
            return str(e),400
        else:
            return render_template("showproducts.html",rows=data,total=str(total),name="Products",price=amount,order=order)
    else:
        return "Error Occured"

@app.route('/success',methods=['POST'])
def success():
    #extract payment details from the form
    payment_id=request.form.get('razorpay_payment_id')
    order_id=request.form.get('razorpay_order_id')
    signature=request.form.get('razorpay_signature')
    name=request.form.get('name')
    total_price=request.form.get('total_price')
    #verification process
    params_dict = {
        'razorpay_order_id':order_id,
        'razorpay_payment_id':payment_id,
        'razorpay_signature':signature
    }
    try:
        client.utility.verify_payment_signature(params_dict)
        return "Payment Sucess"
    except razorpay.errors.SignatureVerificationError:
        return 'Payment verification failed!',400
if __name__ == "__main__":
    app.run()


    