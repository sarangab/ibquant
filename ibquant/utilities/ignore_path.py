import os


def ignore_path(dest, dest_is_dir=True):
    if dest_is_dir:
        dest = dest + "/"
    if ".gitignore" not in os.listdir(os.getcwd()):
        with open(os.path.join(os.getcwd(), ".gitignore"), "a") as file:
            file.write("\n# added by ibtrader")
            file.write(f"\n{dest}")
        file.close()
    else:
        with open(os.path.join(os.getcwd(), ".gitignore"), "a") as file:
            file.write("\n# added by ibtrader")
            file.write(f"\n{dest}")
        file.close()
