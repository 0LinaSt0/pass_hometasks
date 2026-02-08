import argparse
from pathlib import Path

from consts import (
    DEFAULT_EXAMPLE_IMG, 
    DEFAULT_EXAMPLE_LABEL, 
    DEFAULT_OUTPUT_DIR
)

def get_execute_params(
    parser: argparse.ArgumentParser
) -> dict:
    req_params = {}

    args = parser.parse_args()
    try: req_params['img_path'] = Path(args.image) 
    except: req_params['img_path'] = Path('...')
    
    try: req_params['label_path'] = Path(args.label) 
    except: req_params['label_path'] = Path('...')

    try: req_params['output_dir'] = Path(args.output) 
    except: req_params['output_dir'] = Path('...')

    req_params['no_show_vis'] = args.no_visual
    req_params['no_detect_clusters'] = args.no_group_in_clusters 
    req_params['no_compare_bboxes'] = False

    if not req_params['img_path'].exists():
        req_params['img_path'] = DEFAULT_EXAMPLE_IMG
        req_params['label_path'] = DEFAULT_EXAMPLE_LABEL
        print(f'***> Invalid image path. Return results for img {req_params['img_path']} for demonstration')
    elif not req_params['label_path'].exists():
        if req_params['no_detect_clusters']:
            req_params['img_path'] = DEFAULT_EXAMPLE_IMG
            req_params['label_path'] = DEFAULT_EXAMPLE_LABEL
            print(f'***> Invalid label path. Return results for img {req_params['img_path']} for demonstration')
        else:
            req_params['no_compare_bboxes'] = True
            print(f'***> Invalid label path. Return only groups of clusters')

    if not req_params['output_dir'].exists(): 
        req_params['output_dir'] = DEFAULT_OUTPUT_DIR
        print(f'***> Invalid output dir. Save results to the {req_params['output_dir']}')

    return req_params


def form_response(req_params: dict, metrics: dict, bboxes_data: dict) -> dict:
    '''
    response = {
        'request_id': <req_id>,
        'timestamp': <req_time>,
        'store_id': None,
        'planogram_id': None,

        'detections': [
            {
                'sku': <num_sku>,
                'brand': <cluster_name>,
                'category': None,
                'confidence': confidence,
                'bbox': <x1, y1, x2, y2>
                'area_px': <area_px>
            }
        ],
        'counts': {
            'sku_by_categoty': {
                <cluster_name>:
                    'total_sku': None
                    'detected_sku': <count_sku_by_cluster>
                    'total_area_px': <area_by_cluster>
            },
            'total_sku': None
            'detected_sku': sum(by_clusters)
            'total_area_px': sum(by_clusters)
        },
        'planogram_match': None,

        'metrics': {
            'f1': <f1_if_exists>,
            'osa': None,
            'shelf': None
        },
        'processing_time_ms': float
    }
    '''

    sku_by_categoty = {}
    total_area_px = 0
    detections = []
    for idx in bboxes_data['idx_bbox']:
        idx = int(idx)
        current_sku = {
            'sku': idx,
            'category': None,
            'confidence': float(bboxes_data['conf_bbox'][idx]),
            'bbox': bboxes_data['pred_xyxy'][idx].tolist(),
            'area_px': float(bboxes_data['area_px'][idx])
        }

        if (cluster_names := bboxes_data.get('cluster_name')) is not None:
            cluster_name = int(cluster_names[idx])

            current_sku['brand'] = cluster_name

            if sku_by_categoty.get(cluster_name):
                sku_by_categoty[cluster_name]['detected_sku'] += 1
                sku_by_categoty[cluster_name]['total_area_px'] += current_sku['area_px']
            else:
                sku_by_categoty[cluster_name] = {
                    'total_sku': None,
                    'detected_sku': 1,
                    'total_area_px': current_sku['area_px']
                }
        
        total_area_px += current_sku['area_px']

        detections.append(current_sku)


    counts = {
        'sku_by_categoty': sku_by_categoty,
        'total_sku': None,
        'detected_sku': len(bboxes_data['idx_bbox']),
        'total_area_px': float(total_area_px)
    }
   

    response = {
        'request_id': req_params['req_id'],
        'timestamp': str(req_params['req_time']),
        'store_id': None,
        'planogram_id': None,

        'detections': detections,
        'counts': counts,
        'planogram_match': None,

        'metrics': {
            'f1': metrics['f1'] if metrics.get('f1') else None,
            'osa': None,
            'shelf': None
        },
        'processing_time_ms': round(req_params['total_exec_sec'] * 1000, 5)
    }

    return response