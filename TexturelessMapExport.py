
bl_info = {
        "name":         "Texless map exporter",
        "author":       "Karol Wajs",
        "blender":      (2,7,6),
        "version":      (0,0,1),
        "location":     "File > Export > Texless map",
        "description":  "Export scene texless map",
        "category":     "Import-Export"
}

import bpy
import mathutils
from mathutils import Vector
import math
import string
import os
import numpy
from bpy_extras.io_utils import ExportHelper

def tstr(number):
    # return str(round(number, 6))
    return str("%.4f" %number)

def vecToString(vec):
    str = '['+tstr(vec.x)+', '+tstr(vec.y)+', '+tstr(vec.z)+']'
    return str

def getVectTo(a, b):
    Pa = a.matrix_world*mathutils.Vector((0.0, 0.0, 0.0, 1.0))
    Pb = b.matrix_world*mathutils.Vector((0.0, 0.0, 0.0, 1.0))
    return Pb - Pa

def writeQuaternion(file, object, offset):
	# quat = object.rotation_euler.to_quaternion()
	object.rotation_mode = 'QUATERNION'
	quat = object.rotation_quaternion
	str = '['+tstr(quat[0])+', '+tstr(quat[1])+', '+tstr(quat[2])+', '+tstr(quat[3])+']'
	file.write(offset + 'Quaternion: ' + str)
	return quat

#---------------------

def scene_bounds():
    meshes = [o for o in bpy.data.objects if o.scene.objectType == 'TerrainChunk']

    minV = Vector((min([min([co[0] for co in m.bound_box]) + m.location[0] for m in meshes]),
                   min([min([co[1] for co in m.bound_box]) + m.location[1] for m in meshes]),
                   min([min([co[2] for co in m.bound_box]) + m.location[2] for m in meshes])))

    maxV = Vector((max([max([co[0] for co in m.bound_box]) + m.location[0] for m in meshes]),
                   max([max([co[1] for co in m.bound_box]) + m.location[1] for m in meshes]),
                   max([max([co[2] for co in m.bound_box]) + m.location[2] for m in meshes])))

    return minV, maxV

def saveMapDescription(file):
    minV, maxV = scene_bounds()


    file.write("\n    Max: " + vecToString(maxV))
    file.write("\n    Min: " + vecToString(minV))
    file.write("\n    Chunks:")
    for chunk in bpy.data.objects:
        if not chunk.scene.objectType == "TerrainChunk":
            continue

        file.write("\n      - Name: " + chunk.name)
        file.write("\n        Mesh: " + chunk.data.name)
        file.write("\n        Position: " + vecToString(chunk.location))
        file.write("\n        Dimension: " + vecToString(chunk.dimensions))
        file.write("\n        isCollider: " + str(chunk.scene.is_collider))

def saveMapCollider(file):
    file.write("\n    Collider:")
    for obj in bpy.data.objects:
        if obj.scene.objectType == "TerrainCollider":
            file.write(" " + obj.data.name)
            return

def saveObjects(file, s):
    for obj in bpy.data.objects:
        if obj.scene.objectType == "Model":
            saveObject(obj, file, s)

def saveObject(obj, file, s):
    file.write(s + "- Name: " + obj.name)
    file.write(s + "  Mesh: " + obj.data.name)
    file.write(s + "  Position: " + vecToString(obj.location))
    writeQuaternion(file, obj, s+"  ")
    file.write(s + "  Dimension: " + vecToString(obj.dimensions))
    file.write(s + "  isCollider: " + str(obj.scene.is_collider))
    if obj.scene.is_collider:
        file.write(s + "  Colliders: ")
        for child in obj.children:
            file.write(s + "    - Mesh: " + child.data.name)


#---------------------
class ExportMyFormat(bpy.types.Operator, ExportHelper):
    bl_idname       = "map.yml";
    bl_label        = "Texless map exporter";
    bl_options      = {'PRESET'};

    filename_ext    = ".yml";

    def execute(self, context):
        print("\n--------------------------------------------------------\n")
        filepath = os.path.dirname(self.filepath)

        file = open(filepath+"\map.yml", "w", encoding='utf8')
        file.write("Terrain:")
        saveMapCollider(file)
        saveMapDescription(file)
        file.write("\nObjects:")
        saveObjects(file, "\n    ")
        file.close()

        # save whole file to collada

        return {'FINISHED'};

def menu_func(self, context):
    self.layout.operator(ExportMyFormat.bl_idname, text="Texless Map (.yml)");
def register():
    bpy.utils.register_module(__name__);
    bpy.types.INFO_MT_file_export.append(menu_func);
def unregister():
    bpy.utils.unregister_module(__name__);
    bpy.types.INFO_MT_file_export.remove(menu_func);
if __name__ == "__main__":
    register()
