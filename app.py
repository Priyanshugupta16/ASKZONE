import os
from flask import Flask, render_template, request, redirect, url_for, flash, session, send_from_directory
from scripts.user import registerUser, activate, loginUser, fetchUser, updateProfile, sendPasswordResetMail, resetPassword
from scripts.notesData import userEngagement, weeklyNotesUpload, generateUniqueFilename, saveFile, allowedFile, uploadNotes, fetchNotes
from werkzeug.utils import secure_filename
from flask_socketio import SocketIO, send
import eventlet
eventlet.monkey_patch()


app = Flask(__name__)
app.secret_key = b'\x02\x81I\r\x88~E\x17\xaf\xf7\xfd\x8d;\xd5M\xd8\x95Xj\xf2\xab\xc8\xd6\xe8'
socketio = SocketIO(app)

UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

UPLOAD_FOLDER_AVATAR = 'static/uploads/avatar'
app.config['UPLOAD_FOLDER_AVATAR'] = UPLOAD_FOLDER_AVATAR

@app.route('/')
def home():
    if ('login' in session) & (session.get('login') == True):
        return redirect(url_for('dashboard'))
    return render_template('landingPage.html')

@app.route('/dashboard')
def dashboard():
    if ('login' in session) & (session.get('login') == True):
        userName = session['user']['name']
        userStats = userEngagement()
        notesList = weeklyNotesUpload()
        return render_template('dashboard.html', userName=userName, userStats=userStats, notesList=notesList)
    else:
        message = "You need to login first."
        flash(message, "error")
        return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        message, isLoggedIn, name = loginUser(email=email, password=password)
        if isLoggedIn:
            session['login'] = True
            session['user'] = {
                'name': name,
                'email': email
            }
            return redirect(url_for('dashboard'))
        else:
            flash(message, "error")
            return redirect(url_for('login'))
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        branch = request.form.get('branch')
        specialization = request.form.get('specialization')
        semester = request.form.get('semester')
        bestSubject = request.form.get('bestSubject')
        cgpa = request.form.get('cgpa')
        password = request.form.get('password')
        
        message, isRegistered = registerUser(name=name, email=email, branch=branch, specialization=specialization, semester=semester, bestSubject=bestSubject, cgpa=cgpa, password=password)

        if isRegistered:
            return redirect(url_for('login'))
        else:
            return render_template('registration.html', error=message)
    return render_template('registration.html')

@app.route('/upload', methods=['GET', 'POST'])
def notesUpload():
    if ('login' in session) & (session.get('login') == True):
        if request.method == 'POST':
            title = request.form.get('title')
            subject = request.form.get('subject')
            category = request.form.get('category')
            description = request.form.get('description')
            file = request.files.get('file')
            if file and allowedFile(file.filename):
                filename = generateUniqueFilename(file.filename, title)
                filepath = saveFile(file, app.config['UPLOAD_FOLDER'], filename)
                message, isUploaded = uploadNotes(title=title, subject=subject, category=category, description=description, path=filepath)
                if isUploaded:
                    return redirect(url_for('browseNotes'))
                else:
                    return render_template('upload.html', error=message)
            else:
                message = "Invalid file, Try again."
                return render_template('upload.html', error=message)
        return render_template('upload.html')
    else:
        message = "You need to login first."
        flash(message, "error")
        return redirect(url_for('login'))

@app.route('/browse')
def browseNotes():
    if ('login' in session) & (session.get('login') == True):
        message, isFetched, notes = fetchNotes()
        if isFetched:
            return render_template('browsenotes.html', notes=notes)
        else:
            return render_template('browsenotes.html', error=message)
    else:
        message = "You need to login first."
        flash(message, "error")
        return redirect(url_for('login'))

@app.route('/uploads/<filename>')
def fileDownload(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/profile', methods=['GET', 'POST'])
def profile():
    if ('login' in session) & (session.get('login') == True):
        if request.method == 'POST':
            name = request.form.get('name')
            email = session['user']['email']
            branch = request.form.get('branch')
            avatar = request.files['profilePic']

            filename = None
            if avatar and avatar.filename != '':
                filename = generateUniqueFilename(avatar.filename, title=name)
                filepath = os.path.join(app.root_path, app.config['UPLOAD_FOLDER_AVATAR'], filename)
                avatar.save(filepath)
                message, isUpdated = updateProfile(name=name, email=email, branch=branch, avatar=filename)
                if isUpdated:
                    return redirect(url_for('profile'))
                else:
                    return render_template('profile.html', error=message)
            else:
                message, isUpdated = updateProfile(name=name, email=email, branch=branch, avatar="None")
                if isUpdated:
                    return redirect(url_for('profile'))
                else:
                    return render_template('profile.html', error=message)
        email = session['user']['email']
        message, isFetched, details = fetchUser(email=email)
        if isFetched:
            return render_template('profile.html', details=details)
        else:
            return render_template('profile.html', error=message)
    return redirect(url_for('login'))

@app.route('/chat')
def chat():
    if ('login' in session) & (session.get('login') == True):
        return render_template('chat.html')
    return redirect(url_for('login'))

@app.route('/forgotpass', methods=['GET', 'POST'])
def forgotPass():
    if ('login' in session) & (session.get('login') == True):
        return redirect(url_for('dashboard'))
    else:
        if request.method == 'POST':
            email = request.form.get('email')
            message, isEmailSend = sendPasswordResetMail(email=email)
            if isEmailSend:
                return redirect(url_for('login'))
            else:
                return render_template('forgotpass.html', error=message)
        return render_template('forgotpass.html')

@app.route('/resetpass/<token>', methods=['GET', 'POST'])
def resetpass(token):
    if ('login' in session) & (session.get('login') == True):
        return redirect(url_for('login'))
    else:
        if request.method == 'POST':
            password = request.form.get('password')
            message, isReset = resetPassword(token=token, password=password)
            if isReset:
                flash(message, "success")
                return redirect(url_for('login'))
            else:
                return render_template('forgotpass.html', showResetForm=True, error=message, token=token)
        return render_template('forgotpass.html', showResetForm=True, token=token)

@app.route('/activate/<token>')
def activateAccount(token):
    message, isActivated = activate(token=token)
    if isActivated:
        flash(message, "success")
        return redirect(url_for('login'))
    else:
        flash(message, "error")
        return redirect(url_for('login'))

@app.route('/logout')
def logout():
    session.clear()
    message = "Logged out successfully."
    flash(message, "success")
    return redirect(url_for('login'))

@socketio.on('message')
def handle_message(data):
    send(data, broadcast=True)


if __name__ == '__main__':
    socketio.run(app, debug=True)
    