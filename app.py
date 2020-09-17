from flask import Flask, render_template, request, redirect, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from celery import Celery

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI']        = 'mysql+pymysql://root:xflow@123@localhost/xflow_monitoring_system'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class Interface(db.Model):
    id         = db.Column(db.Integer, primary_key=True)
    port       = db.Column(db.String(100), nullable=False)
    date       = db.Column(db.DateTime, nullable=False)
    status     = db.Column(db.String(100), nullable=False)
    device     = db.Column(db.String(100), nullable=False)

    def __init__(self, port, date, status, device):
        self.port       = port
        self.date = date
        self.status     = status
        self.device     = device

class Login(db.Model):
    id         = db.Column(db.Integer, primary_key=True)
    user       = db.Column(db.String(100), nullable=False)
    ip_address = db.Column(db.String(100), nullable=False)
    date       = db.Column(db.DateTime, nullable=False)
    line       = db.Column(db.String(100), nullable=False)
    device     = db.Column(db.String(100), nullable=False)

    def __init__(self, user, ip_address, date, line, device):
        self.user       = user
        self.ip_address = ip_address
        self.date       = date
        self.line       = line
        self.device     = device

class Temperature(db.Model):
    id           = db.Column(db.Integer, primary_key=True)
    temperature  = db.Column(db.Integer, nullable=False)
    time         = db.Column(db.DateTime, nullable=False)
    device       = db.Column(db.String(100), nullable=False)

    def __init__(self, temperature, time, device):
        self.temperature = temperature
        self.time        = time
        self.device      = device

# ************* CORE SWITCH 2 Starts *************

#Fetching Interfaces stats
import re

datetimelist = []
intlist = []
interfaceslist = []
statlist = []
statuslist = []
datetime_list = []

textfile = open('/root/dashboard/filtering/log_switch.txt', 'rt')
filetext = textfile.read()
textfile.close()

login = re.findall("\w{3} \d{1,2} [0-2][0-9]:[0-5][0-9]:[0-5][0-9].\d{1,3}: %[a-zA-Z0-9- ]*: Interface [a-zA-Z0-9\/ ]*, changed state to \w{2,4}", filetext)
mylist = list(dict.fromkeys(login))
# print(mylist)

dateTime = re.compile('\w{3} \d{1,2} [0-2][0-9]:[0-5][0-9]:[0-5][0-9]')

for i in range(len(mylist)):
    m = dateTime.findall(mylist[i])
    datetimelist.append(m)

datetimelist = [item for sublist in datetimelist for item in sublist]

intp = re.compile('Interface [a-zA-Z0-9\/]*')

for i in range(len(mylist)):
    m = intp.findall(mylist[i])
    intlist.append(m)

intlist = [item for sublist in intlist for item in sublist]

interfaces = re.compile(' [a-zA-Z0-9\/]*')

for i in range(len(intlist)):
    m = interfaces.findall(intlist[i])
    interfaceslist.append(m)

interfaceslist = [item for sublist in interfaceslist for item in sublist]
interfaceslist = [x.strip(' ') for x in interfaceslist]

stat = re.compile('to \w{2,4}')

for i in range(len(mylist)):
    m = stat.findall(mylist[i])
    statlist.append(m)

statlist = [item for sublist in statlist for item in sublist]

status = re.compile(' \w{2,4}')

for i in range(len(statlist)):
    m = status.findall(statlist[i])
    statuslist.append(m)

statuslist = [item for sublist in statuslist for item in sublist]
statuslist = [x.strip(' ') for x in statuslist]

# print(type(datetimelist))
# print(interfaceslist)
# print(statuslist)

for dt in datetimelist:
    datetime_list.append(datetime.strptime(dt, '%b %d %H:%M:%S'))

# print(datetime_list)

# Adding/Updating Interfaces in DB
port_status_datetime = zip(interfaceslist, statuslist, datetime_list)
interfaces_from_db = Interface.query.filter_by(device='Core-Switch-2').all()

for (port, status, dateTime) in port_status_datetime:
    if not interfaces_from_db:
        new_interface = Interface(port=port, status=status, date=dateTime, device='Core-Switch-2')
        try:
            db.session.add(new_interface)
            db.session.commit()

        except:
            print('There was a problem adding that Interface attempt')
    else:
        for interface_from_db in interfaces_from_db:
            if(interface_from_db.date != dateTime):
                new_interface = Interface(port=port, status=status, date=dateTime, device='Core-Switch-2')
                try:
                    db.session.add(new_interface)
                    db.session.commit()

                except:
                    print('There was a problem adding that interface attempt')

