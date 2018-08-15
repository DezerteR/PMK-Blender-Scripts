
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

class ExportScene(bpy.types.Operator, ExportHelper):
    bl_idname       = "pmkscene.yml";
    bl_label        = "PMK Scene exporter";
    bl_options      = {'PRESET'};

    filename_ext    = ".yml";

    def execute(self, context):
        config = OrderedDict()
        config['Materials'] = self.getMaterials(bpy.data.materials)
        config["Objects"] = self.getObjects(bpy.data.objects)
        ls = self.getLights(bpy.data.objects)
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
            out[mat.name] = {
                "roughness": mat.pmk.roughness,
                "metallic": mat.pmk.metallic,
                "reflectance": mat.pmk.reflectance,
                "clearCoat": mat.pmk.clearCoat,
                "clearCoatRoughness": mat.pmk.clearCoatRoughness,
                "anisotropy": mat.pmk.anisotropy,
                "emissive": mat.pmk.emissive,
            }
        return out


    def getObjects(self, objectList):
        out = []
        for obj in objectList:
            self.appendObject(obj, out)

        return out

    def appendObject(self, thing, objectList):
        if thing.type != 'MESH' or thing.pmk.propertyType == 'Physical':
            return

        data = OrderedDict()
        data['Name'] = thing.name

        m = thing.matrix_world
        data['Position'] = OrderedDict()
        data['Position']['X'] = mathutils.Vector(( m[0][0], m[1][0], m[2][0], 0))
        data['Position']['Y'] = mathutils.Vector(( m[0][1], m[1][1], m[2][1], 0))
        data['Position']['Z'] = mathutils.Vector(( m[0][2], m[1][2], m[2][2], 0))
        data['Position']['W'] = mathutils.Vector(( m[0][3], m[1][3], m[2][3], 1))
        # data['Texture'] = self.getTexture(thing)
        if thing.data is not None:
            data["Models"] = self.getMeshes(thing)
        data['isPhysical'] = thing.rigid_body is not None
        if thing.rigid_body is not None:
            data['Mass'] = thing.rigid_body.mass
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
        for thing in objects:
            if thing.type == 'LAMP':
                data = OrderedDict()

                data['Name'] = thing.name
                # object = bpy.data.objects[lamp.name]
                lamp = bpy.data.lamps[thing.data.name]

                m = thing.matrix_world
                data['Position'] = OrderedDict()
                data['Position']['X'] = mathutils.Vector(( m[0][0], m[1][0], m[2][0], 0))
                data['Position']['Y'] = mathutils.Vector(( m[0][1], m[1][1], m[2][1], 0))
                data['Position']['Z'] = mathutils.Vector(( m[0][2], m[1][2], m[2][2], 0))
                data['Position']['W'] = mathutils.Vector(( m[0][3], m[1][3], m[2][3], 1))
                data['Color'] = mathutils.Vector(( thing.color[0], thing.color[1], thing.color[2] ))

                data['Falloff_distance'] = lamp.distance
                data['Energy'] = lamp.energy
                data['Type'] = lamp.type

                if lamp.type == 'POINT':
                    data['falloff_type'] = lamp.falloff_type

                if lamp.type == 'SPOT':
                    # file.write(offset + '  falloff_type: ' + lamp.falloff_type)
                    data['spot_size'] = lamp.spot_size

                if lamp.type == 'AREA':
                    data['Size'] = lamp.size
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
