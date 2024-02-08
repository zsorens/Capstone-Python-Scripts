# # # # #
# DEPRECIATED
# # # # #
# Used to save files into Azure Storage Blob
# -> Depreciated as that is technically against Google TOS to save images recieved from Google Maps API
# 


from azure.core.exceptions import (
    ResourceExistsError,
    ResourceNotFoundError
)

from azure.storage.fileshare import (
    ShareServiceClient,
    ShareClient,
    ShareDirectoryClient,
    ShareFileClient
)
import os
import dotenv
dotenv.load_dotenv()


FILES_CONNECT = os.getenv('FILES_CONNECT')
FILES_SHARE = os.getenv("FILES_SHARE")
# Set up function
# Addrive service client, accessing
# Share client -> File directory.
def set_up():
    global service_client
    global share_client
    try:
        service_client = ShareServiceClient.from_connection_string(FILES_CONNECT)
        share_client = ShareClient.from_connection_string(
                FILES_CONNECT, FILES_SHARE)
    except Exception as e:
        print("Error in set up: ", e) 
# File Upload
def upload(local_file_path,dest_file_path):
    try:
        # Create a ShareFileClient from a connection string
        file_client = ShareFileClient.from_connection_string(
            FILES_CONNECT, FILES_SHARE, dest_file_path)
        source_file = open(local_file_path, "rb")
        data = source_file.read()

        file_client.upload_file(data)

    except ResourceExistsError as ex:
        print("ResourceExistsError:", ex.message)

    except ResourceNotFoundError as ex:
        print("ResourceNotFoundError:", ex.message)
# mimics ls command from linux
def ls(dir_name):
    try:
        for item in list(share_client.list_directories_and_files(dir_name)):
            if item["is_directory"]:
                print("Directory:", item["name"])
            else:
                print("File:", dir_name + "/" + item["name"])

    except ResourceNotFoundError as ex:
        print("ResourceNotFoundError:", ex.message)
# delete said file
def delete(self, file_path):
    try:
        # Create a ShareFileClient from a connection string
        file_client = ShareFileClient.from_connection_string(
            FILES_CONNECT, FILES_SHARE, file_path)

        print("Deleting file:", share_name + "/" + file_path)

        # Delete the file
        file_client.delete_file()

    except ResourceNotFoundError as ex:
        print("ResourceNotFoundError:", ex.message)
