# Importing required libraries
import base64
from fileinput import filename
import os
import numpy as np
import tensorflow as tf
from tensorflow.keras.models import model_from_json
from flask.helpers import flash
from flask import Flask, flash, render_template, request, redirect, url_for
from werkzeug.utils import secure_filename
import matplotlib.pyplot as plt
from PIL import Image
import PIL


# Specifying the path to store uploaded images
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}

# Loading the model json file
json_file = open('model.json', 'r')
loaded_model_json = json_file.read()
json_file.close()

# Using Keras model_from_json to make a loaded model
loaded_model = model_from_json(loaded_model_json)

# Loading weights into new model
loaded_model.load_weights("model.h5")
print("Loaded Model from disk")

# Compiling and evaluvating loaded model
loaded_model.compile(loss=["binary_crossentropy", "mae"],
                     optimizer='Adam', metrics=['accuracy'])


# Initiating flask instance
app = Flask(__name__)

# Adding uploading directory to flask app configuration
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.secret_key = b'_5#y2L"FYIOz\n\xec]/'

# Checking if the file extension is in allowed types


def allowed_file(filename):
    return ('.' in filename) and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# gray_img=cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
def convert_image_to_array(image_path):
    im = Image.open(image_path).convert('L')
    im = im.resize((48,48))
    image_array = np.array(im)
    print(image_array.shape)
    print(image_array)
    return image_array

# (48,48,1) -> input
# Model=model((48,48,1))
# Model.summary()



def predict_image(array, loaded_model = loaded_model):

    plt.imshow(array)

    image_test = array

    pred_1 = loaded_model.predict(np.array([image_test]))

    sex_f = ['Male','Female']
    print(pred_1)

    age = int(np.round(pred_1[1][0]))

    sex = int(np.round(pred_1[0][0]))

    print("Predicted Age:",int(age/100))

    print("Predicted Sex:",sex_f[sex])

    return [int(age/100), sex_f[sex]]


#### App Routes ####

@app.route('/')
def home():
    return render_template('index.html', predictions = None)


@app.route('/predict', methods=['POST'])
def predict():
    if 'file' not in request.files:
        flash('No file part')
        return 'No files Uploaded'
    file = request.files['file']
    file
    if file.filename == '':
        flash('No selected file')
        return 'Please Select a File!'
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER']+"/"+filename))

        with open(os.path.join(app.config['UPLOAD_FOLDER']+"/"+filename), "rb") as image2string:
           converted_string = base64.b64encode(image2string.read())
        #    print(converted_string)
           converted_string = converted_string.decode('UTF-8') 
           converted_string ='data:image/jpeg;base64,' +converted_string

        image_array = convert_image_to_array(
            app.config['UPLOAD_FOLDER']+"/"+filename)
        predictions = predict_image(image_array)
        print(predictions)
        return render_template('index.html', predictions = predictions, image = converted_string)


if __name__ == '__main__':
    app.run(debug=True)

