import base64
import numpy as np
import io
from PIL import Image
import tensorflow as tf
# from tensorflow import keras
# from tensorflow.keras.models import Sequential, load_model
# from keras.models import load_model
# from tensorflow.keras.preprocessing.image import ImageDataGenerator, img_to_array
from flask import request,render_template
from flask import jsonify
from flask import Flask
import os

os.environ['CUDA_VISIBLE_DEVICES'] = '-1'

app = Flask(__name__)

def get_model():
    global model
    model = tf.keras.models.load_model('Models/my_model1.h5')
    print(" * Model loaded!")

print(" * Loading Keras model...")
get_model()

def preprocess_image(image, target_size):
    if image.mode != "RGB":
        image = image.convert("RGB")
    image = image.resize(target_size)
    image = tf.keras.preprocessing.image.img_to_array(image)
    image = np.expand_dims(image, axis=0)
    return image

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/test")
def rand_123():
    message = request.get_json(force=True)
    encoded = message['image']
    decoded = base64.b64decode(encoded)
    image = Image.open(io.BytesIO(decoded))
    image = image.rotate(45)
    width, height = image.size
    image = image.crop((0, 0, width/2, height/2))
    image = image.resize((width*2, height*2))
    processed_image = preprocess_image(image, target_size=(100,100))
    return processed_image


@app.route('/predict',methods=['POST'])
def predict():
    message = request.get_json(force=True)
    encoded = message['image']
    decoded = base64.b64decode(encoded)
    image = Image.open(io.BytesIO(decoded))
    processed_image = preprocess_image(image, target_size=(100,100))

    prediction = model.predict(processed_image).tolist()

    response = {
        'prediction': {
            'Cloudy': prediction[0][0],
            'Sunny': prediction[0][1],
            'Rainy': prediction[0][2],
            'Snowy': prediction[0][3],
            'Foggy': prediction[0][4],
        }
    }
    return jsonify(response)

if __name__=="__main__":
    app.run(debug=True)    
