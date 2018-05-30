import io, numbers
def write_yaml_to(stream, object):
    write_collection_to(stream, object, "")

def write_collection_to(stream, object, indent="", as_array_element=False):
        if isinstance(object, dict):
            for key, value  in object.items():
                write_to(stream, value, key, indent, as_array_element)
                as_array_element = False
        elif isinstance(object, list):
            for value  in object:
                write_to(stream, value, "", indent, as_array_element)
                as_array_element = False

def write_to(stream, object, key, indent="", as_array_element=False):
    (value, is_array, is_dict) = stringify(object)

    if key == "":
        stream.write(indent[0:-2] + "- ")
        if value != "":
            stream.write(value + "\n")
        else:
            write_collection_to(stream, object, indent, True)


    else:
        stream.write((indent if not as_array_element else "" )+ key + ": " + value + "\n")
        if is_array and value == "":
            write_collection_to(stream, object, indent + "  ")


def stringify(object):
    if isinstance(object, dict):
        return "", False, True
    elif isinstance(object, list):
        if all(isinstance(x, numbers.Number) for x in object):
            return str(object), False, False
        else:
            return "", True, True
    else:
        return str(object), False, False

if __name__ == '__main__':

    object = {
        "A": 10,
        "B": 20,
        "C": [12, 13, 1289.0],
        "D": [
            {"E": 16,
             "U": "sdf"},
            {"F": 20}
        ],
        "Arr": [[{"1": 2}, {"5": 6}], [{"3": 4}]]
    }
    ''' Array of arrays, dopilnować żeby to też znalazło się w parserze, jak na to zareaguje importer?
            -
              - a
              - b
              - c
            -
              - d
              - e
              - f
            -
              - g
              - h
              - i

        Wygląda że zareagował trochę chujowo, nie rozpoznał zagniezdżonej tablicy, rozpoznawanie typów jest bardzo słabe
              '''
    # i jeszcze array of arrays "Arr": [[1,2], [3,4]]
    stream = io.StringIO()
    write_yaml_to(stream, object)
    print(stream.getvalue())
