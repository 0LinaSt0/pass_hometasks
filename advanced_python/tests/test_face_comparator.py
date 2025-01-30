import numpy as np
import pytest
from unittest.mock import patch
from face_comparator.face_detector import FaceDetection


import numpy as np
import pytest
from unittest.mock import patch
from face_comparator.face_detector import FaceDetection, FaceComparator
from face_comparator.utils import encoding_to_json, encoding_from_json


class TestFaceDetection:
    @pytest.fixture
    def mtx_photo(self):
        # Create a dummy image (100x100 pixels)
        return np.zeros((100, 100, 3), dtype=np.uint8)

    @pytest.fixture
    def face_mtxs(self):
        # Mocked face detection results (two detected faces)
        return [(10, 10, 50, 50), (20, 20, 50, 50)]

    @pytest.fixture
    def face_detection(self):
        return FaceDetection()

    @pytest.fixture
    def detected_faces(self, face_detection, mtx_photo, face_mtxs):
        with patch.object(FaceDetection.FACE_CASCADE, 'detect_faces') as mock_detect:
            # Mocking detect_faces to return predefined face coordinates
            mock_detect.return_value = face_mtxs

            # Call the method under test
            result = face_detection._detect_and_crop_face(mtx_photo)

        return result

    def test_detect_and_crop_face_with_face(self, detected_faces):
        # Assert that two faces were detected and cropped correctly
        assert len(detected_faces) == 2  
        # Check dimensions of first cropped face
        assert detected_faces[0].shape == (50, 50, 3)

    @patch.object(FaceDetection.FACE_CASCADE, 'detect_faces')
    def test_detect_and_crop_face_no_faces(self, mock_detect, face_detection, mtx_photo):
        # Mocking detect_faces to return no faces
        mock_detect.return_value = []

        result = face_detection._detect_and_crop_face(mtx_photo)

        # Assert that no faces were found
        assert len(result) == 0


class TestFaceComparator:
    @pytest.fixture
    def face_comparator(self):
        return FaceComparator()
    
    @patch('scipy.spatial.distance.euclidean')
    def test_faces_euclidean_distance_more(
        self, mock_euclidean, face_comparator
    ):
        mock_euclidean.return_value = 0.7

        dist, is_same = face_comparator.faces_euclidean_distance(
            np.array([]), np.array([])
        )

        assert dist == 0.7
        # Since 0.5 < THRESHOLD (0.6), is_same should be True
        assert is_same is False
    
    @patch('scipy.spatial.distance.euclidean')
    def test_faces_euclidean_distance_less(
        self, mock_euclidean, face_comparator
    ):
        mock_euclidean.return_value = 0.5 

        dist, is_same = face_comparator.faces_euclidean_distance(
            np.array([]), np.array([])
        )

        assert dist == 0.5
        # Since 0.5 < THRESHOLD (0.6), is_same should be True
        assert is_same is True


class TestEncoders:
    @pytest.fixture
    def encoded_arr(self):
        return np.zeros((5, 5), dtype=np.uint8)
    
    @pytest.fixture
    def encoded_list(self):
        return [
            '0;0;0;0;0',
            '0;0;0;0;0',
            '0;0;0;0;0',
            '0;0;0;0;0',
            '0;0;0;0;0'
        ]
    
    def test_encoding_to_json(
        sefl, encoded_arr, encoded_list
    ):
        result = encoding_to_json(encoded_arr)

        assert len(result) == encoded_arr.shape[0]
        assert result == encoded_list


    def test_encoding_from_json(
        self, encoded_arr, encoded_list
    ):
        result = encoding_from_json(';'.join(encoded_list))

        assert result.shape == encoded_arr.flatten().shape
        assert np.array_equal(result, encoded_arr.flatten())



