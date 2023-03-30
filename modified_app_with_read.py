import face_recognition , cv2 ,  numpy as np , pyodbc , sqlite3

# connection_string = 'Driver={SQL Server};Server=DESKTOP-CIRT352;Database=Face_recogntion;Trusted_Connection=yes;'

# mydb = pyodbc.connect(connection_string)

mydb = sqlite3.connect("mydb.db")
cursor = mydb.cursor()
cursor.execute("SELECT id FROM images")
image_ids = cursor.fetchall()

known_face_encodings = []
for image_id in image_ids:
    cursor.execute("SELECT image FROM images WHERE id = ?",(image_id[0],))
    image_data = cursor.fetchone()
    np_image = np.frombuffer(image_data[0], np.uint8)
    image = cv2.imdecode(np_image, cv2.IMREAD_COLOR)
    face_encoding = face_recognition.face_encodings(np.array(image))[0]
    known_face_encodings.append(face_encoding)
    # image = Image.open(io.BytesIO(image_data))
    # image = face_recognition.load_image_file(image_data)
    # face_encoding = face_recognition.face_encodings(image)[0]
    # known_face_encodings.append(face_encoding)



face_locations = []
face_encodings = []
face_names = []
process_this_frame = True
video_capture = cv2.VideoCapture(0)

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

video_capture.release()
cv2.destroyAllWindows()




























# # Query the database for the image you want to use
# # query = "SELECT image_data FROM images WHERE image_id = %s"
# # image_id = 1 # replace with the ID of the image you want to use

# # cursor.execute(query, (image_id,))
# # row = cursor.fetchone()
# # image_data = row[0]
#
# # Convert the image data to a numpy array
# nparr = np.frombuffer(image_data, np.uint8)
# image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
#
# # Generate a face encoding for the image
# face_encoding = face_recognition.face_encodings(image)[0]
#
# # Create a list of known face encodings
# known_face_encodings = [
#     face_encoding
# ]
#
# # Initialize some variables
# face_locations = []
# face_encodings = []
# face_names = []
# process_this_frame = True
#
# # Initialize the video capture device
# video_capture = cv2.VideoCapture(0)
#
# # Define a Flask app
# from flask import Flask, jsonify, request
# app = Flask(__name__)
#
# # Define an API endpoint for facial recognition
# @app.route('/recognize', methods=['POST'])
# def recognize():
#     # Read the image from the request data
#     nparr = np.fromstring(request.data, np.uint8)
#     image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
#
#     # Generate a face encoding for the image
#     face_encoding = face_recognition.face_encodings(image)[0]
#
#     # Compare the face encoding to the known face encodings
#     matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
#     name = "Unknown"
#     if True in matches:
#         name = "Person 1"
#
#     # Return the name or ID of the person in the image
#     return jsonify({'name': name})
#
# if __name__ == '__main__':
#     app.run()
