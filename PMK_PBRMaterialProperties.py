import os
import bpy
from bpy.props import *

bl_info = {
    "name": "PMK PBR Materials",
    "author": "Karol Wajs",
    "version": (0, 0, 1),
    "blender": (2, 7, 6),
    "location": "Viewport",
    "description": "Adds panel in material properties that allows editing material PBR properties.",
    "category": "Material"
    }

def register():
    bpy.utils.register_class(OBJECT_PT_MaterialProps)
    bpy.types.Material.pmk = PointerProperty(type=OBJECT_PT_MaterialProps)
    bpy.utils.register_class(OBJECT_PT_MaterialPropsUI)

def unregister():
    bpy.utils.unregister_class(OBJECT_PT_MaterialPropsUI)
    del bpy.types.Material.pmk
    bpy.utils.unregister_class(OBJECT_PT_MaterialProps)

if __name__ == "__main__":
    register()

class OBJECT_PT_MaterialPropsUI(bpy.types.Panel):
    bl_label = "PMK"
    bl_idname = "OBJECT_PT_MaterialPropsUI"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_options = {'DEFAULT_CLOSED'}
    bl_context = "material"

    def draw(self, context):
        layout = self.layout
        obj = context.object
        layout.row().prop(obj.active_material.pmk, "roughness")
        layout.row().prop(obj.active_material.pmk, "metallic")
        layout.row().prop(obj.active_material.pmk, "reflectance")
        layout.row().prop(obj.active_material.pmk, "clearCoat")
        layout.row().prop(obj.active_material.pmk, "clearCoatRoughness")
        layout.row().prop(obj.active_material.pmk, "anisotropy")
        layout.row().prop(obj.active_material.pmk, "emissive")

class OBJECT_PT_MaterialProps(bpy.types.PropertyGroup):
    '''Common module properties '''
    roughness = FloatProperty(default = 0.6, name = 'Roughness', min = 0.0, max = 1.0)
    metallic = FloatProperty(default = 0, name = 'Metallic', min = 0.0, max = 1.0)
    reflectance = FloatProperty(default = 0.5, name = 'Reflectance', min = 0.0, max = 1.0)
    clearCoat = FloatProperty(default = 0, name = 'ClearCoat', min = 0.0, max = 1.0)
    clearCoatRoughness = FloatProperty(default = 0.1, name = 'ClearCoat Roughness', min = 0.0, max = 1.0)
    anisotropy = FloatProperty(default = 0.0, name = 'Anisotropy', min = 0.0, max = 1.0)
    emissive = FloatProperty(default = 0.0, name = 'Emissive', min = 0.0, max = 1.0)
