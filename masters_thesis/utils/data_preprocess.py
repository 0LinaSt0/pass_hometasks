import cv2
import numpy as np

from typing import Tuple

from consts import PREPROCESS_PARAMS
    

class SKUPreprocessor:
    @staticmethod
    def resize_img_with_scale(img: np.ndarray, scale: float | None=None) -> np.ndarray:
        h: int
        w: int
        img_resized: np.ndarray
        
        h, w = img.shape[:2]
        
        if scale is None:
            scale = min(
                PREPROCESS_PARAMS.RESIZE / w, 
                PREPROCESS_PARAMS.RESIZE / h, 
                1.0
            )
        
        img_resized = cv2.resize(
            img,
            (int(w * scale), int(h * scale)),
            interpolation=cv2.INTER_AREA
        )

        return img_resized

    @staticmethod
    def eda(img: np.ndarray) -> Tuple[bool, dict]:
        '''
        {
            'issues': ['blurry', 'bad_wb', 'bad_geometry'],
            'metrics': {
                'laplacian': <float>,
                'white_balance_a_std': <float>,
                'white_balance_b_std': <float>,
                'proportion_diff': <float>,
            },
            'shape': (height, weight)
        }
        '''
        result: dict 
        img_gray: np.ndarray
        laplacian: cv2.typing.MatLike
        balance_a: cv2.typing.MatLike
        balance_b: cv2.typing.MatLike
        proportion_diff: float
        is_good: bool = True

        
        result = {
            'issues': [],
            'metrics': {
                'laplacian': 0.0,
                'white_balance_a_std': 0.0,
                'white_balance_b_std': 0.0,
                'proportion_diff': 0.0
            },
            'shape': (0, 0)
        }

        img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        result['shape'] = img.shape[:2] 

        # Detect metrics
        laplacian = cv2.Laplacian(img_gray, cv2.CV_64F)
        _, balance_a, balance_b = cv2.split(cv2.cvtColor(img, cv2.COLOR_BGR2LAB))
        proportion_diff = abs(
            (result['shape'][0]/result['shape'][1]) 
            - PREPROCESS_PARAMS.ASPECT_TARGET
        ) / PREPROCESS_PARAMS.ASPECT_TARGET

        result['metrics']['laplacian'] = laplacian.var()
        result['metrics']['white_balance_a_std'] = balance_a.std()
        result['metrics']['white_balance_b_std'] = balance_b.std()
        result['metrics']['proportion_diff'] = proportion_diff

        # Classify problems
        if result['metrics']['laplacian'] < PREPROCESS_PARAMS.EDA_THRESHOLDS.LAPLACIAN:
            is_good = False
            result['issues'].append('blurry')
        
        if result['metrics']['white_balance_a_std'] > PREPROCESS_PARAMS.EDA_THRESHOLDS.WHITE_BALANCE_A_STD \
            or result['metrics']['white_balance_b_std'] > PREPROCESS_PARAMS.EDA_THRESHOLDS.WHITE_BALANCE_B_STD:
            is_good = False
            result['issues'].append('bad_wb')
        
        if result['metrics']['proportion_diff'] > PREPROCESS_PARAMS.EDA_THRESHOLDS.ASPECT_RATIO:
            is_good = False
            result['issues'].append('bad_geometry')

        return is_good, result
    
    @staticmethod
    def fix_dirty(img: np.ndarray, eda_result: dict) -> np.ndarray:      
        # 1. Blurry
        if 'blurry' in eda_result['issues']:
            laplacian_deficit: float
            sharpen_strength: float
            kernel: np.ndarray

            laplacian_deficit = max(
                PREPROCESS_PARAMS.CORRECTION_POWER_RANGE.LAPLACIAN_DEFICIT[0], 
                PREPROCESS_PARAMS.EDA_THRESHOLDS.LAPLACIAN - eda_result['metrics']['laplacian']
            )
            sharpen_strength = min(
                laplacian_deficit / 100, 
                PREPROCESS_PARAMS.CORRECTION_POWER_RANGE.LAPLACIAN_DEFICIT[1]
            )
            kernel = np.array(
                [[-1,-1,-1], [-1,9,-1], [-1,-1,-1]], 
                dtype=np.float32
            )
            img = cv2.filter2D(img, -1, kernel * sharpen_strength)
    
        # 2. WB
        if 'bad_wb' in eda_result['issues']:
            wb_a_excess: float
            wb_b_excess: float
            wb_strength: float
            balancer: cv2.xphoto_WhiteBalancer

            wb_a_excess = max(
                PREPROCESS_PARAMS.CORRECTION_POWER_RANGE.WB_EXCESS[0], 
                eda_result['metrics']['white_balance_a_std'] - PREPROCESS_PARAMS.EDA_THRESHOLDS.WHITE_BALANCE_A_STD
            )
            wb_b_excess = max(
                PREPROCESS_PARAMS.CORRECTION_POWER_RANGE.WB_EXCESS[0], 
                eda_result['metrics']['white_balance_b_std'] - PREPROCESS_PARAMS.EDA_THRESHOLDS.WHITE_BALANCE_B_STD
            )
            wb_strength = min(
                (wb_a_excess + wb_b_excess) / (PREPROCESS_PARAMS.EDA_THRESHOLDS.WHITE_BALANCE_A_STD + PREPROCESS_PARAMS.EDA_THRESHOLDS.WHITE_BALANCE_B_STD), 
                PREPROCESS_PARAMS.CORRECTION_POWER_RANGE.WB_EXCESS[1]
            )

            if wb_strength > PREPROCESS_PARAMS.CORRECTION_POWER_RANGE.WB_EXCESS[0]:
                balancer = cv2.xphoto_WhiteBalancer_create()
                img = balancer.balancerWhite(img)
    
        # 3. Geometry
        if 'bad_geometry' in eda_result['issues']:
            h: int
            w: int
            aspect_current: float
            aspect_diff: float
            crop_ratio: float
            target_w: int
            start_x: float

            h, w = img.shape[:2]
            aspect_current = w / h
            aspect_diff = abs(aspect_current - PREPROCESS_PARAMS.ASPECT_TARGET) / PREPROCESS_PARAMS.ASPECT_TARGET

            if aspect_diff > 0.05: # if diff more 5%
                crop_ratio = min(
                    (1.0 - aspect_diff * 0.5), # multiply 0.5 for non-aggressive cropping
                    PREPROCESS_PARAMS.CORRECTION_POWER_RANGE.ASPECT_DIFF_MORE_5_CROP[1]
                )

                target_w = int(h * PREPROCESS_PARAMS.ASPECT_TARGET * crop_ratio)
                start_x = max(0, (w - target_w) // 2)
                img = img[:, start_x:(start_x + target_w)]

        # 4. Resize img with scale
        img = SKUPreprocessor.resize_img_with_scale(img)

        # 5. CLAHE
        clahe_clip: float
        clahe_title: int

        clahe_clip = min(
            PREPROCESS_PARAMS.CORRECTION_POWER_RANGE.CLAHE_CLIP_LIMIT[0] + (eda_result['metrics']['laplacian'] / 200),
            PREPROCESS_PARAMS.CORRECTION_POWER_RANGE.CLAHE_CLIP_LIMIT[1]
        )
        clahe_title = PREPROCESS_PARAMS.CORRECTION_POWER_RANGE.CLAHE_TITLE_AGGRESSIVE \
            if eda_result['metrics']['laplacian'] > 100 \
            else PREPROCESS_PARAMS.CORRECTION_POWER_RANGE.CLAHE_TITLE_PASSIVE

        clahe = cv2.createCLAHE(clipLimit=clahe_clip, tileGridSize=clahe_title)
        lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)
        lab[:, :, 0] = clahe.apply(lab[:, :, 0]) # Only L channel
        img = cv2.cvtColor(lab, cv2.COLOR_LAB2BGR)

        return img