
bl_info = {
		"name":         "Tank config",
		"author":       "DezerteR",
		"blender":      (2,6,7),
		"version":      (0,0,1),
		"location":     "File > Export > Tank config",
		"description":  "Export Tank config",
		"category":     "Import-Export"
}

import bpy
import mathutils
import string
from bpy_extras.io_utils import ExportHelper

g_ID = 0;
good_types = ['EMPTY', 'MESH']

def tstr (number):
	# return str(round(number, 6))
	return str("%.4f" %number)

def vectos (vec):
	str = tstr(vec.x)+' '+tstr(vec.y)+' '+tstr(vec.z)
	return str

def getConvex(object):
	out = []
	if hasattr(object, 'children'):
		for child in object.children:
			# if hasattr(child, 'Class') and child['Class'] == 'Convex':
			if 'Convex' in child.name:
				out.append(child)
				print(child.name)
	return out

def getEmptys(object):
	out = []
	if hasattr(object, 'children'):
		for child in object.children:
			if child.type == 'EMPTY':
				out.append(child)
	return out

def getAllChildren(object):
	out = []
	if hasattr(object, 'children'):
		for child in object.children:
			# if child.type == 'MESH' and hasattr(child, 'Class') and child['Class'] != 'Convex' and not child.hide:
			# if child.type == 'MESH' and hasattr(child, 'Class') and child['Class'] != 'Convex':
			if child.type == 'MESH' and 'Class' in child.keys() and child['Class'] != 'Convex':
				out.append(child)
				print('**Child:'+child.name)
	return out
def hasProp(obj, prop):
	return prop in obj.keys()
def vecToYAML(file, vec, offset):
		o = offset+' '
		file.write(o+'   - '+tstr(vec.x)+'\n')
		file.write(o+'   - '+tstr(vec.y)+'\n')
		file.write(o+'   - '+tstr(vec.z)+'\n')
def vecToYAMLinLine(file, vec):
		file.write('['+tstr(vec.x)+', '+tstr(vec.y)+', '+tstr(vec.z)+']\n')
def getChildByName(obj, name):
	for child in obj.children:
		if name in child.name:
			return child
	return False
def getVectTo(a, b):
	print(',,'+a.name+'   ' +b.name)
	# return a.location -b.location
	Pa = a.matrix_world*mathutils.Vector((0.0, 0.0, 0.0, 1.0))
	Pb = b.matrix_world*mathutils.Vector((0.0, 0.0, 0.0, 1.0))
	return Pb - Pa

def nameToID(name):
	# line = name.translate(str.maketrans(None, '-_. '))
	line = name.translate({ord(i):None for i in '!@#$ .-_'})
	return line.upper()


def writeProperties(file, obj, offset):
	for K in obj.keys():
		if K not in '_RNA_UI':
			file.write(offset+K+': ')
			file.write('%s \n' % obj[K])

def initialWriteModuleProperties(file, obj, offs):
	file.write(' - Name: '+nameToID(obj.name)+'\n')
	file.write('   Model: '+obj.name+'\n')
	file.write('   Pivot: [0.0, 0.0, 0.0]\n')

	file.write(offs+'   Dimensions: ')
	vecToYAMLinLine(file, obj.dimensions)

	offset = offs+'   '

	emptys = getEmptys(obj)
	convexs = getConvex(obj)
	children = getAllChildren(obj)

	writeProperties(file, obj, offset)

	# convex: [conv1, cnv2, oqrgkp, ]
	if len(convexs) > 0:
		file.write(offset+'Convex: \n')
		for convex in convexs:
			file.write(offset+' - '+ convex.name+'\n')


	joints = getEmptys(obj)
	if len(joints) > 0:
		file.write(offset+'Slots:\n')
		offset = offset + ' '

		for slot in joints:
			file.write(offset+slot.name+':\n')
			file.write(offset+' Pivot: ')
			pivot = getVectTo(obj, slot)
			vecToYAMLinLine(file, pivot)

			file.write(offset+' Axis: ')
			axis = slot.matrix_local*mathutils.Vector((0.0, 0.0, 1.0, 0.0))
			vecToYAMLinLine(file, axis)

			if hasProp(slot, 'min'):
				file.write(offset+' min: '+slot['min']+'\n')
				file.write(offset+' max: '+slot['max']+'\n')
			else:
				file.write(offset+' min: 0\n')
				file.write(offset+' max: 0\n')
			file.write(offset+' children:\n')
			for jointed in slot.children:
				# if not jointed.hide:
					writeModuleProperties(file, jointed, slot, offset+' ',False)

