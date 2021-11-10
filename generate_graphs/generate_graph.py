import pandas as pd
from blob_storage_client import BlobStorageClient
import logging
import io
import matplotlib.pyplot as plt


class GenerateGraph:

    def __init__(self, cosmos_db_client_obj) -> None:

        # connect to cosmos db and blob storage
        self.cosmos_db_client_obj = cosmos_db_client_obj

        # TODO: find a better way to connect with BlobStorage
        # create different client for each blob
        self.blob_client_obj_vaccine_status = BlobStorageClient(
            "coviorg-graph", "vaccine_status_graph.png")
        self.blob_client_obj_vaccine_name = BlobStorageClient(
            "coviorg-graph", "vaccine_name_graph.png")

        self.blob_client_obj_department_vaccination_status = BlobStorageClient(
            "coviorg-graph", "department_vaccination_status.png")
        self.blob_client_obj_department_vaccination_status_bar = BlobStorageClient(
            "coviorg-graph", "department_vaccination_status_bar.png")

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
        """Process the image and upload it to blob storage"""
        buf = io.BytesIO()
        image_object.savefig(buf, format='png')

        # get value of the image in bytes
        byte_im = buf.getvalue()

        # upload it to blob storage with the respective client
        blob_client.upload_blob(
            byte_im, overwrite=True, blob_type="BlockBlob")
        # flush and close the buffer for next image to be created and stored
        buf.flush()
        buf.close()

    def generate_graph_vaccine_status(self):

        # create pie graph with pandas dataframe
        vaccine_status_fig = self.vaccine_status_df.plot.pie(
            y="vaccination_status", figsize=(8, 8), fontsize=20,
            legend="vaccination_status", title="By Vaccination Status",
            autopct=lambda p: '{:.0f}'.format(
                (p / 100) * self.vaccine_status_df.sum()),
            cmap="terrain").legend(loc="upper left")

        image_object = vaccine_status_fig.get_figure()

        self.save_image_to_blob_storage(
            self.blob_client_obj_vaccine_status.blob_client, image_object)

        # clear the image object after uploading the image to blob storage
        image_object.clear(True)

    def generate_graph_vaccination_name(self):
        # create pie graph with pandas dataframe
        vaccine_name_fig = self.vaccine_name_df.plot.pie(
            y="vaccine_name", figsize=(8, 8), fontsize=20,
            legend="vaccine_name", title="By Vaccine Name",
            autopct=lambda p: '{:.0f}'.format(
                (p / 100) * self.vaccine_name_df.sum()),
            cmap="Pastel1")

        # get the figure object
        image_object = vaccine_name_fig.get_figure()

        self.save_image_to_blob_storage(
            self.blob_client_obj_vaccine_name.blob_client, image_object)

        image_object.clear(True)

    def generate_graph_department_with_vaccination_status(self):
        # create a dataframe from all the documents in the cosmos DB
        df_temp = pd.DataFrame(self.query_result)

        # generate the scatter plot
        department_vaccination_status_fig = df_temp.plot.scatter(
            x="department", y="vaccination_status", color="#E26A2C",
            figsize=(35, 14), fontsize=30)

        image_object = department_vaccination_status_fig.get_figure()

        self.save_image_to_blob_storage(
            self.blob_client_obj_department_vaccination_status.blob_client,
            image_object)

        # clear the image to avoid overlapping of images while plotting
        image_object.clear(True)

    def generate_graph_department_with_vaccination_status_bar(self):

        df = pd.DataFrame(self.query_result)
        # get only unique departments
        department_list = df["department"].drop_duplicates()

        vaccination_status_list = {
            "Fully Vaccinated": [],
            "Partially Vaccinated": [],
            "Not Vaccinated": []}

        # iterate through all the departments and get the people with different vaccination status
        for department_name in department_list:

            vaccination_status_list["Fully Vaccinated"].extend([
                list(
                    ((df["department"] == department_name) &
                     (df["vaccination_status"] == "Fully Vaccinated"))).count(
                    True)])

            vaccination_status_list["Partially Vaccinated"].extend([list(
                ((df["department"] == department_name) &
                 (df["vaccination_status"] == "Partially Vaccinated"))).count(True)])

            vaccination_status_list["Not Vaccinated"].extend([list(
                ((df["department"] == department_name) &
                 (df["vaccination_status"] == "Not Vaccinated"))).count(True)])

        # create another dataframe with the result form the above iteration
        final_df = pd.DataFrame(vaccination_status_list, index=department_list)

        # finally plot the image
        department_vaccination_status_fig = final_df.plot(
            kind="bar", stacked=True, figsize=(12, 12), fontsize=20,
        ).legend(loc='upper right', ncol=4, title="By Department")

        image_object = department_vaccination_status_fig.get_figure()

        self.save_image_to_blob_storage(
            self.blob_client_obj_department_vaccination_status_bar.blob_client,
            image_object)

        # clear the image to avoid overlapping of images while plotting
        image_object.clear(True)

    def start_process(self):
        logging.info("Starting generate graph process")

        self.query_all_item_from_cosmos_db()

        self.prepare_df()

        try:
            # generate and upload graphs to blob storage
            self.generate_graph_department_with_vaccination_status()
            self.generate_graph_vaccination_name()
            self.generate_graph_vaccine_status()
            self.generate_graph_department_with_vaccination_status_bar()

        except Exception as e:
            logging.exception(
                f"An error occurred while trying to generate and upload image to blob storage \n Error details: \n {e}",
                exc_info=True, stack_info=True)

        logging.info("Successfully uploaded images to blob storage")