# Fetching Login stats

ipaddlist = []
timelist = []
datelist = []
userlist = []
usernamelist = []
datetime_list = []
datetimelist = []

textfile = open('/root/dashboard/filtering/log.txt', 'rt')
filetext = textfile.read()
textfile.close()


login = re.findall("Login failed \[user: \] \[Source: \d{2,3}.\d{2,3}.\d{2,3}.\d{2,3}\] \[localport: \d{2,3}\] \[Reason: [a-zA-Z0-9- ]*\] at [0-2][0-9]:[0-5][0-9]:[0-5][0-9] UTC \w{3} \w{3} \d{2} \d{4}", filetext)
mylist = list(dict.fromkeys(login))

ipadd = re.compile('\d{2,3}.\d{2,3}.\d{2,3}.\d{2,3}')

for i in range(len(mylist)):
    m = ipadd.findall(mylist[i])
    ipaddlist.append(m)

ipaddlist = [item for sublist in ipaddlist for item in sublist]

user = re.compile('user: [a-zA-Z]*')

for i in range(len(mylist)):
    m = user.findall(mylist[i])
    userlist.append(m)

userlist = [item for sublist in userlist for item in sublist]

username = re.compile(' [a-zA-Z]*')

for i in range(len(userlist)):
    m = username.findall(userlist[i])
    usernamelist.append(m)

usernamelist = [item for sublist in usernamelist for item in sublist]
usernamelist = [x.strip(' ') for x in usernamelist]

time = re.compile(' [0-2][0-9]:[0-5][0-9]:[0-5][0-9]')

for i in range(len(mylist)):
    m = time.findall(mylist[i])
    timelist.append(m)

timelist = [item for sublist in timelist for item in sublist]

date = re.compile('\w{3} \w{3} \d{2} \d{4}')

for i in range(len(mylist)):
    m = date.findall(mylist[i])
    datelist.append(m)

datelist = [item for sublist in datelist for item in sublist]
datetimelist = [i + j for i, j in zip(datelist, timelist)]
for dt in datetimelist:
    datetime_list.append(datetime.strptime(dt, '%a %b %d %Y %H:%M:%S'))

# Adding login stats in DB

user_ip_add_datetime = zip(usernamelist, ipaddlist, datetime_list)
logins_from_db = Login.query.filter_by(device='Core-Switch-2').all()

for (user, ip_add, date_time) in user_ip_add_datetime:
    if not logins_from_db:
        new_login = Login(user = user, date = date_time, ip_address = ip_add, line = 'Vty 0', device='Core-Switch-2')
        try:
            db.session.add(new_login)
            db.session.commit()

        except:
            print('There was a problem adding that login attempt')
    else:
        for login_from_db in logins_from_db:
            if(login_from_db.user != user and login_from_db.ip_address != ip_add and login_from_db.date != date_time):
                new_login = Login(user = user, date = date_time, ip_address = ip_add, line = 'Vty 0', device='Core-Switch-2')
                try:
                    db.session.add(new_login)
                    db.session.commit()

                except:
                    print('There was a problem adding that login attempt')

# Fetching Temperatures
import os
import time

i = 0
j = 0
temps         = []
chassis_temps = []
timelist      = []

with open('/root/Temp_logs.txt','r') as f:
    for line in f:
        for word in line.split():
            chassis_temps.append(word)

while j < len(chassis_temps):
    if("Chassis" in chassis_temps[j]):
      if(chassis_temps[j+1] == "Temperature"):
        j+=3
        temps.append(chassis_temps[j])
        timelist.append(datetime.now())
        break
    j+=1

# print(temps)
for temp in temps:
    temp = int(temp)