# wycign lokalne pooenie jointa wzgldem childa, jest to uzyskiwalne
def writeModuleProperties(file, obj, parentJoint, offs, boool):
	offset = offs+'   '
	print(offs+obj.name)
	file.write(offs+' - Name: '+nameToID(obj.name)+'\n')
	file.write(offs+'   Model: '+obj.name+'\n')

	file.write(offs+'   Dimensions: ')
	vecToYAMLinLine(file, obj.dimensions)


	convexs = getConvex(obj)
	children = getAllChildren(obj)

	writeProperties(file, obj, offset)

		# lokalna pozycja jointa wzgldem dziecka
	file.write(offset+'Pivot: ')

	if getChildByName(obj, 'In') != False:
		pivot = getVectTo( getChildByName(obj, 'In'), obj)
		# pivot = obj.location
	else :
		pivot = getVectTo( parentJoint, obj)
		# pivot = obj.location

	vecToYAMLinLine(file, pivot)

	if len(convexs) > 0:
		file.write(offset+'Convex: \n')
		for convex in convexs:
			file.write(offset+' - '+ convex.name+'\n')

	# 1. wycigamy kolekcj widocznych jointw
	emptys = getEmptys(obj)
	joints = []
	addons = []
	spec = []
	jchildren = []
	for j in emptys:
		if j['Class'] == 'joint' and 'Slot' in j.name:
			joints.append(j)
		elif j['Class'] == 'joint':
			jchildren.append(j)
		else:
			spec.append(j)

	#1.5 wypisujemy dodatki podpiete do danego moduu (te przyczepione na sztywno, np.)
	# if len(addons) > 0:
		# file.
	if len(spec) > 0:
		file.write(offset+'Special:\n')
		for s in spec:
			print(offs+s.name)
			file.write(offset+'  '+s['name']+':\n');
			axis = s.matrix_local*mathutils.Vector((0.0, 0.0, 1.0, 0.0))
			pivot = getVectTo(parentJoint,s);
			file.write(offset+'    pivot: ')
			vecToYAMLinLine(file, pivot)
			file.write(offset+'    axis: ')
			vecToYAMLinLine(file, axis)
	# 2. iterujemy po tym co wycignlimy (po jointach)
	if len(jchildren) > 0:
		# file.write(offset+'children:\n')
		for joint in jchildren:
			file.write(offset+joint.name+':\n')
			for child in joint.children:
				writeModuleProperties(file, child, joint, offset+' ',False)

	if len(joints) > 0:
		file.write(offset+'Slots:\n')
		offset = offset + '  '

		for slot in joints:
		# 3. iterujemy po widocznych dzieciach jointa i na kaym robimy writeModuleProperties(file, child, joint, offset)
			# file.write(offset+'Joint:\n')
			file.write(offset+slot.name+':\n')
			file.write(offset+' Pivot: ')
			pivot = getVectTo(obj, slot)
			vecToYAMLinLine(file, pivot)

			file.write(offset+' Axis: ')
			axis = slot.matrix_local*mathutils.Vector((0.0, 0.0, 1.0, 0.0))
			vecToYAMLinLine(file, axis)

			if hasProp(slot, 'min'):
				file.write(offset+' min: '+slot['min']+'\n')
				file.write(offset+' max: '+slot['max']+'\n')
			else:
				file.write(offset+' min: 0\n')
				file.write(offset+' max: 0\n')
			file.write(offset+' children:\n')
			for jointed in slot.children:
				# if not jointed.hide:
					writeModuleProperties(file, jointed, slot, offset+' ',False)

	if len(joints) < 1 and len(children) > 0:
		file.write(offset+'children:\n')
	if len(children) > 0:
		for child in children:
			writeModuleProperties(file, child, obj, offset, True)

def writeSuspension(file, suspension):
	# suspension:
		# tracks: [trackleft, trackright]
		# wheels: z zachowaniem porzdku left side, right side
			# - name: wh1
				# pivotPoint: [235 2345 35]
		# addons: []
	file.write('Suspension:\n')
	file.write(' FreeWheels:\n')
	EFreeWheels = getChildByName(suspension, 'EFreeWheels')
	for wheel in EFreeWheels.children:
		file.write(' - Name: '+wheel.name+'\n')
		file.write('   Pivot: ')
		# pivot = getChildByName(wheel, 'Empty').matrix_world*mathutils.Vector((0.0, 0.0, 0.0, 1.0))
		pivot = wheel.location
		vecToYAMLinLine(file, pivot)

	file.write(' Wheels:\n')
	EWheels = getChildByName(suspension, 'EWheels')
	for wheel in EWheels.children:
		file.write(' - Name: '+wheel.name+'\n')
		file.write('   Pivot: ')
		pivot = wheel.location
		vecToYAMLinLine(file, pivot)

	file.write(' Tracks:\n')
	ETrack = getChildByName(suspension, 'ETrack')
	for track in ETrack.children:
		file.write(' - Name: '+track.children[0].name+'\n')

	file.write(' Springs:\n')
	ESprings = getChildByName(suspension, 'ESprings')
	for spring in ESprings.children:
		file.write(' - Name: '+spring.children[0].name+'\n')
def do_exports(context, filepath):
	file = open(filepath, "w", encoding='utf8')

	file.write('Model:\n')
	offset = ''
	initialWriteModuleProperties(file, bpy.data.objects['Hull'], offset)

	file.close()
class ExportMyFormat(bpy.types.Operator, ExportHelper):
	bl_idname       = "tank_config.yml";
	bl_label        = "Tank config exporter";
	bl_options      = {'PRESET'};

	filename_ext    = ".yml";

	def execute(self, context):
		do_exports(context, self.filepath)
		return {'FINISHED'};
def menu_func(self, context):
	self.layout.operator(ExportMyFormat.bl_idname, text="Tank config(.yml)");
def register():
	bpy.utils.register_module(__name__);
	bpy.types.INFO_MT_file_export.append(menu_func);
def unregister():
	bpy.utils.unregister_module(__name__);
	bpy.types.INFO_MT_file_export.remove(menu_func);
if __name__ == "__main__":
	register()
