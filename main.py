#######################################################################################
#REMOTE-SERVER-MANAGEMENT-TOOL
#DEVELOPER: KETAN SOLANKI 
#VERSION: 1.0
#######################################################################################
from flask import Flask,redirect,url_for,request,session,flash,render_template
import paramiko, random
from datetime import timedelta

#######################################################################################
#FUNCTION FOR THE FILE TRANSFER
#######################################################################################
def transfer(client,local_path,remote_path,mode):
    sftp_client = client.open_sftp()
    if mode == "upload":
        try:
            sftp_client.put(localpath=local_path, remotepath=remote_path)
        except Exception as e:
            flash(f"Exception: {e}")
            exit
        finally:
            return True
    if mode == "download":
        try:
            sftp_client.get(remotepath=remote_path, localpath=local_path)
        except Exception as e:
            flash(f"Exception: {e}")
            exit
        finally:
            return True
###########################################################################################
###########################################################################################

app = Flask(__name__)
keyint = random.randrange(1,100)
app.secret_key = str(keyint)
app.permanent_session_lifetime = timedelta(minutes=15)


@app.route('/',methods=["POST","GET"])
def home():
    render_template('index.html')
    if request.method == "POST":
        session.permanent = True #setting session for 15 mins
        #getting data form the form
        host = request.form['host']
        keyFile = request.form['keyFile']
        username = request.form['username']
        #creating the SSH client
        global client 
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        try:
            #Establishing the connection
            client.connect(hostname=host,port=22,username=username,key_filename=keyFile)
            if client:
                session['username'] = username
                return redirect(url_for("dashboard"))
            
        except Exception as e:
            flash(f"Exception Occurred while connecting!! : {e}")
            return render_template("index.html")
    else:
        return render_template("index.html")


###########################################################################################
#DASHBOARD
###########################################################################################

@app.route('/dashboard', methods=["POST","GET"])
def dashboard():
    if 'username' in session: #CHECK THE ACTIVE SESSION
        cpu_usage_command = "top -bn1 | grep 'Cpu(s)' | sed 's/.*, *\\([0-9.]*\\)%* id.*/\\1/' | awk '{print 100 - $1}'"
        memory_usage_command = "free -m | awk 'NR==2{printf \"Total: %.2f GB, Used: %.2f GB, Free: %.2f GB\", $2/1024, $3/1024, $4/1024}'"
        disk_usage_command = "df -h / | awk 'NR==2 {print \"Total: \" $2 \", Used: \" $3 \", Available: \" $4 \", Usage: \" $5}'"
        
        stdin,stdout,stderr = client.exec_command(command=cpu_usage_command)
        cpu_usage = stdout.read().decode()
        std, stdout, stderr = client.exec_command( command=memory_usage_command)
        memory_usage = stdout.read().decode()
        stdin, stdout, stderr = client.exec_command( command=disk_usage_command)
        disk_usage = stdout.read().decode()
    
        if request.method == "POST":
            action = request.form['action']

            if action == 'execute':
                cmd = request.form['cmd']   
                stdin, stdout, stderr = client.exec_command(command = cmd)
                if stdout:
                    output = stdout.read().decode()
                    return render_template("dashboard.html",output = output,cpu_usage=cpu_usage,memory_usage=memory_usage, disk_usage = disk_usage)
                elif stderr:
                    err = stderr.read().decode()
                    flash(err)
                    return render_template("dashboard.html",cpu_usage=cpu_usage,memory_usage=memory_usage,disk_usage = disk_usage)    
                return render_template('dashboard.html',cpu_usage=cpu_usage,memory_usage=memory_usage,disk_usage = disk_usage)
            
            elif action == 'upload':
                mode = "upload"
                localPath = request.form['local_path']  
                remotePath = request.form['remote_path']
            
                status = transfer(client=client,local_path=localPath,remote_path=remotePath,mode=mode)
                if status:
                    output = "Transfer Success!!"
                    return render_template("dashboard.html", output=output,cpu_usage=cpu_usage,memory_usage=memory_usage,disk_usage = disk_usage)
                
            elif action == 'download':  
                mode = "download"
                localPath = request.form['local_path']
                remotePath = request.form['remote_path']
                status = transfer(client=client,local_path=localPath,remote_path=remotePath,mode=mode)
                
                if status:
                    return render_template("dashboard.html",output = "Transfer Success!!",cpu_usage=cpu_usage,memory_usage=memory_usage,disk_usage = disk_usage)
            return render_template("dashboard.html",cpu_usage=cpu_usage,memory_usage=memory_usage,disk_usage = disk_usage)
        else:
            
            return render_template("dashboard.html")
        
    else:
        return redirect(url_for('home'))

###########################################################################################
#LOGOUT
###########################################################################################

@app.route("/logout/")
def logout():
    if 'username' in session:
        session.pop('username',None)
        flash("logged out!!")
        client.close()
        return redirect(url_for("home"))
    else:
        flash("No active Session!!")
        return redirect(url_for('home'))

if __name__ == "__main__":
    app.run(debug=True,
            host='0.0.0.0',
            port=5000)