# Adding temperature stats to db
temp_time = zip(temps, timelist)
temps_from_db = Temperature.query.filter_by(device='Core-Switch-2').all()
for (temp, time) in temp_time:
    if not temps_from_db:
        new_temp = Temperature(temperature=temp, time=time, device='Core-Switch-2')
        try:
            db.session.add(new_temp)
            db.session.commit()

        except:
            print('There was a problem adding that temperature stats')
    else:
        for temp_from_db in temps_from_db:
            if(temp_from_db.time != time):
                new_temp = Temperature(temperature=temp, time=time, device='Core-Switch-2')
                try:
                    db.session.add(new_temp)
                    db.session.commit()

                except:
                    print('There was a problem adding that temperature stats')
            
# ************* CORE SWITCH 2 Ends *************

# ************* CORE ROUTER Starts *************

# Fetching Interfaces Stats

datetimelist = []
intlist = []
interfaceslist = []
statlist = []
statuslist = []
datetime_list = []

textfile = open('/root/dashboard/filtering/log_router.txt', 'rt')
filetext = textfile.read()
textfile.close()

login = re.findall("\w{3} \d{1,2} [0-2][0-9]:[0-5][0-9]:[0-5][0-9].\d{1,3}: %[a-zA-Z0-9- ]*: Interface [a-zA-Z0-9\/ ]*, changed state to \w{2,4}", filetext)
mylist = list(dict.fromkeys(login))
# print(mylist)

dateTime = re.compile('\w{3} \d{1,2} [0-2][0-9]:[0-5][0-9]:[0-5][0-9]')

for i in range(len(mylist)):
    m = dateTime.findall(mylist[i])
    datetimelist.append(m)

datetimelist = [item for sublist in datetimelist for item in sublist]

intp = re.compile('Interface [a-zA-Z0-9\/]*')

for i in range(len(mylist)):
    m = intp.findall(mylist[i])
    intlist.append(m)

intlist = [item for sublist in intlist for item in sublist]

interfaces = re.compile(' [a-zA-Z0-9\/]*')

for i in range(len(intlist)):
    m = interfaces.findall(intlist[i])
    interfaceslist.append(m)

interfaceslist = [item for sublist in interfaceslist for item in sublist]
interfaceslist = [x.strip(' ') for x in interfaceslist]

stat = re.compile('to \w{2,4}')

for i in range(len(mylist)):
    m = stat.findall(mylist[i])
    statlist.append(m)

statlist = [item for sublist in statlist for item in sublist]

status = re.compile(' \w{2,4}')

for i in range(len(statlist)):
    m = status.findall(statlist[i])
    statuslist.append(m)

statuslist = [item for sublist in statuslist for item in sublist]
statuslist = [x.strip(' ') for x in statuslist]

# print(type(datetimelist))
# print(interfaceslist)
# print(statuslist)

for dt in datetimelist:
    # print(type(dt))
    datetime_list.append(datetime.strptime(dt, '%b %d %H:%M:%S'))

for dt in datetime_list:
    dt.replace(year=2020)
# print(datetime_list)

# Adding/Updating Interfaces in DB
port_status_datetime = zip(interfaceslist, statuslist, datetime_list)
interfaces_from_db = Interface.query.filter_by(device='Core-Router').all()

for (port, status, dateTime) in port_status_datetime:
    if not interfaces_from_db:
        new_interface = Interface(port=port, status=status, date=dateTime, device='Core-Router')
        try:
            db.session.add(new_interface)
            db.session.commit()

        except:
            print('There was a problem adding that Interface attempt')
    else:
        for interface_from_db in interfaces_from_db:
            if(interface_from_db.port != port and interface_from_db.date != dateTime):
                new_interface = Interface(port=port, status=status, date=dateTime, device='Core-Router')
                try:
                    db.session.add(new_interface)
                    db.session.commit()

                except:
                    print('There was a problem adding that interface attempt')

# Fetching Login stats

ipaddlist = []
timelist = []
datelist = []
userlist = []
usernamelist = []
datetime_list = []

textfile = open('/root/dashboard/filtering/log_router.txt', 'rt')
filetext = textfile.read()
textfile.close()

login = re.findall("Still timeleft for watching failures is \d{2} secs, \[user: [a-zA-Z]*\] \[Source: \d{2,3}.\d{2,3}.\d{2,3}.\d{2,3}\] \[localport: \d{2,3}\] \[Reason: [a-zA-Z0-9- ]*\] \[ACL: sl_def_acl\] at [0-2][0-9]:[0-5][0-9]:[0-5][0-9] UTC \w{3} \w{3} \d{2} \d{4}", filetext)
mylist = list(dict.fromkeys(login))

