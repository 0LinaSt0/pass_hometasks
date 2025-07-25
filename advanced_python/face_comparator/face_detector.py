from typing import List

import cv2
import numpy as np
import face_recognition
from scipy.spatial import distance

from utils.logging import LoggingMethods


class FaceCascadeWrapper:
    def __init__(self, cascade_path):
        self.cascade = cv2.CascadeClassifier(cascade_path)

    def detect_faces(self, gray_image):
        return self.cascade.detectMultiScale(gray_image, scaleFactor=1.1, minNeighbors=5)



class FaceDetection(LoggingMethods):
    ''' Class includes method for:
        - detection faces in the images with Haar Cascades;
        - extract features from faces by face_recognition encoding.
    '''

    # Load Haar Cascade for face detection
    FACE_CASCADE = FaceCascadeWrapper(
        cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
    )

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(FaceDetection, cls).__new__(cls)
        return cls._instance

    @classmethod
    def _detect_and_crop_face(cls, mtx_photo: np.ndarray) -> list:
        faces_pics = []

        gray_image = cv2.cvtColor(mtx_photo, cv2.COLOR_BGR2GRAY)

        faces = cls.FACE_CASCADE.detect_faces(
            gray_image
        )

        if len(faces) != 0:
            for (x, y, w, h) in faces:
                # Crop the face from the image and save to face_pics list
                face = mtx_photo[y:y+h, x:x+w]
                faces_pics.append(face)

        return faces_pics

    @classmethod
    def detect_and_crop_face_from_path(cls, image_path: str) -> list:
        image = cv2.imread(image_path)

        return cls._detect_and_crop_face(image)

    @classmethod
    def detect_and_crop_face(cls, image_mtx: np.ndarray) -> list:
        return cls._detect_and_crop_face(image_mtx)

    @classmethod
    def get_face_encodings(cls, face_mtxs: np.ndarray) -> List[np.ndarray]:
        encodings = []
        for pic in face_mtxs:
            image_rgb = cv2.cvtColor(pic, cv2.COLOR_BGR2RGB)
            encoding = face_recognition.face_encodings(image_rgb)

            if len(encoding) > 0:
                encodings.append(encoding[0])

        return encodings

    @classmethod
    def get_face_encoding_by_img_path(cls, image_path: str) -> List[np.ndarray]:
        face_mtxs = FaceDetection.detect_and_crop_face_from_path(image_path)

        encodings = FaceDetection.get_face_encodings(face_mtxs)

        return encodings


class FaceComparator(LoggingMethods):
    '''
    Class for comparing two faces. Methods for calculating
    the distance between two face encodings. A common metric is
    the Euclidean distance. If the distance is below a certain
    threshold, the faces are likely to be of the same person.
    '''

    THRESHOLD = 0.6

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(FaceComparator, cls).__new__(cls)
        return cls._instance

    @classmethod
    def faces_euclidean_distance(
        cls,
        encoding_face_mtx1: np.ndarray,
        encoding_face_mtx2: np.ndarray
    ):
        dist = distance.euclidean(
            encoding_face_mtx1,
            encoding_face_mtx2
        )

        is_same = True if dist < cls.THRESHOLD else False

        return dist, is_same
