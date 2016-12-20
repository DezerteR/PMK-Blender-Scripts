import os
import bpy
import PMK_SceneProperties

bl_info = {
    "name": "PMK Scene Panel",
    "author": "DezerteR",
    "version": (0, 0, 1),
    "blender": (2, 7, 6),
    "location": "Viewport",
    "description": "Adds panel in object properties that allows editing sceneproperties.",
    "category": "Object"
    }

''' Utils:
panel API: http://www.blender.org/api/blender_python_api_2_73a_release/bpy.types.Panel.html?highlight=panel%20class
UI API: http://www.blender.org/api/blender_python_api_2_73a_release/bpy.types.UILayout.html#bpy.types.UILayout
UI description: http://www.blenderui.com/Blender_UI.html
useful: http://elfnor.com/drop-down-and-button-select-menus-for-blender-operator-add-ons.html
'''

class OBJECT_PT_tank_module(bpy.types.Panel):
    """Object Cursor Array"""
    bl_label = "PMK Scene"
    bl_idname = "OBJECT_PT_scene_module"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_options = {'DEFAULT_CLOSED'}
    bl_context = "object"

    def draw(self, context):
        layout = self.layout
        obj = context.object

        layout.row().prop(obj.scene, "objectType", expand=True)
        layout.row().prop(obj.scene, "is_collider", expand=True)
        if obj.scene.objectType == 'Glossy':
            layout.row().prop(obj.scene, "glossEnergy", text='Energy')

def register():
    print('\nregistering ', 'Tank Modules')
    bpy.utils.register_class(OBJECT_PT_tank_module)

def unregister():
    bpy.utils.unregister_class(OBJECT_PT_tank_module)

if __name__ == "__main__":
    register()