ipadd = re.compile('\d{2,3}.\d{2,3}.\d{2,3}.\d{2,3}')

for i in range(len(mylist)):
    m = ipadd.findall(mylist[i])
    ipaddlist.append(m)

ipaddlist = [item for sublist in ipaddlist for item in sublist]

user = re.compile('user: [a-zA-Z]*')

for i in range(len(mylist)):
    m = user.findall(mylist[i])
    userlist.append(m)

userlist = [item for sublist in userlist for item in sublist]

username = re.compile(' [a-zA-Z]*')

for i in range(len(userlist)):
    m = username.findall(userlist[i])
    usernamelist.append(m)

usernamelist = [item for sublist in usernamelist for item in sublist]
usernamelist = [x.strip(' ') for x in usernamelist]

time = re.compile(' [0-2][0-9]:[0-5][0-9]:[0-5][0-9]')

for i in range(len(mylist)):
    m = time.findall(mylist[i])
    timelist.append(m)


timelist = [item for sublist in timelist for item in sublist]

date = re.compile('\w{3} \w{3} \d{2} \d{4}')

for i in range(len(mylist)):
    m = date.findall(mylist[i])
    datelist.append(m)

datelist = [item for sublist in datelist for item in sublist]

datetimelist = [i + j for i, j in zip(datelist, timelist)]

for dt in datetimelist:
    datetime_list.append(datetime.strptime(dt, '%a %b %d %Y %H:%M:%S'))

# Adding login stats in DB

user_ip_add_datetime = zip(usernamelist, ipaddlist, datetime_list)
logins_from_db = Login.query.filter_by(device='Core-Router').all()

for (user, ip_add, date_time) in user_ip_add_datetime:
    if not logins_from_db:
        new_login = Login(user = user, date = date_time, ip_address = ip_add, line = 'Vty 0', device='Core-Router')
        try:
            db.session.add(new_login)
            db.session.commit()

        except:
            print('There was a problem adding that login attempt')
    else:
        for login_from_db in logins_from_db:
            if(login_from_db.user != user and login_from_db.ip_address != ip_add and login_from_db.date != date_time):
                new_login = Login(user = user, date = date_time, ip_address = ip_add, line = 'Vty 0', device='Core-Router')
                try:
                    db.session.add(new_login)
                    db.session.commit()

                except:
                    print('There was a problem adding that login attempt')

# Fetching Temperatures
i = 0
j = 0

temps         = []
chassis_temps = []
timelist      = []

with open('/root/Temp_logs_router.txt','r') as f:
    for line in f:
        for word in line.split():
            chassis_temps.append(word)

while j < len(chassis_temps):
    if("CPU" == chassis_temps[j]):
      if("temperature" in chassis_temps[j+1]):
        j+=2
        temps.append(chassis_temps[j])
        timelist.append(datetime.now())
        break
    j+=1
# print(temps)

for i in range(0, len(temps)): 
    temps[i] = int(temps[i])


# print(timelist)

# Adding temperature stats to db
temp_time = zip(temps, timelist)
temps_from_db = Temperature.query.filter_by(device='Core-Router').all()
for (temp, time) in temp_time:
    if not temps_from_db:
        new_temp = Temperature(temperature=temp, time=time, device='Core-Router')
        try:
            db.session.add(new_temp)
            db.session.commit()

        except:
            print('There was a problem adding that temperature stats')
    else:
        for temp_from_db in temps_from_db:
            if(temp_from_db.time != time):
                new_temp = Temperature(temperature=temp, time=time, device='Core-Router')
                try:
                    db.session.add(new_temp)
                    db.session.commit()

                except:
                    print('There was a problem adding that temperature stats')

# ************* CORE ROUTER Ends *************

@app.route('/')
def index():
    return render_template('index.html')

#************* CORE ROUTER *************
@app.route('/core_router')
def core_router():
    interfaces = Interface.query.filter_by(device='Core-Router').order_by(Interface.date.desc()).all()
    logins = Login.query.filter_by(device='Core-Router').all()
    return render_template('details.html', interfaces=interfaces, logins=logins, temps=temps)

@app.route('/core_router/ports_stats')
def core_router_ports():
    interfaces = Interface.query.filter_by(device='Core-Router').order_by(Interface.date.desc()).all()
    return render_template('ports_stats.html', interfaces=interfaces)

