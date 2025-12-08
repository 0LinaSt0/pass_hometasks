import sys
import os
from pathlib import Path

DATAPATH = '/home/msalena/SFMaga/main_repo/mlops/sources/files_hw_DE'

sys.path.insert(0, DATAPATH)

from functools import reduce
from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import pandas as pd
from transform_script import transfrom

PROFIT_TABLE_FILE = Path(DATAPATH) / 'profit_table.csv'
OUTPUT_FILE = Path(DATAPATH) / 'flags_activity.csv'
PRODUCTS = list('abcdefghij')

default_args = {
    'owner': 'msalena',
    'retries': 1,
    "retry_delay": timedelta(minutes=5),
}


def get_prev_month_first_day(logical_date):
    '''Get first day of prev month'''

    prev_month = logical_date.subtract(months=1)
    date_str = prev_month.replace(day=1).strftime('%Y-%m-%d')

    # ~~~ FOR DEBUG:
    # date_str = '2024-03-01'
    # ~~~ ~~~ ~~~ ~~~

    return date_str


def process_product(product, **context):
    '''Create tmp json for product and return path to it'''
    if not os.path.exists(PROFIT_TABLE_FILE):
        raise FileNotFoundError(f'Data file not found: {PROFIT_TABLE_FILE}')

    df = pd.read_csv(PROFIT_TABLE_FILE)

    if df.empty:
        raise ValueError(f'Data file is empty: {PROFIT_TABLE_FILE}')

    date_str = get_prev_month_first_day(context['logical_date'])
    
    print(f'PRODUCT: {product}, DATE FOR CALCULATING: {date_str}')
    
    temp_path = str(Path(DATAPATH) / f'tmp_{product}_result.json')
    df_result = transfrom(df, date_str, product_list=[product,])
    df_result.to_json(temp_path)
    
    return temp_path

def merge_and_save(**context):
    '''Save all products to one file'''
    ti = context['ti']
    dfs = []

    for product in PRODUCTS:
        json_path = ti.xcom_pull(task_ids=f'polina_khristoforova_{product}')
        df = pd.read_json(json_path)
        dfs.append(df)

    # Merge all to one dataframe by id
    final_df = reduce(
        lambda left, right: pd.merge(left, right, on='id', how='outer'), 
        dfs
    ).reset_index(drop=True)

    # Save data on append mode if file exists
    if os.path.exists(OUTPUT_FILE):
        final_df.to_csv(OUTPUT_FILE, index=False, mode='a', header=False)
    else:
        final_df.to_csv(OUTPUT_FILE, index=False)

    print(f'Saved final DataFrame: {OUTPUT_FILE}')
    print(f'Rows: {final_df.shape[0]}')


with DAG(
    'polina_khristoforova',
    default_args=default_args,
    schedule_interval='0 0 5 * *',  # every 5th day of every month at 12am
    catchup=False,
    start_date=datetime(2024, 4, 1),
    max_active_runs=1,
) as dag:

    # 1. Parallel calculate and save to tmp_json file for every product
    results = []
    for product in PRODUCTS:
        task = PythonOperator(
            task_id=f'polina_khristoforova_{product}',
            python_callable=process_product,
            op_kwargs={'product': product},
        )
        results.append(task)

    # 2. Save to one target .csv file 
    merge_task = PythonOperator(
        task_id='merge_and_save',
        python_callable=merge_and_save,
    )

    results >> merge_task
