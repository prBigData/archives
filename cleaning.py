from os import listdir
from os.path import isfile, join


def cleanall(path, last=False, export_path=None):
    """format json files to spark readable"""

    filelist = [f for f in listdir(path) if isfile(join(path, f))]
    if not last:
        # pop last (which is current writing file)
        del filelist[-1]

    for filename in filelist:
        with open(path + filename, "r") as f:
            string = f.read()
        string = string.replace("][", ", ")
        string = string.replace("},", "},\n")
        string = string.replace("[", "")
        string = string.replace("]", "")
        if export_path:
            with open(export_path + filename, "w") as f2:
                f2.write(string)

    return string
