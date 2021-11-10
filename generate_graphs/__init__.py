import datetime
import logging
from cosmos_db_client import CosmosDBClient
from .generate_graph import GenerateGraph

import azure.functions as func


def main(mytimer: func.TimerRequest) -> None:
    utc_timestamp = datetime.datetime.utcnow().replace(
        tzinfo=datetime.timezone.utc).isoformat()

    logging.info(
        'Python timer trigger Genreate Graph function started at %s',
        utc_timestamp)

    if mytimer.past_due:
        logging.info('The timer is past due!')

    logging.info("Generate graphs started!!")

    cosmos_db_client_obj = CosmosDBClient(
        "CoviOrg", "EmployeeTable", "emp_id")

    cosmos_db_client_obj.connect()

    logging.info("Successfully connected with cosmos db!!")

    generate_graph_obj = GenerateGraph(
        cosmos_db_client_obj)

    generate_graph_obj.start_process()

    logging.info("graph process has been successfully completed!!")
