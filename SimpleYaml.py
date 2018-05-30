import io
import mathutils
primitive = (int, str, bool, float)

def write_yaml_to(stream, thing):
    write_collection_to(stream, thing, "")

def write_collection_to(stream, thing, indent, omit_indentation=False):
        if isinstance(thing, dict):
            for key, value  in thing.items():
                write_dict(stream, key, value, "" if omit_indentation else indent)
                omit_indentation = False

        elif isinstance(thing, list):
            for value in thing:
                write_list_element(stream, value, indent)

def write_dict(stream, key, value, indent):
    stringed = stringify(value)
    stream.write(indent + key + ": " + stringed + "\n")
    if stringed=="":
        write_collection_to(stream, value, indent + "    ")

def write_list_element(stream, value, indent):
    stringed = stringify(value)
    stream.write(indent[0:-2] + "- ")
    is_dictionary = stringed == ""

    if is_dictionary:
        write_collection_to(stream, value, indent, True)
    else:
        stream.write(stringed + "\n")
        write_collection_to(stream, value, indent + "    ")
def is_primitive(thing):
    return isinstance(thing, primitive)

def is_list_of_simple_types(thing):
    if not isinstance(thing, list):
        return False
    for i in thing:
        if not is_primitive(i):
            return False
    return True

def stringify(thing):
    if is_list_of_simple_types(thing):
        return str(thing)
    elif isinstance(thing, list) or isinstance(thing, dict):
        return ""
    elif isinstance(thing, mathutils.Vector):
        return "<"+str(thing.x)+", "+str(thing.y)+", "+str(thing.z)+", "+str(thing.w)+">"
    elif isinstance(thing, bool):
        return "yes" if thing else "no"
    else:
        return str(thing)

if __name__ == '__main__':

    object = {
        "Enable": True,
        "A": 10,
        "B": 20,
        "C": [12, 13],
        "Vec": mathutils.Vector((1,2,3,4)),
        "MultiModel": ["partA", "partB"],
        "D": [
            {"E": 16,
             "U": "sdf"},
            {"F": 20}
        ],
        "Tank": {
            "Turret": {
                "Position": mathutils.Vector((1,2,3,4)),
                "Power": 100
            },
            "Dupa": {
                "DupaDup": "asd",
                "table": [56,86,56]
            }
        }
    }
    stream = io.StringIO()
    write_yaml_to(stream, object)
    print(stream.getvalue())


    with open("example.yml", 'w') as fp:
        write_yaml_to(fp, object)
