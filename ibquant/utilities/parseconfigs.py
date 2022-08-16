import configparser
import os


def add_ibconfigs_section(configpath):
    with open(configpath, "r") as file:
        contents = file.readlines()
    contents.insert(0, "[ibconfigs]\n")
    with open(configpath, "w") as file:
        contents = "".join(contents)
        file.write(contents)
