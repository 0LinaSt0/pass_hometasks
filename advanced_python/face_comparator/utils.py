import numpy as np

from utils.logging import log_raises


@log_raises
def encoding_to_json(encodings: list[np.ndarray]):
    converted_encodings = []

    for encoding in encodings:
        converted_encodings.append(
            ';'.join(map(str, encoding))
        )
    return converted_encodings


@log_raises
def encoding_from_json(encoded_string: str) -> np.ndarray:
    float_list = np.array([
        float(num) for num in encoded_string.split(';')
    ])
    
    return float_list