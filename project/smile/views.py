from django.shortcuts import render
from django.views.decorators import gzip
from django.http import StreamingHttpResponse, HttpResponseServerError
import cv2,time
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.image import img_to_array
import numpy as np
from statistics import mode

context = {
    'title': 'Home'
}

# model path
detection_model_path = 'C:/dev/finalProject/project/smile/detection_models/haarcascade_frontalface_default.xml'
emotion_model_path = 'C:/dev/finalProject\project\smile\emotion_models\_vgg16_01_.34-0.77-0.6478.h5'
emotion_labels = ["happy", "angry", "sad", "neutral", "surprise"]

# initialization
frame_window = 30
emotion_window = []
best_prob =[]



class VideoCamera_smile:
    global detection_model_path
    global emotion_model_path
    global emotion_labels
    global frame_window
    global emotion_window
    global best_prob


    def __init__(self):
        self.video = cv2.VideoCapture(0)
        self.cascade = cv2.CascadeClassifier(detection_model_path)

        # 추가코드
        self.emotion_classifier = load_model(emotion_model_path, compile=False)
        # getting input model shapes for inference
        self.emotion_target_size = self.emotion_classifier.input_shape[1:3]  # emotion_target_size = (48,48)
        self.smile_count = 0
        self.save_file_count = 0
        self.smile_data = {}    #{count:percent}

        '''
        self.image_size = ''
        self.embeddings = []
        
        
        '''

    def __del__(self):
        self.video.release()

    def get_frame(self):
        success, frame = self.video.read()
        success, jpeg = cv2.imencode('.jpg', frame)
        return jpeg.tobytes()

    def get_frame(self):
        success, frame = self.video.read()
        self.gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        self.rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)  # 추가코드0924

        # 추카코드0924
        self.faces = self.cascade.detectMultiScale(self.gray, scaleFactor=1.1, minNeighbors=5)
        # face = sorted(faces, reverse=True, key=lambda x:(x[2] - x[0]) * (x[3] - x[1]))[0]
        for (fX, fY, fW, fH) in self.faces:

            gray_face = self.gray[fY:fY + fH, fX:fX + fW]
            # color_face = self.rgb[fY:fY + fH, fX:fX + fW]
            gray_face = cv2.resize(gray_face, (48, 48))
            gray_face = gray_face.astype("float") / 255.0
            gray_face = img_to_array(gray_face)
            gray_face = np.expand_dims(gray_face, axis=0)  # (48,48,1)

            emotion_prediction = self.emotion_classifier.predict(gray_face)[0]
            emotion_probability = np.max(emotion_prediction)
            emotion_label = np.argmax(emotion_prediction)
            emotion_text = emotion_labels[emotion_label]  # happy, sad, surprise
            emotion_window.append(emotion_text)

            #if len(emotion_window) > frame_window:      #frame_window = 30
                #emotion_window.pop(0)
                #emotion_window.clear()

            #try:
                #emotion_mode = mode(emotion_window)

            #except:
                #continue

            if emotion_text == 'happy':
                color = emotion_probability * np.asarray((255,0,0))

            elif emotion_text == 'angry':
                color = emotion_probability * np.asarray((0, 0, 255))

            elif emotion_text == 'sad':
                color = emotion_probability * np.asarray((255, 255, 0))

            elif emotion_text == 'neutral':
                color = emotion_probability * np.asarray((0, 255, 255))

            else:
                color = emotion_probability * np.asarray((0, 255, 0))

            color = color.astype(int)
            color = color.tolist()



            if emotion_text =='happy':

                if self.smile_count <= 20: #30
                    self.smile_count +=1
                    image = cv2.rectangle(frame, (fX, fY), (fX + fW, fY + fH), (0,255,100), 2)
                    cv2.putText(image, (str(self.smile_count)+": "+str(emotion_probability)) ,(fX, fY),cv2.FONT_HERSHEY_SIMPLEX, 2, (0,255,100), 4)

                    success, jpeg = cv2.imencode('.jpg', frame)
                    jpeg_tobytes =jpeg.tobytes()

                    #smile percent
                    emotion_probability
                    self.smile_data[self.smile_count] = [emotion_probability,jpeg_tobytes]     #dictionary


                    return jpeg_tobytes

                elif self.smile_count > 20:






                    prob_list =[]
                    for keys, values in self.smile_data.items():
                        prob_list.append(values)

                    best_prob.append(max(prob_list))


                    #byte인 상태


                    image = cv2.rectangle(frame, (fX, fY), (fX + fW, fY + fH), (0, 255, 100), 2)
                    cv2.putText(image, ("smile_count" + str(self.smile_count)), (fX, fY), cv2.FONT_HERSHEY_SIMPLEX, 2,(0, 255, 100), 4)


                    success, jpeg = cv2.imencode('.jpg', frame)

                    #img write
                    if len(best_prob) !=0:


                        data = best_prob[0][1]  # binary형태의 데이터타입: b'\...\...\...
                        data = np.frombuffer(data, dtype=np.uint8)  # numpy.uint8변환
                        img = cv2.imdecode(data, cv2.IMREAD_COLOR)  # color이미지로 불러오기
                        #cv2.imshow('img_decode', img)
                        cv2.imwrite(str(self.save_file_count)+'.jpg', img)


                        self.save_file_count+=1
                        best_prob.clear()








                    return jpeg.tobytes()











                    #cv2.destroyAllWindows()

            else:
                self.smile_count = 0







        success, jpeg = cv2.imencode('.jpg', frame)
        return jpeg.tobytes()



