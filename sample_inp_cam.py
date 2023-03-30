import cv2 , face_recognition , numpy as np , pyodbc , sqlite3

# Connect to the database
# connection_string = 'Driver={SQL Server};Server=DESKTOP-CIRT352;Database=Face_recogntion;Trusted_Connection=yes;'
# mydb = pyodbc.connect(connection_string)
mydb = sqlite3.connect("mydb.db")
cursor = mydb.cursor()
# cursor.execute(" CREATE TABLE images (id INTEGER PRIMARY KEY AUTOINCREMENT,name VARCHAR(50) NOT NULL, encoding BLOB, image BLOB ) ")
# print("Table Created ")
# mydb.commit()
# Open a video capture object for the camera
video_capture = cv2.VideoCapture(0)

# Display the video capture feed in a window
cv2.namedWindow("Camera Feed")
while True:
    # Capture a frame from the video feed
    ret, frame = video_capture.read()

    # Resize the frame for faster processing
    small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)

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

        # Insert the image data, filename, and ID into the database
        img_data = pyodbc.Binary(img_encoded)
        img_filename = input("Enter the name for the image file: ")
        if len(face_encodings) > 0:
            sql  = "INSERT INTO images (name, encoding, image) VALUES (?, ?, ?)"
            val  =  ( img_filename , face_encodings[0].tobytes() , img_data )
            cursor.execute(sql , val)
            mydb.commit()
        else:
            print("No face detected in the image.")

        # cursor.execute("INSERT INTO images (name, encoding, image) VALUES (?, ?, ?)", img_filename, face_encodings[0].tobytes(), img_data)
        # mydb.commit()

        # Break out of the loop and close the window
        break

# Release the camera and database connection
video_capture.release()
cursor.close()
mydb.close()
cv2.destroyAllWindows()
