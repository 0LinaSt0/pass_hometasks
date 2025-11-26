import numpy as np

def encoding_to_json(encodings: list[np.ndarray]):
    converted_encodings = []

    for encoding in encodings:
        converted_encodings.append(
            ';'.join(map(str, encoding))
        )
    return converted_encodings


def encoding_from_json(encoded_string: str) -> np.ndarray:
    float_list = np.array([
        float(num) for num in encoded_string.split(';')
    ])
    
    return float_list