
bl_info = {
        'name':         'PMK Scene exporter',
        'author':       'Karol Wajs',
        'blender':      (2,80,0),
        'version':      (0,1,1),
        'location':     'File > Export > PMK Scene exporter',
        'description':  'Export scene for Po-Male-Ka',
        'category':     'Import-Export'
}

import bpy
import mathutils
import string
import os
from bpy_extras.io_utils import ExportHelper
from collections import OrderedDict
import SimpleYaml

def copyPosition(thing, data):
    m = thing.matrix_world
    data['Position'] = OrderedDict()
    data['Position']['X'] = mathutils.Vector(( m[0][0], m[1][0], m[2][0], 0))
    data['Position']['Y'] = mathutils.Vector(( m[0][1], m[1][1], m[2][1], 0))
    data['Position']['Z'] = mathutils.Vector(( m[0][2], m[1][2], m[2][2], 0))
    data['Position']['W'] = mathutils.Vector(( m[0][3], m[1][3], m[2][3], 1))


class ExportScene(bpy.types.Operator, ExportHelper):
    bl_idname       = 'pmkscene.yml';
    bl_label        = 'PMK Scene exporter';
    bl_options      = {'PRESET'};

    filename_ext    = '.yml';

    def execute(self, context):
        config = OrderedDict()
        config['Materials'] = self.getMaterials(bpy.data.materials)
        config['Markers'] = self.getMarkers(bpy.data.objects)
        config['Cameras'] = self.getCameras(bpy.data.objects)
        config['Objects'] = self.getObjects(bpy.data.objects)
        ls = self.getLights(bpy.data.lights)
        if len(ls) > 0:
            config['LightSources'] = ls



        with open(self.filepath, 'w') as fp:
            fp.write('# created with blender 2.8, script revision: ' + str(bl_info['version']) + '\n')
            SimpleYaml.writeYamlTo(fp, config)

        path = os.path.dirname(self.filepath)
        name = os.path.splitext(os.path.split(self.filepath)[1])[0]

        bpy.ops.wm.collada_export(
            filepath = os.path.join(path, name+'.dae'),
            check_existing = False,
            apply_modifiers = True,
            triangulate = True,
            use_object_instantiation = False
        )
        return {'FINISHED'};

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

    def getMarkers(self, objectList):
        out = []
        for obj in objectList:
            if obj.type == 'EMPTY' and obj.pmk.emptyProps.objectType == 'Marker':
                data = OrderedDict()
                data['Name'] = obj.name
                data['Type'] = obj.pmk.emptyProps.markerType
                copyPosition(obj, data)

                out.append(data)
        return out;

    def getCameras(selft, objectList):
        out = []
        for obj in objectList:
            if obj.type == 'CAMERA':
                camera = obj.data
                data = OrderedDict()
                data['Name'] = obj.name
                data['Mode'] = obj.pmk.cameraProps.mode
                data['Inertia'] = obj.pmk.cameraProps.inertia
                data['Offset'] = obj.pmk.cameraProps.offset
                data['CameraType'] = camera.type
                data['Angle'] = camera.angle
                copyPosition(obj, data)

                out.append(data)

        return out

    def getObjects(self, objectList):
        out = OrderedDict()
        out['Regular'] = []
        out['RegularSubPart'] = []
        out['Terrain'] = []
        for obj in objectList:
            self.appendObject(obj, out)

        return out

    def appendObject(self, thing, inout):
        if thing.type != 'MESH': # colliders are not exported this way
            return

        data = OrderedDict()
        data['Name'] = thing.name

        copyPosition(thing, data)
        data['Dimensions'] = thing.dimensions
        # data['Texture'] = self.getTexture(thing)
        if thing.data is not None:
            data['Models'] = self.getMeshes(thing)
        data['isPhysical'] = thing.rigid_body is not None
        if thing.rigid_body is not None:
            data['Mass'] = thing.rigid_body.mass if thing.rigid_body.collision_shape != 'MESH' else 0
            data['Shape'] = thing.rigid_body.collision_shape
            data['Colliders'] = self.findPhysicalModels(thing)
            # todo: uzupełnić collidery na różne typy kolizyjne: box, sphere, *convex*, trimesh
            # todo: można by też z defaultu generować convexhulle albo dodać taki operator do pmk modelu: zainicjalzuj część fizyczną

        inout[thing.pmk.sceneObjectProps.objectType].append(data)

    def getMeshes(self, thing):
        # out = [thing.data.name] 'cos using object names, not mesh names
        out = [thing.name]
        for child in thing.children:
            if child.pmk.sceneObjectProps.objectType == 'RegularSubPart' and child.data is not None and child.type == 'MESH':
                # out.append(child.data.name) 'cos using object names, not mesh names
                out.append(child.name)
        return out

    def findPhysicalModels(self, thing):
        out = []
        for c in thing.children:
            if c.pmk.sceneObjectProps.objectType == 'Collider':
                # out.append(c.data.name) 'cos using object names, not mesh names
                out.append(c.name)
        return 'none'

    def getTexture(self, thing):
        # TODO: later should be converted to texture with material ID and decals, but for now one from PBR material pool will be enough
        # tex = object.data.uv_textures.active.data[0].image
        # if tex:
            # return tex.name
        # else:
            return 'none'

    def getLights(self, objects):
        out = []
        for lamp in objects:
            data = OrderedDict()

            data['Name'] = lamp.name

            lampObject = bpy.data.objects[lamp.name]

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


def menu_func(self, context):
    self.layout.operator(ExportScene.bl_idname, text='PMK Scene (.yml)');

def register():
    bpy.utils.register_class(ExportScene);
    bpy.types.TOPBAR_MT_file_export.append(menu_func);

def unregister():
    bpy.types.TOPBAR_MT_file_export.remove(menu_func);
    bpy.utils.register_class(ExportScene);

if __name__ == '__main__':
    register()