def video_smile(request):
    try:
        return StreamingHttpResponse(gen(VideoCamera_smile()), content_type="multipart/x-mixed-replace;boundary=frame")
    except HttpResponseServerError as e:
        print("asborted", e)


#_______________________________________________________________________
class VideoCamera_none:
    global detection_model_path
    global emotion_model_path
    global emotion_labels
    global frame_window
    global emotion_window
    global best_prob

    def __init__(self):
        self.video = cv2.VideoCapture(0)
        self.cascade = cv2.CascadeClassifier(detection_model_path)

        # 추가코드
        self.emotion_classifier = load_model(emotion_model_path, compile=False)
        # getting input model shapes for inference
        self.emotion_target_size = self.emotion_classifier.input_shape[1:3]  # emotion_target_size = (48,48)
        self.smile_count = 0
        self.emotion_count = 0
        self.smile_data = {}  # {count:percent}

        '''
        self.image_size = ''
        self.embeddings = []


        '''

    def __del__(self):
        self.video.release()



    def get_frame(self):
        success, frame = self.video.read()
        success, jpeg = cv2.imencode('.jpg', frame)
        return jpeg.tobytes()

    def get_frame(self):
        success, frame = self.video.read()
        self.gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        self.rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)  # 추가코드0924

        # 추카코드0924
        self.faces = self.cascade.detectMultiScale(self.gray, scaleFactor=1.1, minNeighbors=5)
        # face = sorted(faces, reverse=True, key=lambda x:(x[2] - x[0]) * (x[3] - x[1]))[0]
        for (fX, fY, fW, fH) in self.faces:

            gray_face = self.gray[fY:fY + fH, fX:fX + fW]
            # color_face = self.rgb[fY:fY + fH, fX:fX + fW]
            gray_face = cv2.resize(gray_face, (48, 48))
            gray_face = gray_face.astype("float") / 255.0
            gray_face = img_to_array(gray_face)
            gray_face = np.expand_dims(gray_face, axis=0)  # (48,48,1)

            emotion_prediction = self.emotion_classifier.predict(gray_face)[0]
            emotion_probability = np.max(emotion_prediction)
            emotion_label = np.argmax(emotion_prediction)
            emotion_text = emotion_labels[emotion_label]  # happy, sad, surprise
            emotion_window.append(emotion_text)

            # if len(emotion_window) > frame_window:      #frame_window = 30
            # emotion_window.pop(0)
            # emotion_window.clear()

            # try:
            # emotion_mode = mode(emotion_window)

            # except:
            # continue

            if emotion_text == 'happy':
                color = emotion_probability * np.asarray((255, 0, 0))

            elif emotion_text == 'angry':
                color = emotion_probability * np.asarray((0, 0, 255))

            elif emotion_text == 'sad':
                color = emotion_probability * np.asarray((255, 255, 0))

            elif emotion_text == 'neutral':
                color = emotion_probability * np.asarray((0, 255, 255))

            else:
                color = emotion_probability * np.asarray((0, 255, 0))

            color = color.astype(int)
            color = color.tolist()

            if emotion_text != 'happy':

                if self.smile_count <= 15:  # 30
                    self.smile_count += 1
                    image = cv2.rectangle(frame, (fX, fY), (fX + fW, fY + fH), (0, 255, 100), 2)
                    cv2.putText(image, (str(self.smile_count) + ": " + str(emotion_probability)), (fX, fY),
                                cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 255, 100), 4)

                    success, jpeg = cv2.imencode('.jpg', frame)
                    jpeg_tobytes = jpeg.tobytes()

                    # smile percent
                    #emotion_probability
                    #self.smile_data[self.smile_count] = [emotion_probability, jpeg_tobytes]  # dictionary

                    return jpeg_tobytes

                else:
                    '''
                    prob_list = []
                    for keys, values in self.smile_data.items():
                        prob_list.append(values)

                    #best_prob.append(max(prob_list))
                    '''

                    # byte인 상태

                    image = cv2.rectangle(frame, (fX, fY), (fX + fW, fY + fH), (0, 255, 100), 2)
                    cv2.putText(image, "count"+":"+str(self.smile_count), (fX, fY), cv2.FONT_HERSHEY_SIMPLEX, 2,
                                (0, 255, 100), 4)

                    success, jpeg = cv2.imencode('.jpg', frame)

                    return jpeg.tobytes()

                    # cv2.destroyAllWindows()

        success, jpeg = cv2.imencode('.jpg', frame)
        return jpeg.tobytes()


