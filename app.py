from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI']        = 'mysql+pymysql://root:xflow@123@localhost/xflow_monitoring_system'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class Interface(db.Model):
    id          = db.Column(db.Integer, primary_key=True)
    port        = db.Column(db.String(100), nullable=False)
    ip_address  = db.Column(db.String(100), nullable=False)
    status      = db.Column(db.String(100), nullable=False)
    device      = db.Column(db.String(100), nullable=False)

    def __init__(self, port, ip_address, status, device):
        self.port       = port
        self.ip_address = ip_address
        self.status     = status
        self.device     = device

# ************* CORE SWITCH 1 Starts *************
i               = 8
j               = 0
interfaces      = []
ports           = []
ip_addresses    = []
vlans           = []
statuses        = []
with open('/root/switch_int.txt','r') as f:
    for line in f:
        for word in line.split():
            interfaces.append(word)

while i < 504:
   if("Vlan" in interfaces[i] ):
     if("," in interfaces[i+7]):
       i+=8
       continue
     else:
       i+=7
       continue
   ports.append(interfaces[i])
   i+=1
   ip_addresses.append(interfaces[i])
   i+=3
   if(interfaces[i]=="administratively"):
     i+=1
   statuses.append(interfaces[i])
   i+=3

ports_ip_statuses = zip(ports, ip_addresses, statuses)
for (port,ip_address,status) in ports_ip_statuses:
    interface = Interface.query.filter_by(port=port, device='Core-Switch-1').first()
    
    #If interface already exists then update interface else add interface to db
    if interface != None:
        if (interface.status != status or interface.port != port or interface.ip_address != ip_address):
            interface.status     = status
            interface.ip_address = ip_address

            try:
                print('Updating')
                db.session.commit()
            except:
                print('There was a problem updating that interface')
    else:
        new_interface = Interface(port=port, status=status, ip_address=ip_address, device='Core-Switch-1')

        try:
            db.session.add(new_interface)
            db.session.commit()

        except:
            print('There was a problem creating that interface')
# ************* CORE SWITCH 1 Ends *************

# ************* CORE ROUTER Starts *************
i            = 8
j            = 0
interfaces   = []
ports        = []
ip_addresses = []
statuses     = []

with open('/root/Router.txt','r') as f:
    for line in f:
        for word in line.split():
            interfaces.append(word)

while i < 40:
   ports.append(interfaces[i])
   i+=1
   ip_addresses.append(interfaces[i])
   i+=3
   if(interfaces[i]=="administratively"):
     i+=1
   statuses.append(interfaces[i])
   i+=3

ports_ip_statuses = zip(ports, ip_addresses, statuses)
for (port,ip_address,status) in ports_ip_statuses:
    interface = Interface.query.filter_by(port=port, device='Core-Router').first()
    
    #If interface already exists then update interface else add interface to db
    if interface != None:
        if (interface.status != status or interface.port != port or interface.ip_address != ip_address):
            interface.status     = status
            interface.ip_address = ip_address

            try:
                print('Updating')
                db.session.commit()
            except:
                print('There was a problem updating that interface')
    else:
        new_interface = Interface(port=port, status=status, ip_address=ip_address, device='Core-Router')

        try:
            db.session.add(new_interface)
            db.session.commit()

        except:
            print('There was a problem creating that interface')

# ************* CORE ROUTER Ends *************

@app.route('/')
def index():
    return render_template('index.html')

#************* CORE ROUTER *************
@app.route('/core_router')
def core_router():
    interfaces = Interface.query.filter_by(device='Core-Router').all()
    return render_template('details.html', interfaces=interfaces)

@app.route('/core_router/ports_stats')
def core_router_ports():
    interfaces = Interface.query.filter_by(device='Core-Router').all()
    return render_template('ports_stats.html', interfaces=interfaces)

@app.route('/core_router/login_stats')
def core_router_login():
    # interfaces = Interface.query.filter_by(device='Core-Router').all()
    return render_template('login_stats.html')

#************* CORE SWITCH 1 *************
@app.route('/core_switch1')
def core_switch1():
    interfaces = Interface.query.filter_by(device='Core-Switch-1').all()
    return render_template('details.html', interfaces=interfaces)

@app.route('/core_switch1/ports_stats')
def core_switch1_ports():
    interfaces = Interface.query.filter_by(device='Core-Switch-1').all()
    return render_template('ports_stats.html', interfaces=interfaces)

@app.route('/core_switch1/login_stats')
def core_switch1_login():
    # interfaces = Interface.query.filter_by(device='Core-Switch-1').all()
    return render_template('login_stats.html')

#************* CORE SWITCH 2 *************
@app.route('/core_switch2')
def core_switch2():
    interfaces = Interface.query.filter_by(device='Core-Switch-2').all()
    return render_template('details.html', interfaces=interfaces)

@app.route('/core_switch2/ports_stats')
def core_switch2_ports():
    interfaces = Interface.query.filter_by(device='Core-Switch-2').all()
    return render_template('ports_stats.html', interfaces=interfaces)

@app.route('/core_switch2/login_stats')
def core_switch2_login():
    # interfaces = Interface.query.filter_by(device='Core-Switch-2').all()
    return render_template('login_stats.html')

#************* ACCESS SWITCH 1 *************

@app.route('/access_switch1')
def access_switch1():
    interfaces = Interface.query.filter_by(device='Access-Switch-1').all()
    return render_template('details.html', interfaces=interfaces)

@app.route('/access_switch1/ports_stats')
def access_switch1_ports():
    interfaces = Interface.query.filter_by(device='Access-Switch-1').all()
    return render_template('ports_stats.html', interfaces=interfaces)

@app.route('/access_switch1/login_stats')
def access_switch1_login():
    # interfaces = Interface.query.filter_by(device='Access-Switch-1').all()
    return render_template('login_stats.html')

#************* ACCESS SWITCH 2 *************
@app.route('/access_switch2')
def access_switch2():
    interfaces = Interface.query.filter_by(device='Access-Switch-2').all()
    return render_template('details.html', interfaces=interfaces)

@app.route('/access_switch2/ports_stats')
def access_switch2_ports():
    interfaces = Interface.query.filter_by(device='Access-Switch-2').all()
    return render_template('ports_stats.html', interfaces=interfaces)

@app.route('/access_switch2/login_stats')
def access_switch2_login():
    # interfaces = Interface.query.filter_by(device='Access-Switch-2').all()
    return render_template('login_stats.html')

#********************************************

if __name__ == "__main__":
    app.run(debug=True, host='172.30.211.14')
