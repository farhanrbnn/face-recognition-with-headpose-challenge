from app import app, socketio
from flask import render_template, jsonify, request, redirect, Response
from flask_socketio import emit, send
from pymongo import MongoClient
from app.camera import VideoCamera
from app.pose_module import FacePosition
from bson.objectid import ObjectId
from PIL import Image
from gpiozero import LED, Button
from gpiozero.pins.pigpio import PiGPIOFactory
from signal import pause
from imutils.video import WebcamVideoStream
from imutils.video import FPS
import face_recognition as fr 
import cv2
import json 
import pickle
import base64
import numpy as np 
import io
import os.path
import random
import time
import string


# cap = cv2.VideoCapture(0)
cap = WebcamVideoStream(src=2).start()

# db initialize
client = MongoClient('mongodb://localhost:27017')
db = client.employees_data
data = db.data

# define module
video_stream = VideoCamera(cap)
pose = FacePosition(cap)

# route to landing page
@app.route('/', methods = ['GET'])
def home():
    return render_template('landing-page.html')

@socketio.on('connect', namespace = '/greet')
def connect():
    print('clinet connect')

# get all name from database
@app.route('/employees', methods = ['GET'])
def list_employee():
    try:
        employees = data.find()
        return render_template('employees.html', employees = employees), 200

    except Exception as e:
        error_message = 'error ' + str(e)

        return error_message, 500

# route to store data to database
@app.route('/employees', methods = ['POST'])
def post_t():
    try: 
        image = request.form['image']       
        nama = request.form['nama']
        nik = request.form['nik']
        jabatan = request.form['jabatan']
        new_employee = {'image':image, 'nama':nama, 'nik': nik, 'jabatan':jabatan}
    
        new_data = data.insert_one(new_employee)

        return redirect('/employees')

    except Exception as e:
        error_message = 'error ' + str(e)
        
        return error_message, 500

def id_generator(size=6, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))

#API for get encoding from image registration
@app.route('/employees/encode', methods = ['POST'])
def get_encode():
    try:
        get_data = request.get_json()
        arr_image = get_data['images']
        name = get_data['name']

        known_encoding = []
        known_name = []
        name_pickle = []
        encoding_pickle = []

        for image in arr_image:
            encoded_image = image.split(",")[1]
            decoded_image = base64.b64decode(encoded_image)
            frame = cv2.imdecode(np.frombuffer(decoded_image, np.uint8), -1)

            cv2.imwrite('./dataset/{}.png'.format(id_generator()), frame)

            face_locations = fr.face_locations(frame, number_of_times_to_upsample = 0, model = 'cnn')
            face_encodings = fr.face_encodings(frame, known_face_locations = face_locations)[0]

            known_encoding.append(face_encodings)
            known_name.append(name)

        to_pickle = {'names':known_name, 'encodings':known_encoding}
        to_pickle = {'names':known_name, 'encodings':known_encoding}   

        if os.path.exists('encodings.pickle'):
            with open('encodings.pickle', 'rb') as data:
                pickle_data = pickle.load(data)

                print(pickle_data)
                list_name = pickle_data['names']
                list_encodings = pickle_data['encodings']

                for new_name in to_pickle['names']:
                    list_name.append(new_name)

                for new_encodings in to_pickle['encodings']:
                    list_encodings.append(new_encodings)

                with open('encodings.pickle', 'wb') as data:
                    pickle_data.update(names = list_name, encodings = list_encodings)
                    data.write(pickle.dumps(pickle_data))
                    data.close()

                arr_name = pickle_data['names']
                arr_encodings = pickle_data['encodings']

                for new_name in to_pickle['names']:
                    arr_name.append(new_name)

                for new_encodings in to_pickle['encodings']:
                    arr_encodings.append(new_encodings)

                with open('encodings.pickle', 'wb') as data:
                    pickle_data.update(names = arr_name, encodings = arr_encodings)
                    data.write(pickle.dumps(pickle_data))
                    data.close()

        else:
            new_pickle = open('encodings.pickle', 'wb')
            pickle_dump = new_pickle.write(pickle.dumps(to_pickle))
            new_pickle.close()

        return redirect('/employees')

    except Exception as e:
        error_message = 'error ' + str(e)
        
        return error_message

# route to  form page
@app.route('/employees/new', methods=['GET', 'POST'])
def index():
    return render_template('index.html')

# get all details form /employees route 
@app.route('/employees/<_id>', methods = ['GET'])
def detail(_id):
    try:
        employees = data.find({'_id':ObjectId(_id)})
        return render_template('detail.html', employees = employees)

    except Exception as e:
        error_message = 'error ' + str(e)

        return error_message, 500

# delete one document based on id 
@app.route('/employees/delete/<_id>', methods = ['GET'])
def delete_doc(_id):
    employees = data.delete_one({'_id':ObjectId(_id)})

    return redirect('/employees')

def gen():
    status = True

    a = ['right', 'left']

    # factory = PiGPIOFactory('192.168.0.103')
    # red = LED(17, pin_factory = factory)
    random_one = random.choice(a)

    timeout = 20
    countdown = timeout

    fps = FPS().start()
    
    time.sleep(2)
    while True:
        fps.update()

        countdown -= 1

        head_pose = pose.run()
        frame = video_stream.get_frame()

        print(random_one)

        if len(frame[1]) >= 1 and status:
            # print('HELLO {}'.format(frame[1][0]))
            # print('look to your {}'.format(random_one))

            header = 'look to your {}'.format(random_one)

            socketio.emit('name', {'oi':frame[1][0]})
            socketio.emit('pose', {'pose':header})

            status = False

        elif len(frame[1]) == 1 and countdown == 0:
            print('try again')

            gen()
            countdown = timeout

        if len(frame[1]) >= 1 and head_pose == random_one:
            
            socketio.emit('access')

            # red.on()
            # time.sleep(1)
            # red.off()
            time.sleep(1)

            socketio.emit('reload')

            status = False

            gen()

        fps.stop()
        # print("[INFO] approx. FPS: {:.2f}".format(fps.fps()))

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame[0] + b'\r\n\r\n')

@app.route('/greet', methods = ['GET'])
def tes():
    return render_template('greetings.html')
        
@app.route('/video-feed')
def video_feed():
    return Response(gen(),
                    mimetype = 'multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    # app.run(host = '10.10.10.10', port = '5000', debug = True, threaded = True, ssl_context = 'adhoc')
    socketio.run(app, threaded = True, ssl_context = 'adhoc')


"""
TO DO: 
2. DELETE SPESIFIC NAME AND ENCODING )
"""