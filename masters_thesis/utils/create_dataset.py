import random
import shutil

import cv2
import pandas as pd
import numpy as np
from PIL import Image
import imagehash

import albumentations as A

from consts import AUG_PREPROCESS, PREPROCESS_PARAMS
from utils.data_preprocess import SKUPreprocessor

class SKUDatasetCreator:
    def __init__(self):   
        # Paths as class vars or external params
        self.images_path = None
        self.label_path = None
        self.target_images_path = None
        self.target_label_path = None

    def _save_img(self, img_name: str, img: np.ndarray):

        if img.dtype != np.uint8:
            img = img.astype(np.uint8)
        
        if len(img.shape) != 3 or img.shape[2] != 3:
            img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)

        img_dist = self.target_images_path / img_name
        cv2.imwrite(
            str(img_dist), img, [cv2.IMWRITE_JPEG_QUALITY, 95]
        )

    def _save_new_yolo_label_from_albumentations(
        self, img_name: str, bboxes_aug: list, 
        classes_aug: list, w_final: int, h_final: int
    ):
        '''
        Albumentations PascalVOC → YOLO format

        bboxes_aug: [[x_min, y_min, x_max, y_max], ...]  # PascalVOC pixels
        '''
        label_dist = (self.target_label_path / img_name).with_suffix('.txt')

        with open(label_dist, 'w') as f:
            for bbox, cls_id in zip(bboxes_aug, classes_aug):
                x_min, y_min, x_max, y_max = bbox

                x_center = (x_min + x_max) / 2
                y_center = (y_min + y_max) / 2

                bbox_width = x_max - x_min
                bbox_height = y_max - y_min

                # YOLO normalization
                x_center_norm = x_center / w_final
                y_center_norm = y_center / h_final
                width_norm = bbox_width / w_final
                height_norm = bbox_height / h_final

                f.write(
                    f'{int(cls_id)} {x_center_norm:.6f} {y_center_norm:.6f} '
                    f'{width_norm:.6f} {height_norm:.6f}\n'
                )

    def _save_img_and_label(
        self, img_name: str, img_dataset: str, img: np.ndarray
    ):
        # Save img
        self._save_img(img_name, img)

        # Save label
        label_str = (self.label_path / img_dataset / img_name).with_suffix('.txt')
        label_dist = (self.target_label_path / img_name).with_suffix('.txt')
        shutil.copy2(label_str, label_dist)

    def broken_eda(self, img_info: tuple) -> dict:
        '''
        {
            'img_info': img_info,
            'status': 'selected' / 'corrupted' 
                        / 'bad_size' / 'low_res'
        }
        '''
        result = {
            'img_info': img_info, 'status': 'selected'
        }

        img_path = self.images_path / img_info[0] / img_info[1]
        
        # Check corrupted
        try:
            with Image.open(img_path) as img:
                img.verify()

            img_cv = cv2.imread(str(img_path))
            if img_cv is None: raise

        except:
            result['status'] = 'corrupted'
            return result

        # Check size
        file_size_kb = img_path.stat().st_size / 1024
        if not (PREPROCESS_PARAMS.EDA_THRESHOLDS.SIZE_RANGE[0] 
            <= file_size_kb 
            <= PREPROCESS_PARAMS.EDA_THRESHOLDS.SIZE_RANGE[1]
        ):
            result['status'] = 'bad_size'
            return result
            
        # Check resolution
        h, w = img_cv.shape[:2]
        if w < PREPROCESS_PARAMS.EDA_THRESHOLDS.IMG_SHAPE[0] \
            or h < PREPROCESS_PARAMS.EDA_THRESHOLDS.IMG_SHAPE[1]:
            result['status'] = 'low_res'
            return result

        return result

    def quality_eda(self, img_info: tuple) -> dict:
        '''
        {
            'img_dataset': img_info[0],
            'img_name': img_info[1],
            'is_good': True / False,
            'issues': ['blurry', 'bad_wb', 'bad_geometry'],
            'phash': <P-Hash of img for check duplicates>,
            'metrics': {
                'laplacian': <float>,
                'white_balance_a_std': <float>,
                'white_balance_b_std': <float>,
                'proportion_diff': <float>,
            },
            'shape': (height, weight)
        }
        '''
        result = {
            'img_dataset': img_info[0], 
            'img_name': img_info[1],
            'is_good': True,
            'issues': [],
            'phash': 0.0,
            'metrics': {
                'laplacian': 0.0,
                'white_balance_a_std': 0.0,
                'white_balance_b_std': 0.0,
                'proportion_diff': 0.0
            },
            'shape': (0, 0)
        }

        img_path = self.images_path / img_info[0] / img_info[1]
        
        img = cv2.imread(str(img_path))
        
        is_good, eda_result = SKUPreprocessor.eda(img)
        
        result['is_good'] = is_good
        result.update(eda_result)

        # P-Hash calculating for duplicates
        # phash = cv2.img_hash.PHash_create().compute(img_gray)
        # result['phash'] = hashlib.md5(phash.tobytes()).hexdigest()

        with Image.open(img_path) as pil_img:
            result['phash'] = str(imagehash.phash(pil_img))

        return result
        
    def process_and_save_dirty_raw(self, img_data: pd.Series) -> dict:
        '''
        {
            'img_dataset': img_data['img_dataset'],
            'img_name': img_data['img_name'],
            'status': 'dirty_fixed',
            'final_shape': <tuple of img shape>,
            'issues': img_data['issues']
        }
        '''
        result = {
            'img_dataset': img_data['img_dataset'],
            'img_name': img_data['img_name'],
            'status': 'dirty_fixed',
            'final_shape': (0, 0),
            'issues': img_data['issues']
        }
        
        img_path = self.images_path / img_data['img_dataset'] / img_data['img_name']
        
        img = cv2.imread(str(img_path))

        img = SKUPreprocessor.fix_dirty(img)

        result['final_shape'] = img.shape[:2]

        # 6 Save img and it's label
        self._save_img_and_label(
            img_data['img_name'], 
            img_data['img_dataset'],
            img
        )

        return result

    def process_and_save_aug_raw(self, img_data: pd.Series) -> dict:
        '''
        {
            'img_dataset': img_data['img_dataset'],
            'img_name': img_data['img_name'],
            'status': 'augmented',
            'final_shape': <tuple of img shape>,
            # 'aug_set': <set of random choosed aurgemntations>
        }
        '''
        result = {
            'img_dataset': img_data['img_dataset'],
            'img_name': img_data['img_name'],
            'status': 'augmented',
            'final_shape': (0, 0),
            # 'aug_set': []
        }

        img_path = self.images_path / img_data['img_dataset'] / img_data['img_name']
        label_path = (self.label_path / img_data['img_dataset'] / img_data['img_name']).with_suffix('.txt')

        img = cv2.imread(str(img_path))
        h, w = img.shape[:2]

        with open(str(label_path)) as f:
            lines = f.readlines()
            
        # 1. YOLO format (class, x_center, y_center, width, height) ->
        #     -> Albumentations format (x_min, y_min, x_max, y_max)
        bboxes = []
        classes = []
        for line in lines:
            cls, xc, yc, bw, bh = map(float, line.strip().split())

            x_min = max(0.0, (xc - bw/2) * w)
            y_min = max(0.0, (yc - bh/2) * h)
            x_max = min(w, (xc + bw/2) * w)
            y_max = min(h, (yc + bh/2) * h)
            bboxes.append([x_min, y_min, x_max, y_max])
            classes.append(int(cls))
            
        # 2. Choice random augs
        lighting_aug = A.ColorJitter(**AUG_PREPROCESS.LIGHT_AUG)
        perspective_aug = random.choice([
            A.Rotate(**AUG_PREPROCESS.PERSPECTIVE_AUG.ROTATE, p=1.0),                              
            A.ShiftScaleRotate(**AUG_PREPROCESS.PERSPECTIVE_AUG.SHIFT_SCALE_ROTATE, p=1.0), 
            A.RandomScale(**AUG_PREPROCESS.PERSPECTIVE_AUG.RANDOM_SCALE, p=1.0), 
            A.OpticalDistortion(**AUG_PREPROCESS.PERSPECTIVE_AUG.OPTICAL_DISTORTION, p=1.0),  
            A.Perspective(**AUG_PREPROCESS.PERSPECTIVE_AUG.PERSPECTIVE, p=1.0)  
        ])
        
        # 3. Augmentations imgs and labels
        transform = A.Compose(
            [lighting_aug, perspective_aug],
            bbox_params=A.BboxParams(
                format='pascal_voc',
                label_fields=['class_labels'],
                min_visibility=0.3,    # ≥30% площади bbox сохранилось
                min_area=0.001         # ≥0.1% площади изображения
            )
        )

        transformed = transform(image=img, bboxes=bboxes, class_labels=classes)
        img_aug = transformed['image']
        bboxes_aug = transformed['bboxes']
        classes_aug = transformed['class_labels']
        # set_aug = transformed['applied_transforms']

        # 4. Resize img and label with scale
        h_aug, w_aug = img_aug.shape[:2]
        scale = min(self.resize / w_aug, self.resize / h_aug, 1.0)
        
        img_aug = SKUPreprocessor.resize_img_with_scale(img_aug, scale)
        result['final_shape'] = img_aug.shape[:2]

        bboxes_resized = []
        for bbox in bboxes_aug:
            x_min, y_min, x_max, y_max = bbox
            bboxes_resized.append([
                x_min * scale, y_min * scale, 
                x_max * scale, y_max * scale
            ])
        
        # 5. Save img and it's label
        self._save_img(
            img_data['img_name'],
            img_aug
        )

        self._save_new_yolo_label_from_albumentations(
            img_data['img_name'], bboxes_resized, classes_aug, 
            w_final=result['final_shape'][1], h_final=result['final_shape'][0]
        )
        # result['aug_set'] = set_aug

        return result

    def process_and_save_good_raw(self, img_data: pd.Series) -> dict:
        '''
        {
            'img_dataset': img_data['img_dataset'],
            'img_name': img_data['img_name'],
            'status': 'good',
            'final_shape': <tuple of img shape>
        }
        '''
        result = {
            'img_dataset': img_data['img_dataset'],
            'img_name': img_data['img_name'],
            'status': 'good',
            'final_shape': (0, 0)
        }

        img_path = self.images_path / img_data['img_dataset'] / img_data['img_name']

        img = cv2.imread(str(img_path))

        # Resize img with scale
        img_resized = SKUPreprocessor.resize_img_with_scale(img)
        result['final_shape'] = img_resized.shape[:2]

        # Save img and it's label
        self._save_img_and_label(
            img_data['img_name'], 
            img_data['img_dataset'],
            img_resized
        )

        return result