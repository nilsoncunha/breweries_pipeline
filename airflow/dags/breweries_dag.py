from airflow.decorators import dag
from airflow.models.param import Param
from airflow.operators.bash import BashOperator
from airflow.operators.empty import EmptyOperator
from airflow.utils.task_group import TaskGroup
from airflow.utils.trigger_rule import TriggerRule
from datetime import datetime, timedelta

doc_md = """
    ## Breweries Pipeline
    Essa dag irá executar apenas quando realizado o Trigger. 
    - Bronze: Realiza a extração dos dados e salva em .json na camada Bronze.
    - Silver: Lê da camada Bronze e salva particionado na Silver como Delta Lake
    - Gold: Lê da camada Silver e realiza a agregação, salva como Delta Lake
    
    O processo sempre irá realizar a extração conforme o número da página nos parâmetros ao realizar o Trigger até o 
    momento em que a API retornar página vazia. Isso se dá ao fato de não sabermos a quantidade total de páginas uma vez
    que pode ocorrer adição ou subtração das informações.
"""

default_args = {
    'owner': 'Nilson Cunha',
    'start_date': datetime.now() - timedelta(days=1),
    'email_on_failure': False,
    # 'retries': 1,
    # 'retry_delay': timedelta(minutes=2),
}

@dag(
    dag_id='brewery_pipeline_dag',
    default_args=default_args,
    schedule_interval=None,  # None pois será executado manualmente.
    catchup=False,
    description='Pipeline para ELT dos dados da API breweries',
    tags=['Pipeline', 'ELT', 'Breweries'],
    params={
        "page_number": Param(default=1, type='integer', minimum=1)
    },
    doc_md=doc_md
)
def breweries_pipeline():
    start, end = [EmptyOperator(task_id=task_id) for task_id in ['start', 'end']]

    with TaskGroup(group_id='Breweries') as tg_breweries:
        bronze = BashOperator(
            task_id='bronze',
            bash_command='docker exec spark python3 app/src/to_bronze.py --page_number {{ params.page_number }}',
            trigger_rule=TriggerRule.ALL_SUCCESS,
        )

        silver = BashOperator(
            task_id='silver',
            bash_command='docker exec spark spark-submit app/src/to_silver.py',
            trigger_rule=TriggerRule.ALL_SUCCESS,
        )

        gold = BashOperator(
            task_id='gold',
            bash_command='docker exec spark spark-submit app/src/to_gold.py',
            trigger_rule=TriggerRule.ALL_SUCCESS,
        )

        start >> bronze >> silver >> gold >> end


breweries_pipeline()
