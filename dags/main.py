from airflow import DAG
import pendulum #Deals with Timezones
from datetime import datetime, timedelta
from airflow.operators.trigger_dagrun import TriggerDagRunOperator

from api.video_stats import (
    get_playlist_id,
    get_video_ids,
    extract_video_data,
    save_to_json,
)

from datawarehouse.dwh import staging_table, core_table
from dataquality.soda import yt_elt_data_quality

# Define the local timezone
local_tz = pendulum.timezone("America/New_York")

# Default Args
default_args = {
    "owner": "dataengineers",
    "depends_on_past": False,
    "email on failure": False,
    "email_on_retry": False,
    "email": "data@engineers.com",
    # 'retries': 1
    # 'retry_delay• : timedelta(minutes=5),
    "max active runs": 1,
    "dagrun_timeout": timedelta(hours=1),
    "start_date": datetime(2025, 1, 1, tzinfo=local_tz), #time at which airflow will begin running the DAG, but the first time will be scheduled at the end of the interval following the start date
    # •end _ date': datetime(2030, 12, 31, tzinfo=local_tz),
}

# Variables
staging_schema = "staging"
core_schema = "core"

# Declaring DAGS. There are 3 ways according the web page
# Dag #1: produce_json
with DAG(
        dag_id='produce_json',
        default_args=default_args,
        description='DAG to produce JSON file with raw data',
        schedule='0 14 * * *', #it will run a 2:00 pm everyday
        catchup=False
) as dag_produce:
    
    # Defining the tasks by calling the funtions in the video task scripts
    playlist_id = get_playlist_id()
    video_ids = get_video_ids(playlist_id)
    extract_data = extract_video_data(video_ids)
    save_to_json_task = save_to_json(extract_data)

    trigger_update_db = TriggerDagRunOperator(
        task_id="trigger_update_db",
        trigger_dag_id = "update_db",
    )
    # Defining dependencies, this is in what order will the tasks run from left to right
    playlist_id >> video_ids >> extract_data >> save_to_json_task >> trigger_update_db

# For triggering the deck manually go on the airflow UI
# DAG 2: update_db
with DAG(
    dag_id='update_db',
    default_args=default_args,
    description='DAG to process JSON file and insert data into both staging and core schemas',
    #schedule='0 15 * * *', #it will run a 2:00 pm everyday
    catchup=False,
    schedule=None,
) as dag_update:

    # Defining the tasks by calling the funtions in the video task scripts
    update_staging = staging_table()
    update_core = core_table()
    # Defining dependencies, this is in what order will the tasks run from left to right

    trigger_data_quality = TriggerDagRunOperator(
        task_id="trigger_data_quality",
        trigger_dag_id="data_quality",
    )
    update_staging >> update_core >> trigger_data_quality
    # For triggering the deck manually go on the airflow UI
#For Dataquality test
# DAG 3: data_quality
with DAG(
    dag_id='data_quality',
    default_args=default_args,
    description='DAG to check the data quality on both layers in the db',
    #schedule='0 16 * * *', #it will run a 2:00 pm everyday
    catchup=False,
    schedule=None,
) as dag_quality:
    
    # Defining the tasks by calling the funtions in the video task scripts
    soda_validate_staging = yt_elt_data_quality(staging_schema)
    soda_validate_core = yt_elt_data_quality(core_schema)

    # Defining dependencies, this is in what order will the tasks run from left to right
    soda_validate_staging >> soda_validate_core