import os
import zipfile


def unzip(filepath, destination):
    with zipfile.ZipFile(filepath, "r") as zip_ref:
        zip_ref.extractall(destination)
        os.remove(filepath)
