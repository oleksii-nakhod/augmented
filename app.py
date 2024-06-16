from flask import Flask, render_template, request, redirect, url_for, send_from_directory
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
from werkzeug.utils import secure_filename
import os
import shortuuid

app = Flask(__name__)
app.config["MONGO_URI"] = "mongodb://localhost:27017/augmented"
mongo = PyMongo(app)
app.config['UPLOAD_FOLDER'] = 'uploads'

if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])


@app.route('/')
def index():
    markers = mongo.db.markers.find()
    return render_template('index.html', markers=markers)

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        marker = {}
        for file_key in request.files:
            file = request.files[file_key]
            filename = generate_unique_filename(file.filename)
            filename = secure_filename(filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            marker[file_key] = filename
        
        mongo.db.markers.insert_one(marker)
            
        return redirect(url_for('markers'))
    return render_template('upload.html')

@app.route('/delete/<id>')
def delete(id):
    marker = mongo.db.markers.find_one({'_id': ObjectId(id)})
    mongo.db.markers.delete_one({'_id': ObjectId(id)})
    for key in marker:
        if key == '_id':
            continue
        if os.path.exists(os.path.join(app.config['UPLOAD_FOLDER'], marker[key])):
            os.remove(os.path.join(app.config['UPLOAD_FOLDER'], marker[key]))
    
    return redirect(url_for('markers'))

@app.route('/markers')
def markers():
    markers = mongo.db.markers.find()
    return render_template('markers.html', markers=markers)


@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)
    
def generate_unique_filename(original_filename):
    name, ext = os.path.splitext(original_filename)
    unique_id = shortuuid.uuid()
    new_filename = f"{name}_{unique_id}{ext}"
    return new_filename

if __name__ == '__main__':
    app.run(debug=True, port=5005)