@app.route('/core_router/login_stats')
def core_router_login():
    logins = Login.query.filter_by(device='Core-Router').all()
    return render_template('login_stats.html', logins=logins)

@app.route('/core_router/temps')
def core_router_temps():
    tempslist = []
    temps_from_db = Temperature.query.filter_by(device='Core-Router').order_by(Temperature.time).all()
    for temp_from_db in temps_from_db:
        tempslist.append(temp_from_db.temperature)

    return jsonify({'temperatures': tempslist})


#************* CORE SWITCH 1 *************
@app.route('/core_switch1')
def core_switch1():
    interfaces = Interface.query.filter_by(device='Core-Switch-1').order_by(Interface.date.desc()).all()
    logins = Login.query.filter_by(device='Core-Switch-1').all()
    return render_template('details.html', interfaces=interfaces, logins=logins)

@app.route('/core_switch1/ports_stats')
def core_switch1_ports():
    interfaces = Interface.query.filter_by(device='Core-Switch-1').order_by(Interface.date.desc()).all()
    return render_template('ports_stats.html', interfaces=interfaces)

@app.route('/core_switch1/login_stats')
def core_switch1_login():
    logins = Login.query.filter_by(device='Core-Switch-1').all()
    return render_template('login_stats.html', logins=logins)

#************* CORE SWITCH 2 *************
@app.route('/core_switch2')
def core_switch2():
    interfaces = []
    logins = []
    interfaces = Interface.query.filter_by(device='Core-Switch-2').order_by(Interface.date.desc()).all()
    logins = Login.query.filter_by(device='Core-Switch-2').all()
    if len(interfaces) == 0:
        interfaces.append(Interface(device='Core-Switch-2', port='', status='', date=None))

    return render_template('details.html', interfaces=interfaces, logins=logins)

@app.route('/core_switch2/ports_stats')
def core_switch2_ports():
    interfaces = Interface.query.filter_by(device='Core-Switch-2').order_by(Interface.date.desc()).all()
    if len(interfaces) == 0:
        interfaces.append(Interface(device='Core-Switch-2', port='', status='', date=None))
    return render_template('ports_stats.html', interfaces=interfaces)

@app.route('/core_switch2/login_stats')
def core_switch2_login():
    logins = Login.query.filter_by(device='Core-Switch-2').all()
    return render_template('login_stats.html', logins=logins)

@app.route('/core_switch2/temps')
def core_switch2_temps():
    tempslist = []
    temps_from_db = Temperature.query.filter_by(device='Core-Switch-2').order_by(Temperature.time).all()
    for temp_from_db in temps_from_db:
        tempslist.append(temp_from_db.temperature)

    return jsonify({'temperatures': tempslist})


#************* ACCESS SWITCH 1 *************

@app.route('/access_switch1')
def access_switch1():
    interfaces = Interface.query.filter_by(device='Access-Switch-1').all()
    logins = Login.query.filter_by(device='Access-Switch-1').all()
    return render_template('details.html', interfaces=interfaces, logins=logins)

@app.route('/access_switch1/ports_stats')
def access_switch1_ports():
    interfaces = Interface.query.filter_by(device='Access-Switch-1').all()
    return render_template('ports_stats.html', interfaces=interfaces)

@app.route('/access_switch1/login_stats')
def access_switch1_login():
    logins = Login.query.filter_by(device='Access-Switch-1').all()
    return render_template('login_stats.html', logins=logins)

#************* ACCESS SWITCH 2 *************
@app.route('/access_switch2')
def access_switch2():
    interfaces = Interface.query.filter_by(device='Access-Switch-2').all()
    logins = Login.query.filter_by(device='Access-Switch-2').all()
    return render_template('details.html', interfaces=interfaces, logins=logins)

@app.route('/access_switch2/ports_stats')
def access_switch2_ports():
    interfaces = Interface.query.filter_by(device='Access-Switch-2').all()
    return render_template('ports_stats.html', interfaces=interfaces)

@app.route('/access_switch2/login_stats')
def access_switch2_login():
    logins = Login.query.filter_by(device='Access-Switch-2').all()
    return render_template('login_stats.html', logins=logins)

#********************************************

if __name__ == "__main__":
    app.run(debug=True, host='172.30.211.14')

