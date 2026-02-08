import inspect
from typing import Tuple
from pathlib import Path

YOLO_MODELPATH = 'data/yolo_model/best.pt'

DEFAULT_EXAMPLE_IMG = Path('data/examples/test_2042.jpg')
DEFAULT_EXAMPLE_LABEL = Path('data/examples/test_2042.txt')
DEFAULT_OUTPUT_DIR = Path('data/tmp_results/')

class Consts:
    @staticmethod
    def _parse(obj):
        if inspect.isclass(obj):
            return {
                k: Consts._parse(v) 
                for k, v in obj.__dict__.items() 
                if not k.startswith('__')
            }
        return obj

    @classmethod
    def to_dict(cls):
        return Consts._parse(cls)

class PREDICT_PARAMS(Consts):
    YOLO_THRESHOLD: float = 0.25
    IOU_THRESHOLD: float = 0.5


class PREPROCESS_PARAMS(Consts):
    ASPECT_TARGET: float = 4/3

    RESIZE: int = 1280

    class EDA_THRESHOLDS:
        SIZE_RANGE: Tuple[int] = (50, 50_000)   # pyright: ignore[reportUndefinedVariable] # 50КВ-50МВ
        IMG_SHAPE: Tuple[int] = (800, 600)      # type: ignore # ≥ 800×600
        LAPLACIAN: int = 120             # ≥ 120
        WHITE_BALANCE_A_STD: int = 30    # type: ignore # ≤ 30
        WHITE_BALANCE_B_STD: int = 30    # ≤ 30
        ASPECT_RATIO: float = 0.15         # 4/3 ≤ 15%

    
    class CORRECTION_POWER_RANGE:
        LAPLACIAN_DEFICIT: Tuple[float] = (0.0, 0.3)
        WB_EXCESS: Tuple[float] = (0.0, 1.0)
        ASPECT_DIFF_MORE_5_CROP: Tuple[float] = (0.9, 0.95)
        CLAHE_CLIP_LIMIT: Tuple[float] = (2.0, 3.0)
        CLAHE_TITLE_AGGRESSIVE: Tuple[int] = (8, 8)
        CLAHE_TITLE_PASSIVE: Tuple[int] = (4, 4)



class AUG_PREPROCESS(Consts):
    LIGHT_AUG = {
        'brightness': 0.2, 
        'contrast': 0.2, 
        'saturation': 0.3 ,
        'hue': 0.015
    }

    class PERSPECTIVE_AUG(Consts):
        ROTATE: dict = {
            'limit': 5
        } # shelf at an angle ±5°

        SHIFT_SCALE_ROTATE: dict = {
            'shift_limit': 0.1, 
            'scale_limit': 0, 
            'rotate_limit': 0
        } # shift ±10%

        RANDOM_SCALE: dict = {
            'scale_limit': 0.3
        } # scaling 0.7-1.3x

        OPTICAL_DISTORTION: dict = {
            'distort_limit': 0.015, 
            'shift_limit': 0
        } # shelf collapse ±1.5°

        PERSPECTIVE: dict = {
            'scale': (0.05, 0.1)
        } # perspective distortion


class KNN_THRESHOLDS(Consts):
    PADDING: int = 10       # Pixels to add around bbox for context
    
    class HDBSCAN_PARAMS:
        MIN_CLUSTER_SIZE: int = 5
        MIN_SAMPLES: int = 2    # Min points for HDBSCAN core point
    
    # class DBSCAN_PARAMS:
    #     METRIC: str = 'euclidean'
    #     DBSCAN_EPS: float = 0.2 # DBSCAN distance threshold for clustering similar embeddings
    #     MIN_SAMPLES: int = 2    # Min points for DBSCAN core point