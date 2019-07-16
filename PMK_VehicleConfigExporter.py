
bl_info = {
    'name':         'PMK Vehicle File Exporter',
    'author':       'Karol Wajs',
    'blender':      (2,80,0),
    'version':      (0,2,2),
    'location':     'config > Export > Vehicle File',
    'description':  'Export Vehicle',
    'category':     'Import-Export'
}

import bpy, mathutils, math
import string, os
from collections import OrderedDict
import SimpleYaml
from bpy_extras.io_utils import ExportHelper
import json

def vecFromTo(a, b):
    return b.location - a.location
def objUpAxis(thing):
    axis = thing.matrix_local*mathutils.Vector((0.0, 0.0, 1.0, 0.0))
    axis.normalize()
    return axis

vecRight = mathutils.Vector((1.0, 0.0, 0.0, 0.0))
vecUp = mathutils.Vector((0.0, 0.0, 1.0, 0.0))
vecForward = mathutils.Vector((0.0, 1.0, 0.0, 0.0))
zeroPosition = mathutils.Vector((0.0, 0.0, 0.0, 1.0))

def setPosition(thing, data):
    m = thing.matrix_world
    data['X'] = mathutils.Vector(( m[0][0], m[1][0], m[2][0], 0))
    data['Y'] = mathutils.Vector(( m[0][1], m[1][1], m[2][1], 0))
    data['Z'] = mathutils.Vector(( m[0][2], m[1][2], m[2][2], 0))
    data['W'] = mathutils.Vector(( m[0][3], m[1][3], m[2][3], 1))

def compareVectors(a, b):
    return math.isclose(a.x, b.x) and math.isclose(a.y, b.y) and math.isclose(a.z, b.z)

