import io
import mathutils
primitive = (int, str, bool, float)

def writeYamlTo(stream, thing):
    writeCollectionTo(stream, thing, "")

def writeCollectionTo(stream, thing, indent, omitIndentation=False):
        if isinstance(thing, dict):
            for key, value  in thing.items():
                writeDict(stream, key, value, "" if omitIndentation else indent)
                omitIndentation = False

        elif isinstance(thing, list):
            for value in thing:
                writeListElement(stream, value, indent)

def writeDict(stream, key, value, indent):
    stringed = stringify(value)
    stream.write(indent + key + ": " + stringed + "\n")
    if stringed=="":
        writeCollectionTo(stream, value, indent + "    ")

def writeListElement(stream, value, indent):
    stringed = stringify(value)
    stream.write(indent[0:-2] + "- ")
    isDictionary = stringed == ""

    if isDictionary:
        writeCollectionTo(stream, value, indent, True)
    else:
        stream.write(stringed + "\n")
        writeCollectionTo(stream, value, indent + "    ")

def isPrimitive(thing):
    return isinstance(thing, primitive)

def isListOfSympleTypes(thing):
    if not isinstance(thing, list):
        return False
    for i in thing:
        if not isPrimitive(i):
            return False
    return True

def strf(number):
    # return str("%.5f" %number)
    return str(round(number, 6))

def roundIfFloat(number):
    return round(number, 6) if isinstance(number, float) else number

def stringify(thing):
    if isListOfSympleTypes(thing):
        return str([roundIfFloat(x) for x in thing])
    elif isinstance(thing, list) or isinstance(thing, dict):
        return ""
    elif isinstance(thing, mathutils.Vector):
        return "<"+strf(thing.x)+", "+strf(thing.y)+", "+strf(thing.z)+">"
    elif isinstance(thing, bool):
        return "yes" if thing else "no"
    elif isinstance(thing, float):
        return strf(thing)
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
    writeYamlTo(stream, object)
    print(stream.getvalue())


    with open("example.yml", 'w') as fp:
        writeYamlTo(fp, object)
