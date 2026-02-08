import argparse
import json
from datetime import datetime

from utils.utils import get_execute_params, form_response
from utils.analyze_shelf import ShelfAnalyzer
    
def main():
    try:
        parser = argparse.ArgumentParser(description='Product Shelf Analysis')
        parser.add_argument('--image', '-i', help='Path to shelf image')
        parser.add_argument('--label', '-l', help='Path to label (.txt)')
        parser.add_argument('--output', '-o', default='data/tmp_results', help='Path to JSON result')
        parser.add_argument('--no-group-in-clusters', action='store_true', help='Do not group bboxes (crops) into clusters')
        parser.add_argument('--no-visual', action='store_true', help='Do not show bboxes visualization')

        # Pars params
        req_params = get_execute_params(parser)

        req_params['req_time'] = datetime.now()
        req_params['img_name'] = req_params['img_path'].name.split('.')[0]
        req_params['req_prefix'] = req_params['req_time'].strftime("%Y%m%d%H%M%S")
        req_params['req_id'] = f'req_{req_params["req_prefix"]}'
        req_params['output_dir'] /= f"{req_params['img_name']}_{req_params['req_prefix']}"

        req_params['output_dir'].mkdir(exist_ok=True)

        # Start analyzer pipeline
        print('\n***> Define analyzer')
        analyzer = ShelfAnalyzer()
        
        metrics, bboxes_data = analyzer.analyze(req_params)

        response = form_response(req_params, metrics, bboxes_data)

        response_path = req_params['output_dir'] / 'response.json'
        
        # Save JSON results
        with open(response_path, 'w', encoding='utf-8') as f:
            json.dump(response, f, ensure_ascii=False, indent=2)
        
        print(
            f"\n********** Analyze completed **********\n"
            f"\t--> Exec time: {req_params['total_exec_sec']: 0.2f}s | {req_params['total_exec_sec'] * 1000: 0.2f}mls\n"
            f"\t--> Image path: {req_params['img_path']}\n"
            f"\t--> Results path: {req_params['output_dir']}\n"
            f"\t--> Response filepath: {response_path}\n"
            f"\t--> Metrics: {json.dumps(metrics, indent=2, ensure_ascii=False)}"
        )

        print('\nRESPONSE 200: Success')

    except Exception as e:
        print('\nRESPONSE 500: Service Error:', e, sep='\n')

if __name__ == '__main__':
    main()