def video_none(request):
    try:
        return StreamingHttpResponse(gen(VideoCamera_none()), content_type="multipart/x-mixed-replace;boundary=frame")
    except HttpResponseServerError as e:
        print("asborted", e)


def gen(camera):
    while True:
        frame = camera.get_frame()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')


def imgwrite():
    if len(best_prob)!=0:
        data = best_prob[1]  # binary형태의 데이터타입: b'\...\...\...
        data = np.frombuffer(data, dtype=np.uint8)
        img = cv2.imdecode(data,cv2.IMREAD_COLOR)
        cv2.imshow('img_decode',img)
        cv2.imwrite('C:/dev/finalProject/aiProject/01.png',img)

    else:
        pass







'''
# 첫번째 시도한 코드 아래 참조
import cv2,os
from django.shortcuts import render,redirect,get_object_or_404
from django.http import HttpResponse, StreamingHttpResponse, HttpResponseServerError
from django.contrib.auth import get_user_model, authenticate
import base64, re, json, time
#import matplotlib.pyplot as plt
from io import BytesIO
import tensorflow as tf
import numpy as np
from tensorflow.keras.preprocessing.image import img_to_array
from statistics import mode
#from skimage.transform import resize
from scipy.spatial import distance
from tensorflow.keras.models import load_model
def home(request):
    render(request, 'smile/index.html')
# model path
detection_model_path = 'detection_models/haarcascade_frontalface_default.xml'
emotion_model_path = 'C:/dev/finalProject/project/smile/emotion_models/_vgg16_01_.34-0.77-0.6478.h5'
print(os.path.exists(emotion_model_path))
#loading models
face_detection = cv2.CascadeClassifier(detection_model_path)
emotion_classifier = load_model(emotion_model_path, compile=False)
print("load_model")
emotion_labels =["happy","angry","sad","neutral","surprise"]
# getting input model shapes for inference
emotion_target_size = emotion_classifier.input_shape[1:3]   #emotion_target_size = (48,48)
image_size =''
embeddings =[]
emotion_count = 0
emotion_data ={}
# initialization
#graph = tf.get_default_graph() --- 오류미해결 생략
camera = 0
cameraChange=False
video_capture = cv2.VideoCapture(camera)
#User = get_user_model()  ---오류미해결 _user관련한 DB??!
# stream video actively
def video(request):
    if request.method =='GET':
        return StreamingHttpResponse(gen(), content_type="multipart/x-mixed-replace; boundary=frame") #내용물형식
    else:
        pass
    return render(request,'smile/index.html')
# face recognition and expression recognition
def processImg(object):
    frame_window = 10
    #emotion_offsets = (20, 40)     #tuple의문제인가..
    global face_detection
    global emotion_classifier
    global emotion_labels
    emotion_window =[]
    gray = cv2.cvtColor(object,cv2.COLOR_RGB2GRAY)
    rgb = cv2.cvtColor(object, cv2.COLOR_BGR2RGB)
    faces = face_detection.detectMultiScale(gray,scaleFactor=1.1,minNeighbors=5)
    face = sorted(faces, reverse=True, key=lambda x:(x[2] - x[0]) * (x[3] - x[1]))[0]
    (fX, fY, fW, fH) = face
    gray_face = gray[fY:fY + fH, fX:fX + fW]
    color_face = rgb[fY:fY + fH, fX:fX + fW]
    gray_face = cv2.resize(gray_face,(48,48))   #(48,48)로 조정
    gray_face = gray_face.astype("float") /255.0    #정규화진행
    gray_face = gray_face = img_to_array(gray_face)
    gray_face = np.expand_dims(gray_face, axis=0)

    emotion_prediction = emotion_classifier.predict(gray_face)[0]
    emotion_probablity = np.max(emotion_prediction)
    emotion_label = np.argmax(emotion_prediction)
    emotion_text = emotion_labels[emotion_label]       #happy, sad, surprise...
    emotion_window.append(emotion_text)
    if len(emotion_window) > frame_window:   #감정이 10개이상 측정되면 frame_window =10
        emotion_window.pop(0)
    emotion_mode = mode(emotion_window) #감정이 가장 많이 나온 최빈값을 도출
    if emotion_text =='happy':
        color = emotion_probablity * np.asarray((255, 0, 0))
    else:
        color = emotion_probablity * np.asarray((0, 255, 0))
    color = color.astype(int)
    color = color.tolist()
    cv2.rectangle(rgb,color,(fX, fY),(fX + fW, fY + fH),color)
    cv2.putText(rgb,emotion_mode,(fX, fY),cv2.FONT_HERSHEY_SIMPLEX,2,color,2)
    bgr_image = cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR)
    return bgr_image
def gen():  #generateVideo
    global video_capture
    global cameraChange
    while True:
        #time.sleep(0.1)
        frame =video_capture.read()[1]
        try:
            frame = bytes(cv2.imencode('.jpeg',processImg(frame))[1]) # byte단위로 이미지를 읽어와서 jpg로 변환해주는 코드
        except:
            continue
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')
'''