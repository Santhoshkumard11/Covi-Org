from typing import Tuple
import pandas as pd
from blob_storage_client import BlobStorageClient
import logging
import io
import matplotlib.pyplot as plt


class GenerateGraph:

    def __init__(self, cosmos_db_client_obj) -> None:

        # connect to cosmos db and blob storage
        self.cosmos_db_client_obj = cosmos_db_client_obj

        self.blob_client_obj_vaccine_status = BlobStorageClient(
            "coviorg-graph", "vaccine_status_graph.png")
        self.blob_client_obj_vaccine_name = BlobStorageClient(
            "coviorg-graph", "vaccine_name_graph.png")

        self.blob_client_obj_department_vaccination_status = BlobStorageClient(
            "coviorg-graph", "department_vaccination_status.png")

        self.vaccine_status_df, self.vaccine_name_df = None, None

        plt.style.use('fivethirtyeight')

    def query_all_item_from_cosmos_db(self):

        self.query_result = self.cosmos_db_client_obj.get_all_items()

    def prepare_df(self):

        vaccine_name_list, vaccine_status_list = [], []
        # get the items from cosmos db
        for item in self.query_result:

            vaccine_name_list.append(item["vaccine_name"])
            vaccine_status_list.append(item["vaccination_status"])

        # create a new dataframe with the items from cosmos db
        df = pd.DataFrame(
            {"s.no": list(range(1, len(vaccine_name_list) + 1)),
             'vaccine_name': vaccine_name_list,
             'vaccination_status': vaccine_status_list},
            columns=["s.no", 'vaccine_name', 'vaccination_status'])

        # count the vaccination status and vaccine name
        self.vaccine_status_df = df.groupby(
            "vaccination_status")["s.no"].count()
        self.vaccine_name_df = df.groupby("vaccine_name")["s.no"].count()

        logging.info("Gathered the data and created the dataframe")

    def save_image_to_blob_storage(self, blob_client, image_object):
        buf = io.BytesIO()
        image_object.savefig(buf, format='png')

        byte_im = buf.getvalue()

        blob_client.upload_blob(
            byte_im, overwrite=True, blob_type="BlockBlob")
        buf.flush()
        buf.close()

    def generate_graph_vaccine_status(self):

        # create pie graph with pandas dataframe
        vaccine_status_fig = self.vaccine_status_df.plot.pie(
            y="vaccination_status", figsize=(5, 5),
            legend="vaccination_status", title="By Vaccination Status",
            autopct=lambda p: '{:.0f}'.format(
                (p / 100) * self.vaccine_status_df.sum()),
            cmap="terrain")

        image_object = vaccine_status_fig.get_figure()

        self.save_image_to_blob_storage(
            self.blob_client_obj_vaccine_status.blob_client, image_object)

        # clear the image object after uploading the image to blob storage
        image_object.clear(True)

    def generate_graph_vaccination_name(self):
        # create pie graph with pandas dataframe
        vaccine_name_fig = self.vaccine_name_df.plot.pie(
            y="vaccine_name", figsize=(5, 5),
            legend="vaccine_name", title="By Vaccine Name",
            autopct=lambda p: '{:.0f}'.format(
                (p / 100) * self.vaccine_name_df.sum()),
            cmap="plasma")

        # get the figure object
        image_object = vaccine_name_fig.get_figure()

        self.save_image_to_blob_storage(
            self.blob_client_obj_vaccine_name.blob_client, image_object)

        image_object.clear(True)

    def generate_graph_department_with_vaccination_status(self):
        df_temp = pd.DataFrame(self.query_result)

        department_vaccination_status_fig = df_temp.plot.scatter(
            x="department", y="vaccination_status", color="#E26A2C")

        image_object = department_vaccination_status_fig.get_figure()

        self.save_image_to_blob_storage(
            self.blob_client_obj_department_vaccination_status.blob_client,
            image_object)

        image_object.clear(True)

    def start_process(self):
        logging.info("Starting generate graph process")

        self.query_all_item_from_cosmos_db()

        self.prepare_df()

        self.generate_graph_department_with_vaccination_status()
        self.generate_graph_vaccination_name()
        self.generate_graph_vaccine_status()

        logging.info("Successfully generated image objects")

        logging.info("Successfully uploaded image to blob storage")