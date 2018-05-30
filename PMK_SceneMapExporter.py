
bl_info = {
		"name":         "PMK Scene Map exporter",
		"author":       "Karol Wajs",
		"blender":      (2,7,5),
		"version":      (0,0,1),
		"location":     "File > Export > PMK Scene Map exporter",
		"description":  "Export scene map for Po-Male-Ka",
		"category":     "Import-Export"
}

import bpy
import mathutils
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

def saveMapDescription(file, obj):
	file.write("MetricalSize: " + vecToString(obj.dimensions))

	no_in_line = math.sqrt(len(obj.data.vertices))
	file.write("\nSize: " + tstr(no_in_line))

	min_co = getMin(obj)
	file.write("\nMinZ: " + tstr(min_co[2]))

	max_co = getMax(obj)
	file.write("\nMaxZ: " + tstr(max_co[2]))

def getMin(obj):
	x = min(x[0] for x in obj.bound_box)
	y = min(x[1] for x in obj.bound_box)
	z = min(x[2] for x in obj.bound_box)
	return mathutils.Vector((x, y, z))

def getMax(obj):
	x = max(x[0] for x in obj.bound_box)
	y = max(x[1] for x in obj.bound_box)
	z = max(x[2] for x in obj.bound_box)
	return mathutils.Vector((x, y, z))

def getOffset(obj):
	min_co = getMin(obj)
	max_co = getMax(obj)
	max_co[2] = 0
	return -min_co

def getScale(obj):
	dim = mathutils.Vector(obj.dimensions)
	side_dim = math.sqrt(len(obj.data.vertices))-1
	dim[0] = side_dim/dim[0]
	dim[1] = side_dim/dim[1]
	dim[2] = 1
	return dim

def saveMapData(filename, selected):
	offset = getOffset(selected)
	scale = getScale(selected)
	no_in_line = math.sqrt(len(selected.data.vertices))

	print("scale:", scale)
	print("offset:", offset)
	print("no_in_line:", no_in_line)

	data_array = numpy.empty(len(selected.data.vertices), dtype=numpy.float32)
	count = 0
	for v in selected.data.vertices:
		co = v.co + offset
		co[0] *= scale[0]
		co[1] *= scale[1]
		data_array[math.ceil(co.x-0.45) + math.ceil(co.y-0.45)*no_in_line] = co.z
		count += 1
	print("written vertices: ", count)
	print("written vertices(len): ", len(data_array))
	data_array.tofile(filename)


#---------------------
class ExportMyFormat(bpy.types.Operator, ExportHelper):
	bl_idname       = "map.yml";
	bl_label        = "PMK Scene Map exporter";
	bl_options      = {'PRESET'};

	filename_ext    = ".yml";

	def execute(self, context):
		print("\n--------------------------------------------------------\n")
		filepath = os.path.dirname(self.filepath)

		file = open(filepath+"\map.yml", "w", encoding='utf8')
		saveMapDescription(file, bpy.context.object)
		file.close()

		saveMapData(filepath+"\map.bin", bpy.context.object)

		return {'FINISHED'};

def menu_func(self, context):
	self.layout.operator(ExportMyFormat.bl_idname, text="PMK Scene Map (.yml)");
def register():
	bpy.utils.register_module(__name__);
	bpy.types.INFO_MT_file_export.append(menu_func);
def unregister():
	bpy.utils.unregister_module(__name__);
	bpy.types.INFO_MT_file_export.remove(menu_func);
if __name__ == "__main__":
	register()
