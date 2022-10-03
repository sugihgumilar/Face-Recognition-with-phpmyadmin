import time

import cv2
import mysql.connector
from simple_facerec import SimpleFacerec


def connect_db(
    host: str,
    user: str,
    password: str,
    database: str,
):
    db = mysql.connector.connect(
        host=host, user=user, passwd=password, database=database
    )
    return db


def detect_face(encoding_image_path: str, db):
    sfr = SimpleFacerec()
    sfr.load_encoding_images(encoding_image_path)

    cap = cv2.VideoCapture(0)

    while True:
        ret, frame = cap.read()
        face_locations, face_names = sfr.detect_known_faces(frame)

        for face_loc, name in zip(face_locations, face_names):
            y1, x2, y2, x1 = face_loc[0], face_loc[1], face_loc[2], face_loc[3]
            cv2.putText(
                frame, name, (x1, y1 - 10), cv2.FONT_HERSHEY_COMPLEX, 1, (0, 0, 0), 2
            )
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 200), 2)

        cv2.imshow("Frame", frame)
        key = cv2.waitKey(1)
        if key == 27:
            break

        # //kirim ke mysql//
        if not check_already_exists(db, name, "timedetect", 6):
            cursor = db.cursor(buffered=True)
            sql = "INSERT INTO customers (name, timedetect) VALUES (%s, now())"
            val = (name, )
            cursor.execute(sql, val)
            db.commit()

    cap.release()
    cv2.destroyAllWindows()


def check_already_exists(
    db,
    name: str,
    column_check: str,
    window_hour: int,
) -> bool:

    cursor = db.cursor(buffered=True)
    cursor.execute(
        "SELECT * FROM customers WHERE ({} >= DATE_SUB(NOW(), INTERVAL {} HOUR)) AND name = %s".format(
            column_check, window_hour
        ),
        (name,),
    )
    result = cursor.fetchone()
    return result is not None


if __name__ == "__main__":
    conn = connect_db(host="localhost", user="root", password="", database="face_rec")
    detect_face("images/", conn)
