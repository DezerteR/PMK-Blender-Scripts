import io
def write_yaml_to(stream, object):
    write_collection_to(stream, object, "")

def write_collection_to(stream, object, indent=""):
        if isinstance(object, dict):
            for key, value  in object.items():
                write_to(stream, value, key, indent, )
        elif isinstance(object, list):
            for value  in object:
                write_to(stream, value, "", indent, True)

def write_to(stream, object, key, indent="", is_part_ofArray=False):
    value = stringify(object)
    is_array = isinstance(object, list)
    if is_part_ofArray:
        stream.write(indent[0:-2] + "- ")
        print_without_indent = value == ""
        if value != "":
            stream.write(value + "\n")

        write_collection_to(stream, object, indent + ("" if print_without_indent else "  "))

    else:
        stream.write(indent + key + ": " + value + "\n")
        write_collection_to(stream, object, indent + "  ")


def stringify(object):
    if isinstance(object, list) or isinstance(object, dict):
        return ""
    else:
        return str(object)

if __name__ == '__main__':

    object = {
        "A": 10,
        "B": 20,
        "C": [12, 13],
        "D": [
            {"E": 16,
             "U": "sdf"},
            {"F": 20}
        ]
    }
    stream = io.StringIO()
    write_yaml_to(stream, object)
    print(stream.getvalue())