class ExportVehicle(bpy.types.Operator, ExportHelper):
    bl_idname       = 'vehicle_info.yaml'
    bl_label        = 'Vehicle Exporter'
    bl_options      = {'PRESET'}
    filename_ext    = '.yml'

    def execute(self, context):
        root = self.findRoot(bpy.data.objects)
        config = OrderedDict()
        config['Modules'] = []
        self.collectModules(config['Modules'], bpy.data.objects)

        config['Cameras'] = self.getCameras(bpy.data.objects)
        config['LightSources'] = self.getLights(bpy.data.lights)
        config['Materials'] = self.getMaterials(bpy.data.materials)

        with open(self.filepath, 'w') as fp:
            fp.write('# created with blender 2.8, script revision: ' + str(bl_info['version']) + ' simplified version' + '\n')
            SimpleYaml.writeYamlTo(fp, config)

        path = os.path.dirname(self.filepath)
        name = os.path.splitext(os.path.split(self.filepath)[1])[0]

        # with open(os.path.join(path, name+'.json'), 'w') as fp:
        #     json.dump(config, fp, indent=4, sort_keys=True)

        bpy.ops.wm.collada_export(
            filepath = os.path.join(path, name+'.dae'),
            check_existing = False,
            apply_modifiers = True,
            triangulate = True,
            use_object_instantiation = False
        )

        return {'FINISHED'}

    def collectModules(self, outputList, collection):
        for x in collection:
            if x.type == 'MESH' and x.pmk.moduleProps.objectType == 'Module':
                outputList.append(self.getModule(x))


    def findRoot(self, objects):
        for obj in objects:
            if obj.pmk.moduleProps.objectType == 'Base':
                return obj

    def getModule(self, thing):
        output = OrderedDict()
        output['Name'] = thing.name
        output['Type'] = str(thing.pmk.moduleProps.objectType)
        output['Class'] = str(thing.pmk.moduleProps.moduleClass)
        output['ArmorClass'] = str(thing.pmk.moduleProps.armorClass)
        output['Active'] = thing.pmk.moduleProps.isActive
        output['Servo'] = thing.pmk.moduleProps.hasServo
        output['Identifier'] = thing.pmk.identifier
        if thing.pmk.moduleProps.objectType == 'Suspension':
            self.writeSuspensionProperties(config, thing)
        if thing.data is not None:
            output['Models'] = self.getMeshes(thing)

        self.appendDecals(output, thing)
        self.appendMarkers(output, thing)
        self.appendPhysical(output, thing)

        self.appendConstraints(output, thing)
        childrenByPosition = self.groupChildrenByPosition(thing)
        if len(childrenByPosition) > 0:
            output['Attached'] = childrenByPosition


        return output

    def putIntoList(self, listOfSlots, thing, thingPosition):
        for x in listOfSlots:
            if compareVectors(x['Position'], thingPosition):
                x['Attached'].append(thing.name)
                return

        listOfSlots.append({'Attached' : [thing.name], 'Position': thingPosition})

    def groupChildrenByPosition(self, thing):
        listOfSlots = []
        for child in thing.children:
            if child.type == 'MESH' and child.pmk.moduleProps.objectType == 'Module':
                self.putIntoList(listOfSlots, child, vecFromTo(thing, child))
        return listOfSlots


    # * find all meshes with type{Module, Part} directly connected to object, they have to be merged in one in engine
    def getMeshes(self, thing):
        # // out = [thing.data.name] 'cos using object names, not mesh names
        out = [thing.name]
        for child in thing.children:
            if child.pmk.moduleProps.objectType == 'Part' and child.data is not None:
                # // out.append(child.data.name) 'cos using object names, not mesh names
                out.append(child.name)
        return out

    def appendPhysical(self, config, thing):
        if thing.rigid_body is None: return

        config['Physical'] = {}
        config['Physical']['Mass'] = thing.rigid_body.mass
        models = self.findPhysicalModels(thing)
        if len(models) > 0 :config['Physical']['CollisionModels'] = models
        # TODO: add bounding box

    def findPhysicalModels(self, thing):
        out = []
        for c in thing.children:
            if c.pmk.moduleProps.objectType == 'Collider':
                # // out.append(c.data.name) 'cos using object names, not mesh names
                out.append(c.name)
        return out

    def getJoints(self, thing):
        out = []
        for child in thing.children:
            if child.pmk.emptyProps.objectType == 'Joint':
                out.append(child)
        return out

    def appendJoints(self, config, thing):
        joints = self.getJoints(thing)
        if len(joints) > 0:
            config['Joints'] = []
            for slot in joints:
                config['Joints'].append(self.getJointProps(slot, thing))

    # * I didn't found usage for linear constraints
    # * lack of limits means that connection is rigid
    def appendConstraints(self, output, thing):
        if not 'Limit Rotation' in thing.constraints:
            return

        c = thing.constraints['Limit Rotation']

        output['Limits'] = [True if c.use_limit_x else False,
                            True if c.use_limit_y else False,
                            True if c.use_limit_z else False, ]
        output['Min'] = [c.min_x, c.min_y, c.min_z]
        output['Max'] = [c.max_x, c.max_y, c.max_z]

    # * axis of rotation is coded in slot Z axis
    # * constraints in object constraints
    def getJointProps(self, slot, parentThing):
        out = OrderedDict()
        out['Name'] = slot.name
        out['Type'] = slot.pmk.emptyProps.jointType
        out['MainAxis'] = slot.pmk.emptyProps.mainAxis
        m = slot.matrix_local
        # * need to get axes of local coordinates
        out['X'] = mathutils.Vector(( m[0][0], m[1][0], m[2][0] ))
        out['Y'] = mathutils.Vector(( m[0][1], m[1][1], m[2][1] ))
        out['Z'] = mathutils.Vector(( m[0][2], m[1][2], m[2][2] ))
        out['W'] = mathutils.Vector(( m[0][3], m[1][3], m[2][3] ))

        if len(slot.children) > 0:
            constraintAxis = mathutils.Vector()
            out['Pinned'] = []
            for pinned in slot.children:
                out['Pinned'].append(pinned.name)

        return out

    def getMaterialParam(self, inputs, name):
        input = inputs[name]
        if input.type == 'VALUE':
            return input.default_value
        elif input.type == 'RGBA':
            tmp = input.default_value
            return mathutils.Vector((tmp[0], tmp[1], tmp[2], tmp[3]))
        else:
            return 'invalid material type: ' + input.type

    def getMaterials(self, materials):
        out = {}
        for mat in materials:
            if not mat.node_tree.nodes['Principled BSDF']:
                print('Unknown material type! Fix it!')
                break

            bsdf = mat.node_tree.nodes['Principled BSDF'].inputs

            out[mat.name.replace('.', '_') + '-material'] = {
                'BaseColor': self.getMaterialParam(bsdf, 'Base Color'),
                'Metallic': self.getMaterialParam(bsdf, 'Metallic'),
                'Specular': self.getMaterialParam(bsdf, 'Specular'),
                'Roughness': self.getMaterialParam(bsdf, 'Roughness'),
                'Anisotropic': self.getMaterialParam(bsdf, 'Anisotropic'),
                'AnisotropicRotation': self.getMaterialParam(bsdf, 'Anisotropic Rotation'),
                'Clearcoat': self.getMaterialParam(bsdf, 'Clearcoat'),
                'IOR': self.getMaterialParam(bsdf, 'IOR'),
                'Emissive': 0
            }
        return out

    def getCameras(selft, objectList):
        out = []
        for obj in objectList:
            if obj.type == 'CAMERA' and obj.parent:
                camera = obj.data
                data = OrderedDict()
                data['Name'] = obj.name
                data['Mode'] = obj.pmk.cameraProps.mode
                data['Inertia'] = obj.pmk.cameraProps.inertia
                data['Offset'] = obj.pmk.cameraProps.offset
                data['CameraType'] = camera.type
                data['Angle'] = camera.angle
                copyPosition(obj, data)

                data['Parent'] = obj.parent.name
                data['FromParentToOrigin'] = vecFromTo(obj.parent, obj)

                out.append(data)

        return out

    def getLights(self, objects):
        out = []
        for lamp in objects:
            if lamp.parent:
                data = OrderedDict()

                data['Name'] = lamp.name

                lampObject = bpy.data.objects[lamp.name]

                data['Parent'] = obj.parent.name
                data['FromParentToOrigin'] = vecFromTo(obj.parent, obj)

                copyPosition(lampObject, data)
                data['Color'] = mathutils.Vector(( lamp.color[0], lamp.color[1], lamp.color[2] ))

                data['Power'] = lamp.energy
                data['Type'] = lamp.type
                data['Shadows'] = lamp.use_shadow
                data['Specular'] = lamp.specular_factor

                if lamp.type == 'POINT':
                    data['Radius'] = lamp.shadow_soft_size
                    data['CustomDistance'] = lamp.cutoff_distance if lamp.use_custom_distance else 'none'

                elif lamp.type == 'SUN':
                    data['Radius'] = lamp.shadow_soft_size

                elif lamp.type == 'SPOT':
                    data['SpotSize'] = lamp.spot_size
                    data['Blend'] = lamp.spot_blend
                    data['Radius'] = lamp.shadow_soft_size
                    data['CustomDistance'] = lamp.cutoff_distance if lamp.use_custom_distance else 'none'

                elif lamp.type == 'AREA':
                    data['Size'] = lamp.size
                    data['Shape'] = lamp.shape
                    data['CustomDistance'] = lamp.cutoff_distance if lamp.use_custom_distance else 'none'


                out.append(data)
        return out

    # * first left side, from begining
    def get_connection(self, thing, to_origin):
        res = OrderedDict()
        res['toOrigin'] = to_origin
        res['MaxV'] = 15
        res['Limits'] = [-15, 15]

        return res
    def sort_wheels(self, wheels):
        return sorted(wheels, key = lambda x: (-x.location.y, x.location.x))
    def get_type(self, thing, type):
        out = []
        for child in thing.children:
            if child.pmk.moduleProps.moduleType == type:
                out.append(child)
        return self.sort_wheels(out)
    def writeSuspensionProperties(self, config, thing):
        road_wheels = self.get_type(thing, 'RoadWheel')
        support_wheels = self.get_type(thing, 'SupportWheel')
        drive_sprocket = self.get_type(thing, 'DriveSprocket')
        idler_wheel = self.get_type(thing, 'IdlerWheel')

        config['ShoeMesh'] = thing.pmk.moduleProps.shoe_mesh
        config['toOrigin'] = vec_to_str_1(thing.location)
        config['Stiffness'] = 10 #thing.pmk.stiffness
        config['Damping'] = 1 #thing.pmk.damping
        config['Compression'] = 1 #thing.pmk.compression
        config['MaxTravel'] = 0.5 #thing.pmk.max_travel

        config['RoadWheels'] = []
        for it in road_wheels:
            config['RoadWheels'].append({
                'Name'      : it.name,
                'Axis'      : it.matrix_world*vecRight,
                'Dimension' : it.dimensions,
                'Position'  : it.location
            })
        config['SupportWheels'] = []
        for it in road_wheels:
            config['SupportWheels'].append({
                'Name'      : it.name,
                'Axis'      : it.matrix_world*vecRight,
                'Dimension' : it.dimensions,
                'Position'  : it.location
            })
        config['DriveSprocket'] = []
        for it in road_wheels:
            config['DriveSprocket'].append({
                'Name'      : it.name,
                'Axis'      : it.matrix_world*vecRight,
                'Dimension' : it.dimensions,
                'Position'  : it.location
            })
        config['IdlerWheel'] = []
        for it in road_wheels:
            config['IdlerWheel'].append({
                'Name'      : it.name,
                'Axis'      : it.matrix_world*vecRight,
                'Dimension' : it.dimensions,
                'Position'  : it.location
            })

    def appendDecals(self, config, thing):
        decals = []
        for child in thing.children:
            if child.pmk.emptyProps.objectType == 'Decal':
                decals.append(child);
        if len(decals) == 0:
            return

        config['Decals'] = []
        for decal in decals:
            locx = decal.matrix_local*vecRight
            locx.normalize()
            locz = decal.matrix_local*vecUp
            locz.normalize()
            config['Decals'].append({
                'Layer'     : decal.pmk.decalProps.decalName,
                'Scale'     : decal.scale,
                'Position'  : vecFromTo(decal, thing),
                'LocX'      : locx,
                'LocZ'      : loc
            })

    def appendMarkers(self, config, thing):
        markers = []
        for child in thing.children:
            if child.pmk.emptyProps.objectType == 'Marker':
                markers.append(child);
        if len(markers) == 0:
            return

        config['Markers'] = []
        for marker in markers:
            m = OrderedDict()
            loc = marker.matrix_local
            m['Type'] = marker.pmk.emptyProps.markerType
            setPosition(marker, m)

            # if 'Camera' == marker.pmk.emptyProps.markerType:
            #     m['Mode'] = marker.pmk.cameraProps.mode
            #     m['Offset'] = mathutils.Vector((marker.pmk.cameraProps.offset[0], marker.pmk.cameraProps.offset[1], marker.pmk.cameraProps.offset[2]))
            #     m['Inertia'] = marker.pmk.cameraProps.inertia
            #     camera = marker.data
            #     m['CameraType'] = camera.type
            #     m['Angle'] = camera.angle

            config['Markers'].append(m)

def menu_func(self, context):
    self.layout.operator(ExportVehicle.bl_idname, text='PMK Vehicle (.yml)')

def register():
    bpy.utils.register_class(ExportVehicle)
    bpy.types.TOPBAR_MT_file_export.append(menu_func)

def unregister():
    bpy.types.TOPBAR_MT_file_export.remove(menu_func)
    bpy.utils.unregister_class(ExportVehicle)

if __name__ == '__main__':
    register()
