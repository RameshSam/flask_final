from flask import Flask, request
import cv2 , face_recognition , numpy as np , pyodbc , sqlite3

# website url

#POST http://localhost:5000/camfaces?image_name=my_image.jpg
#POST http://localhost:5000/face

app = Flask(__name__)

# Connect to the database

mydb = sqlite3.connect("mydb.db",check_same_thread=False)
cursor = mydb.cursor()
cursor.execute(" CREATE TABLE images (id INTEGER PRIMARY KEY AUTOINCREMENT,name VARCHAR(50) NOT NULL, encoding BLOB, image BLOB ) ")
print("Table Created ")


# Create the endpoint for the POST request
@app.route('/camfaces', methods=['GET','POST'])
def faces_read():
    try:
        #image name from parameter
        img_filename = request.args.get('image_name',type=str)

        # Open a video capture object for the camera
        video_capture = cv2.VideoCapture(0)

        # Display the video capture feed in a window
        cv2.namedWindow("Camera Feed")
        while True:
            # Capture a frame from the video feed
            ret, frame = video_capture.read()

            # Resize the frame for faster processing
            small_frame = cv2.resize(frame, (640,480), fx=0.25, fy=0.25)

            # Display the frame in the window
            cv2.imshow('Camera Feed', small_frame)

            # Check if the user has clicked on the window
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
            elif cv2.waitKey(1) & 0xFF == ord('c'):
                # User has clicked on the window, so capture the current frame
                rgb_small_frame = small_frame[:, :, ::-1]  # Convert from BGR to RGB

                # Encode the image to JPEG format
                _, img_encoded = cv2.imencode('.jpg', rgb_small_frame)

                # Detect faces in the image
                face_locations = face_recognition.face_locations(rgb_small_frame)
                face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)
                print(img_filename)
                # Insert the image data, filename, and ID into the database
                img_data = pyodbc.Binary(img_encoded)
                #img_filename = request.form.get('image_name')
                if (img_filename is not None) and (len(face_encodings) > 0):
                    val  =  face_encodings[0].tobytes()
                    cursor.execute("INSERT INTO images (name, encoding, image) VALUES (?, ?, ?);", ( img_filename , val , img_data ))
                else:
                    print("Image name is none or No face detected in the image.")

                # Break out of the loop and close the window
                # scmd = """ SELECT * FROM images ;"""
                # cursor.execute(scmd)
                # result = cursor.fetchmany()
                # for i in result:
                #     print(i)
                # print(" Table Showed ")
                # mydb.commit()

                break
    except:
        mydb.rollback()
    finally:
    # Release the camera and database connection
        video_capture.release()
        cv2.destroyAllWindows()
        cursor.close()
        mydb.close()


        return 'Image Uploaded Successfully!'
    

@app.route('/face', methods=['GET'])
def recognize_faces():
    face_locations = []
    face_encodings = []
    face_names = []
    known_face_encodings = []
    process_this_frame = True

    cursor.execute("SELECT id FROM images") 
    image_ids = cursor.fetchall()

    for image_id in image_ids:
        cursor.execute("SELECT image FROM images WHERE id = ?",(image_id[0],))
        image_data = cursor.fetchone()
        np_image = np.frombuffer(image_data[0], np.uint8)
        image = cv2.imdecode(np_image, cv2.IMREAD_COLOR)
        face_encoding = face_recognition.face_encodings(np.array(image))[0]
        known_face_encodings.append(face_encoding)
    # Capture a single frame of video
    video_capture = cv2.VideoCapture(0)
    # ret, frame = video_capture.read()
    # video_capture.release()
    while True:
        # Capture a single frame of video
        ret, frame = video_capture.read()

        # Resize frame of video to 1/4 size for faster face recognition processing
        small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)

        # Convert the image from BGR color (which OpenCV uses) to RGB color (which face_recognition uses)
        rgb_small_frame = small_frame[:, :, ::-1]

        # Only process every other frame of video to save time
        if process_this_frame:
            # Find all the faces and face encodings in the current frame of video
            face_locations = face_recognition.face_locations(rgb_small_frame)
            face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)

            face_names = []
            for face_encoding in face_encodings:
                # See if the face is a match for any known face encoding
                matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
                name = "Unknown"

                # If a match was found in known_face_encodings, use the corresponding image ID as the name
                if True in matches:
                    first_match_index = matches.index(True)
                    name = str(image_ids[first_match_index][0])

                face_names.append(name)

        process_this_frame = not process_this_frame

        # Display the results
        for (top, right, bottom, left), name in zip(face_locations, face_names):
            # Scale back up face locations since the frame we detected in was scaled to 1/4 size
            top *= 4
            right *= 4
            bottom *= 4
            left *= 4

            # Draw a box around the face
            cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)

            # Draw a label with the image ID below the face
            cv2.rectangle(frame, (left, bottom - 35), (right, bottom), (0, 0, 255), cv2.FILLED)
            font = cv2.FONT_HERSHEY_DUPLEX
            cv2.putText(frame, name, (left + 6, bottom - 6), font, 1.0, (255, 255, 255), 1)

        # Display
        cv2.imshow('Video', frame)

        # Hit 'q' on the keyboard to quit!
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Return the recognized face names as a JSON response
    # response = jsonify({'face_names': face_names})
    # return response
    video_capture.release()
    cv2.destroyAllWindows()


if __name__ == '__main__':
    app.run()
