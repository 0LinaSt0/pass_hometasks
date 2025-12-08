import sys

DATAPATH = '/home/msalena/SFMaga/main_repo/mlops/sources/files_hw_DE'

sys.path.insert(0, DATAPATH)


from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.utils.dates import days_ago
import pendulum
import os
from pathlib import Path
import pandas as pd
from filelock import FileLock
from transform_script import transfrom

PROFIT_TABLE_FILE = Path(DATAPATH) / 'profit_table.csv'
OUTPUT_FILE = Path(DATAPATH) / 'flags_activity.csv'
LOCK_FILE = str(OUTPUT_FILE) + '.lock'
PRODUCTS = list('abcdefghij')

default_args = {
    'owner': 'msalena',
    'depends_on_past': False,
    'start_date': pendulum.datetime(year=2024, month=1, day=5).in_timezone('Europe/Moscow'),
    'retries': 1,
}

def save_results_safely(df_result):
    '''For safe save'''
    lock = FileLock(LOCK_FILE, timeout=10) 
    with lock:
        if os.path.exists(OUTPUT_FILE):
            df_result.to_csv(OUTPUT_FILE, index=False, mode='a', header=False)
        else:
            df_result.to_csv(OUTPUT_FILE, index=False)

def process_product(product, date=None, **context):
    if not os.path.exists(PROFIT_TABLE_FILE):
        print(f'Data file not found: {PROFIT_TABLE_FILE}')
    else:
        df = pd.read_csv(PROFIT_TABLE_FILE)

        if df.empty:
            print(f'Data file is empty: {PROFIT_TABLE_FILE}')
        else:
            if date is None:
                # Get previous month date for calculation (5th of current month -> previous month)
                date = context['logical_date'].subtract(months=1)
            
            date_str = date.strftime('%Y-%m-%d')
            print(f'PRODUCT: {product}, DATE FOR CALCULATING: {date_str}')

            before_size = 0
            if os.path.exists(OUTPUT_FILE):
                before_size = pd.read_csv(OUTPUT_FILE).shape[0]
                print(f'DF COUNT BEFORE: {before_size}')
            
            # Filter data for specific product and calculate
            df_result = transfrom(df, date_str, product_list=[product,])
            
            print(f'DF COUNT AFTER FOR {product}: {df_result.shape[0]}')


            # Save results
            save_results_safely(df_result)


with DAG(
    'polina_khristoforova',
    default_args=default_args,
    schedule_interval='0 0 5 * *',  # every 5th day of every month at 12am
    catchup=False,
    max_active_runs=1,
) as dag:

    tasks = []
    for product in PRODUCTS:
        task = PythonOperator(
            task_id=f'polina_khristoforova_{product}',
            python_callable=process_product,
            op_kwargs={'product': product},
        )
        tasks.append(task)