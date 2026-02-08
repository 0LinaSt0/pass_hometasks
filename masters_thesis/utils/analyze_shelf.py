import time
from typing import List, Tuple
from pathlib import Path
from tqdm import tqdm

import cv2
import numpy as np
import matplotlib
import matplotlib.pyplot as plt

import hdbscan
from sklearn.preprocessing import StandardScaler
from ultralytics import YOLO
from ultralytics.engine.results import Results as YoloEngineResults

from consts import YOLO_MODELPATH, PREDICT_PARAMS, KNN_THRESHOLDS
from utils.data_preprocess import SKUPreprocessor
from utils.clip_img2vec import Img2VecCLIP


class ShelfVisualizer:
    @staticmethod
    def draw_bboxes(
        img: np.ndarray, boxes: np.ndarray, 
        color: Tuple[int, int, int] = (0, 255, 0), 
        thickness: int = 2
    ) -> np.ndarray:
        img_vis: np.ndarray
        x1: int
        y1: int
        x2: int
        y2: int

        img_vis = img.copy()
        for box in boxes:
            x1, y1, x2, y2 = box.astype(int)
            cv2.rectangle(img_vis, (x1, y1), (x2, y2), color, thickness)
        return img_vis
    
    @staticmethod
    def show_comparison(
        img: np.ndarray, 
        pred_boxes: np.ndarray, 
        gt_boxes: np.ndarray | None, 
        metrics: dict,
        is_open_new_window: bool = True
    ):
        img_orig: np.ndarray
        img_pred: np.ndarray
        img_gt: np.ndarray
        img_pred_rgb: np.ndarray
        img_gt_rgb: np.ndarray

        if is_open_new_window:
            matplotlib.use('TkAgg')  # Open in the new window
        
        img_orig = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

        img_pred = ShelfVisualizer.draw_bboxes(img, pred_boxes, (0, 255, 0))
        img_pred_rgb = cv2.cvtColor(img_pred, cv2.COLOR_BGR2RGB)
        
        if gt_boxes is not None:
            img_gt = ShelfVisualizer.draw_bboxes(img, gt_boxes, (0, 0, 255))
            img_gt_rgb = cv2.cvtColor(img_gt, cv2.COLOR_BGR2RGB)
        
        _, axes = plt.subplots(1, 3, figsize=(18, 6))
        axes[0].imshow(img_orig) 
        axes[0].set_title('Image')
        axes[0].axis('off')

        axes[1].imshow(img_pred_rgb)
        axes[1].set_title('Predicted bboxes')
        axes[1].axis('off')

        if gt_boxes is not None:
            axes[2].imshow(img_gt_rgb)
            axes[2].set_title('Labeled bboxes')
            axes[2].axis('off')
        
        metric = round(metrics['f1'], 3) if metrics.get("f1") else "-"
        pred_len = len(pred_boxes)
        gt_len = len(gt_boxes) if gt_boxes is not None else "-"
        plt.suptitle(
            f'F1: {metric} | '
            f'Pred bboxes count: {pred_len} | '
            f'Labeled bboxes count: {gt_len}'
        )
        plt.tight_layout()
        
        if is_open_new_window:
            plt.show(block=True)  # Block execute before closing windows
        else:
            plt.show()


