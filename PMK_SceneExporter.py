
bl_info = {
        "name":         "PMK Scene exporter",
        "author":       "Karol Wajs",
        "blender":      (2,7,9),
        "version":      (0,0,1),
        "location":     "File > Export > PMK Scene exporter",
        "description":  "Export scene for Po-Male-Ka",
        "category":     "Import-Export"
}

import bpy
import mathutils
import string
import os
from bpy_extras.io_utils import ExportHelper
from collections import OrderedDict
import SimpleYaml

def setPosition(thing, data):
    m = thing.matrix_world
    data['Position'] = OrderedDict()
    data['Position']['X'] = mathutils.Vector(( m[0][0], m[1][0], m[2][0], 0))
    data['Position']['Y'] = mathutils.Vector(( m[0][1], m[1][1], m[2][1], 0))
    data['Position']['Z'] = mathutils.Vector(( m[0][2], m[1][2], m[2][2], 0))
    data['Position']['W'] = mathutils.Vector(( m[0][3], m[1][3], m[2][3], 1))


class ExportScene(bpy.types.Operator, ExportHelper):
    bl_idname       = "pmkscene.yml";
    bl_label        = "PMK Scene exporter";
    bl_options      = {'PRESET'};

    filename_ext    = ".yml";

    def execute(self, context):
        config = OrderedDict()
        config['Materials'] = self.getMaterials(bpy.data.materials)
        config["Objects"] = self.getObjects(bpy.data.objects)
        config["Markers"] = self.getMarkers(bpy.data.objects)
        config["Cameras"] = self.getCameras(bpy.data.objects)
        ls = self.getLights(bpy.data.lamps)
        if len(ls) > 0:
            config["LightSources"] = ls

        with open(self.filepath, 'w') as fp:
            SimpleYaml.writeYamlTo(fp, config)

        path = os.path.dirname(self.filepath)
        name = os.path.splitext(os.path.split(self.filepath)[1])[0]

        bpy.ops.wm.collada_export(
            filepath = os.path.join(path, name+".dae"),
            check_existing = False,
            apply_modifiers = True,
            triangulate = True,
            use_object_instantiation = False
        )
        return {'FINISHED'};

    def getMaterials(self, materials):
        out = {}
        for mat in materials:
            out[mat.name.replace(".", "_") + "-material"] = {
                "roughness": mat.pmk.roughness,
                "metallic": mat.pmk.metallic,
                "reflectance": mat.pmk.reflectance,
                "clearCoat": mat.pmk.clearCoat,
                "clearCoatRoughness": mat.pmk.clearCoatRoughness,
                "anisotropy": mat.pmk.anisotropy,
                "emissive": mat.pmk.emissive,
            }
        return out
    def getMarkers(self, objectList):
        out = []
        for obj in objectList:
            if obj.type == 'EMPTY' and obj.pmk.propertyType == 'Marker':
                data = OrderedDict()
                data['Name'] = obj.name
                data['Type'] = obj.pmk.markerProps.type
                setPosition(obj, data)

                out.append(data)
        return out;

    def getCameras(selft, objectList):
        out = []
        for obj in objectList:
            if obj.type == 'CAMERA':
                data = OrderedDict()
                data['Name'] = obj.name
                data['Type'] = obj.pmk.markerProps.type
                setPosition(obj, data)

                data['Mode'] = obj.pmk.markerProps.cameraMode
                camera = obj.data
                data['CameraType'] = camera.type
                data['Angle'] = camera.angle

                out.append(data)

        return out

    def getObjects(self, objectList):
        out = []
        for obj in objectList:
            self.appendObject(obj, out)

        return out

    def appendObject(self, thing, objectList):
        if thing.type != 'MESH' or thing.pmk.propertyType != 'Scene': # colliders are not exported this way
            return

        data = OrderedDict()
        data['Name'] = thing.name

        setPosition(thing, data)
        data['Dimensions'] = thing.dimensions
        # data['Texture'] = self.getTexture(thing)
        if thing.data is not None:
            data["Models"] = self.getMeshes(thing)
        data['isPhysical'] = thing.rigid_body is not None
        if thing.rigid_body is not None:
            data['Mass'] = thing.rigid_body.mass if thing.rigid_body.collision_shape != 'MESH' else 0
            data['Shape'] = thing.rigid_body.collision_shape
            data['Colliders'] = self.findPhysicalModels(thing)

        objectList.append(data)

    def getMeshes(self, thing):
        # // out = [thing.data.name] 'cos using object names, not mesh names
        out = [thing.name]
        for child in thing.children:
            if child.pmk.propertyType == 'Part' and child.data is not None:
                # // out.append(child.data.name) 'cos using object names, not mesh names
                out.append(child.name)
        return out

    def findPhysicalModels(self, thing):
        out = []
        for c in thing.children:
            if c.pmk.propertyType == 'Collision':
                # // out.append(c.data.name) 'cos using object names, not mesh names
                out.append(c.name)
        return "none"

    def getTexture(self, thing):
        # TODO: later should be converted to texture with material ID and decals, but for now one from PBR material pool will be enough
        # tex = object.data.uv_textures.active.data[0].image
        # if tex:
            # return tex.name
        # else:
            return "none"

    def getLights(self, objects):
        out = []
        for lamp in objects:
            if lamp.type != 'POINT' and lamp.type != 'SPOT':
                continue

            data = OrderedDict()

            data['Name'] = lamp.name

            lampObject = bpy.data.objects[lamp.name]

            setPosition(lampObject, data)
            data['Color'] = mathutils.Vector(( lamp.color[0], lamp.color[1], lamp.color[2] ))

            data['Falloff_distance'] = lamp.distance
            data['Energy'] = lamp.energy
            data['Type'] = lamp.type

            if lamp.type == 'POINT':
                data['Falloff_type'] = lamp.falloff_type

            if lamp.type == 'SPOT':
                # file.write(offset + '  falloff_type: ' + lamp.falloff_type)
                data['spot_size'] = lamp.spot_size

            if lamp.type == 'AREA':
                data['Size'] = lamp.size

            out.append(data)
        return out


def menu_func(self, context):
    self.layout.operator(ExportScene.bl_idname, text="PMK Scene (.yml)");
def register():
    bpy.utils.register_module(__name__);
    bpy.types.INFO_MT_file_export.append(menu_func);
def unregister():
    bpy.utils.unregister_module(__name__);
    bpy.types.INFO_MT_file_export.remove(menu_func);
if __name__ == "__main__":
    register()
