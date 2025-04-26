from scripts.db import conn, cursor
import os
import time
from werkzeug.utils import secure_filename

ALLOWED_EXTENSIONS = {'pdf', 'docx', 'pptx', 'txt'}

def allowedFile(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def generateUniqueFilename(original_filename, title=None):
    timestamp = int(time.time())
    ext = os.path.splitext(original_filename)[1]
    safe_title = secure_filename(title or 'note')[:20].replace(" ", "_")
    return f"{safe_title}_{timestamp}{ext}"

def saveFile(file, upload_folder, unique_filename):
    if not os.path.exists(upload_folder):
        os.makedirs(upload_folder)
    filepath = os.path.join(upload_folder, unique_filename)
    file.save(filepath)
    return filepath

def uploadNotes(title, subject, category, description, path):
    filename = os.path.basename(path)
    query = "INSERT INTO `notes` (`Id`, `Title`, `Subject`, `Category`, `Description`, `File`, `Date`) VALUES (NULL, %s, %s, %s, %s, %s, current_timestamp())"
    value = (title, subject, category, description, filename)
    try:
        cursor.execute(query, value)
        conn.commit()
        return "Notes uploaded successfully.", True
    except Exception as e:
        return "Failed to upload notes, Try again.", False
    
def fetchNotes():
    query = "SELECT * FROM `notes`"
    try:
        cursor.execute(query)
        result = cursor.fetchall()
        notes = [{
                'title': row[1],
                'subject': row[2],
                'category': row[3],
                'description': row[4],
                'file': row[5],}
            for row in result
        ]
        return "Notes Fetched.", True, notes
    except Exception as e:
        return "Error fetching notes, Try again.", False, None
    
def weeklyNotesUpload():
    weekdays = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
    notes_data = dict.fromkeys(weekdays, 0)
    cursor.execute("""SELECT DAYNAME(Date) AS day, COUNT(*) AS count FROM notes WHERE Date >= CURDATE() - INTERVAL 6 DAY GROUP BY DAY""")
    for day, count in cursor.fetchall():
        if day in notes_data:
            notes_data[day] = count
    notesList = [notes_data[day] for day in weekdays]
    return notesList

def userEngagement():
    cursor.execute("""SELECT Activation, COUNT(*) AS count FROM user GROUP BY Activation""")
    userStats = dict(cursor.fetchall())
    return userStats