class ShelfAnalyzer:
    def __init__(
        self, 
        yolo_modelpath: str=YOLO_MODELPATH
    ):
        self.yolo_model: YOLO = YOLO(yolo_modelpath)
        self.embedder: Img2VecCLIP = Img2VecCLIP()

    def _xywh2xyxy(self, boxes: np.ndarray, img_shape: Tuple[int, int]) -> np.ndarray:
        '''XYWH normalize to XYXY pixels'''

        h: int
        w: int
        xc: np.ndarray
        yc: np.ndarray
        bw: np.ndarray
        bh: np.ndarray
        x1: np.ndarray
        y1: np.ndarray
        x2: np.ndarray
        y2: np.ndarray
        xyxy: np.ndarray

        h, w = img_shape[:2]
        xc, yc, bw, bh = boxes[:, 0], boxes[:, 1], boxes[:, 2], boxes[:, 3]
        x1 = (xc - bw/2) * w
        y1 = (yc - bh/2) * h
        x2 = (xc + bw/2) * w
        y2 = (yc + bh/2) * h

        xyxy = np.column_stack([x1, y1, x2, y2]).astype(int)

        return xyxy

    def _calc_iou(self, gt_boxes_xyxy: np.ndarray, pred_boxes_xyxy: np.ndarray) -> np.ndarray:
        pred: np.ndarray
        gt: np.ndarray
        inter_x1: np.ndarray
        inter_y1: np.ndarray
        inter_x2: np.ndarray
        inter_y2: np.ndarray
        inter_w: np.ndarray
        inter_h: np.ndarray
        inter_area: np.ndarray
        pred_area: np.ndarray
        gt_area: np.ndarray
        union_area: np.ndarray
        iou: np.ndarray

        if not(len(gt_boxes_xyxy) == 0 or len(pred_boxes_xyxy) == 0):
            # Broadcasting (N,1,4) + (1,M,4) → (N,M,4)
            pred = pred_boxes_xyxy[:, None, :]    # (N,1,4)
            gt = gt_boxes_xyxy[None, :, :]        # (1,M,4)

            # Intersection
            inter_x1 = np.maximum(pred[..., 0], gt[..., 0])
            inter_y1 = np.maximum(pred[..., 1], gt[..., 1])
            inter_x2 = np.minimum(pred[..., 2], gt[..., 2])
            inter_y2 = np.minimum(pred[..., 3], gt[..., 3])
            
            inter_w = np.maximum(0, inter_x2 - inter_x1)
            inter_h = np.maximum(0, inter_y2 - inter_y1)
            inter_area = inter_w * inter_h

            # Union
            pred_area = (pred[..., 2] - pred[..., 0]) * (pred[..., 3] - pred[..., 1])
            gt_area = (gt[..., 2] - gt[..., 0]) * (gt[..., 3] - gt[..., 1])
            
            union_area = pred_area + gt_area - inter_area
            iou = inter_area / (union_area + 1e-8)

            iou = iou.squeeze()  # (N,M)

        else:
            iou =  np.zeros((len(pred_boxes_xyxy), len(gt_boxes_xyxy)))

        return iou

    def get_target_img(self, img_path: Path) -> np.ndarray:
        img: np.ndarray 
        is_good: bool
        eda_result: dict
        
        img = cv2.imread(str(img_path))

        is_good, eda_result = SKUPreprocessor.eda(img)

        if is_good is False:
            img = SKUPreprocessor.fix_dirty(img, eda_result)
        else:
            img = SKUPreprocessor.resize_img_with_scale(img)

        return img

    def load_ground_truth_labels(self, label_path: Path, img_shape: Tuple[int, int]) -> np.ndarray:
        '''
        YOLO txt to XYXY pixels
        '''
        gt_bboxes: np.ndarray
        gt_xywh: np.ndarray
        gt_xyxy: np.ndarray

        # [[cls,xc,yc,w,h], ...]
        gt_bboxes = np.loadtxt(str(label_path), delimiter=' ') 

        # [[xc,yc,w,h], ...]
        gt_xywh = gt_bboxes[:, 1:]  # (M,4)
        gt_xyxy = self._xywh2xyxy(gt_xywh, img_shape)
        
        return gt_xyxy
    
    def predict_bboxes(self, img: np.ndarray) -> dict:
        predict: List[YoloEngineResults]
        idx: int
        idx_bbox: List[int] | np.ndarray
        conf_bbox: List[np.ndarray] | np.ndarray
        area_px: List[np.ndarray] | np.ndarray
        pred_xyxy: List[np.ndarray] | np.ndarray

        predict = self.yolo_model(img, conf=PREDICT_PARAMS.YOLO_THRESHOLD, verbose=False)
        
        idx_bbox = []
        conf_bbox = []
        area_px = []
        pred_xyxy = []
        for r in predict:
            if r.boxes is not None:
                boxes = r.boxes.xyxy.cpu().numpy()
                conf = r.boxes.conf.cpu().numpy()
                
                idx_bbox.append(np.arange(len(boxes)))
                conf_bbox.append(conf)
                area_px.append((boxes[:, 2] - boxes[:, 0]) * (boxes[:, 3] - boxes[:, 1]))
                pred_xyxy.append(boxes)
        
        if pred_xyxy:
            pred_xyxy = np.vstack(pred_xyxy)
            conf_bbox = np.concatenate(conf_bbox)
            area_px = np.concatenate(area_px)
            idx_bbox = np.concatenate(idx_bbox)
        else:
            pred_xyxy = np.empty((0, 4))
            conf_bbox = np.empty(0)
            area_px = np.empty(0)
            idx_bbox = np.empty(0, dtype=int)

        return {
            'pred_xyxy': pred_xyxy,
            'conf_bbox': conf_bbox,
            'area_px': area_px,
            'idx_bbox': idx_bbox
        }
    
    def calc_metrics(self, gt_xyxy: np.ndarray, pred_xyxy: np.ndarray) -> dict:
        metrics: dict
        iou_matrix: np.ndarray        
        gt_bboxes_used: np.ndarray
        best_gt_idx: np.intp

        true_positive: int
        false_positives: int
        false_negative: int
        precision: float
        recall: float
        f1: float

        metrics = {
            'true_positive': 0,
            'false_positives': len(pred_xyxy),
            'false_negative': len(gt_xyxy),
            'precision': 0.0,
            'recall': 0.0,
            'f1': 0.0,
            # 'osa': 0.0
        }

        if len(gt_xyxy) == 0 or len(pred_xyxy) == 0: return metrics

        # IoU matrix match + calc metrics
        iou_matrix = self._calc_iou(gt_xyxy, pred_xyxy)

        true_positive = 0
        gt_bboxes_used = np.zeros(len(gt_xyxy), dtype=bool)

        for i in range(len(pred_xyxy)):
            best_gt_idx = np.argmax(iou_matrix[i])
            if iou_matrix[i, best_gt_idx] > PREDICT_PARAMS.IOU_THRESHOLD and not gt_bboxes_used[best_gt_idx]:
                true_positive += 1
                gt_bboxes_used[best_gt_idx] = True
        
        false_positives = len(pred_xyxy) - true_positive
        false_negative = len(gt_xyxy) - true_positive
        
        precision = (
            true_positive / (true_positive + false_positives)
            if (true_positive + false_positives) > 0 else 0.0
        )

        recall = (
            true_positive / (true_positive + false_negative)
            if (true_positive + false_negative) > 0 else 0.0
        )

        f1 = (
            (2 * precision * recall) / (precision + recall) 
            if precision + recall > 0 else 0.0
        )
        
        # Update result
        metrics['true_positive'] = true_positive
        metrics['false_positives'] = false_positives
        metrics['false_negative'] = false_negative
        metrics['precision'] = precision
        metrics['recall'] = recall
        metrics['f1'] = f1

        return metrics

    def crops_to_clusters(
        self, img: np.ndarray, bboxes_data: dict, output_dir: Path
    ) -> Tuple[int, np.ndarray, str]:
        
        n_clusters: int
        img_vis: np.ndarray
        crops: List[np.ndarray]
        embeddings: List[np.ndarray]
        embeddings: np.ndarray
        x1: float
        y1: float
        x2: float
        y2: float
        scaler: StandardScaler
        clusterer: hdbscan.HDBSCAN
        labels: List[int]
        target_output_dir: Path
        cluster_dir: Path
        save_path: Path
                
        n_clusters = 0
        if len(bboxes_data['pred_xyxy']) != 0: 
            img_vis = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)       
            crops = []
            embeddings = []
            
            for i, box in enumerate(tqdm(bboxes_data['pred_xyxy'])):
                x1, y1, x2, y2 = box
                
                # Padded crop with neighbors context
                x1 = max(0, int(x1 - KNN_THRESHOLDS.PADDING))
                y1 = max(0, int(y1 - KNN_THRESHOLDS.PADDING))
                x2 = min(img_vis.shape[1], int(x2 + KNN_THRESHOLDS.PADDING))
                y2 = min(img_vis.shape[0], int(y2 + KNN_THRESHOLDS.PADDING))
                
                crop = img_vis[y1:y2, x1:x2]
                crops.append(crop)
                
                # Compute embedding
                emb = self.embedder.getVec(crop)
                embeddings.append(emb)
            
            # Stack embeddings
            embeddings = np.array(embeddings)  # Shape: (N, 512)
            
            # Normalize for clustering
            scaler = StandardScaler()
            embeddings = scaler.fit_transform(embeddings)

            
            clusterer = hdbscan.HDBSCAN(
                min_cluster_size=KNN_THRESHOLDS.HDBSCAN_PARAMS.MIN_CLUSTER_SIZE, 
                min_samples=KNN_THRESHOLDS.HDBSCAN_PARAMS.MIN_SAMPLES
            )
            labels = clusterer.fit_predict(embeddings)
            
            # Create cluster folders
            target_output_dir = output_dir / 'clusters'
            target_output_dir.mkdir(exist_ok=True)
            
            n_clusters = len(set(labels)) - (1 if -1 in labels else 0)
            print(f"Found {n_clusters} clusters (+ {-1 in labels} noise points)")
            
            # Save crops to cluster folders
            for i, (crop, label) in enumerate(zip(crops, labels)):
                if label == -1:
                    cluster_dir = target_output_dir / 'noise'
                else:
                    cluster_dir = target_output_dir / f'cluster_{label}'
                
                cluster_dir.mkdir(exist_ok=True)
                
                # Save as JPG (sequential naming)
                save_path = cluster_dir / f'crop_{i:03d}.jpg'
                cv2.imwrite(str(save_path), cv2.cvtColor(crop, cv2.COLOR_RGB2BGR))
            
        return n_clusters, labels, str(target_output_dir)

    def analyze(self, req_params: dict) -> Tuple[dict, dict]:
        '''
        [ALL KEYS ARE OPTIONAL]
        metrics = {
            'true_positive': int
            'false_positives': int
            'false_negative': int
            'precision': float
            'recall': float
            'f1': float
            'detected_clusters': int
            'clusters_output_dir': str
        }

        [ONE KEY IS OPTIONAL]
        bboxes_data = {
            'pred_xyxy': np.ndarray
            'conf_bbox': np.ndarray
            'area_px': np.ndarray
            'idx_bbox': np.ndarray
            'cluster_name': np.ndarray [OPTIONAL]
        }
        '''
        total_exec: float
        img: np.ndarray 
        gt_xyxy: np.ndarray
        bboxes_data: dict
        metrics: dict

        metrics = {}
        gt_xyxy = None

        print('\n***> Start analyzing:')
        print('\t--> Get img and predict bboxes')
        total_exec = time.perf_counter()

        img = self.get_target_img(req_params['img_path'])
        
        if req_params['no_compare_bboxes'] is False:
            gt_xyxy = self.load_ground_truth_labels(req_params['label_path'], img.shape[:2])
        
        bboxes_data = self.predict_bboxes(img)

        total_exec = time.perf_counter() - total_exec
        req_params['total_exec_sec'] = total_exec

        if req_params['no_compare_bboxes'] is False:
            print('\t--> Calculate metrics')
            metrics = self.calc_metrics(gt_xyxy, bboxes_data['pred_xyxy'])

        if req_params['no_detect_clusters'] is False:
            print('\t--> Grouping in clusters')
            n_clusters, labels, output_dir = self.crops_to_clusters(
                img, bboxes_data,
                output_dir=req_params['output_dir']
            )
            bboxes_data['cluster_name'] = labels
            metrics['detected_clusters'] = n_clusters
            req_params['clusters_output_dir'] = output_dir

        if req_params['no_show_vis'] is False:
            ShelfVisualizer.show_comparison(
            img,
            bboxes_data['pred_xyxy'], 
            gt_xyxy,
            metrics
        )

        return metrics, bboxes_data
    