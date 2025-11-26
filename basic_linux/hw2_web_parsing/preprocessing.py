import logging

import pandas as pd

from config import (
    define_logging,
    INT_INFO_COLS,
    NUMERIC_INFO_COLS,
    STR_INFO_COLS,
    DICT_INFO_COLS
)

define_logging()



def replace_nans(df: pd.DataFrame):
    df_current = df.copy()
    logging.info(f'Dataframe NaNs by fields before: \n{df_current.isnull().sum()}\n')
    
    # Revalue numeric
    df_current[NUMERIC_INFO_COLS] = df_current[NUMERIC_INFO_COLS].astype(float)
    df_current[NUMERIC_INFO_COLS] = df_current[NUMERIC_INFO_COLS].fillna(
        df_current[NUMERIC_INFO_COLS].mean()
    )
    
    df_current[INT_INFO_COLS] = df[INT_INFO_COLS].astype(int)

    # Revalue str
    df_current[STR_INFO_COLS] = df_current[STR_INFO_COLS].fillna(
        'Empty'
    )
    
    # Revalue dict
    df_current[DICT_INFO_COLS] = df_current[DICT_INFO_COLS].fillna(
        {}
    )

    logging.info(f'Dataframe NaNs by fields after: \n{df_current.isnull().sum()}\n')

    return df_current