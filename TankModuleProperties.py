import os
import bpy
import PMKProperties

bl_info = {
    "name": "PMK Panel",
    "author": "DezerteR",
    "version": (0, 0, 1),
    "blender": (2, 7, 6),
    "location": "Viewport",
    "description": "Adds panel in object properties that allows editing tank module properties.",
    "category": "Object"
    }

''' Utils:
panel API: http://www.blender.org/api/blender_python_api_2_73a_release/bpy.types.Panel.html?highlight=panel%20class
UI API: http://www.blender.org/api/blender_python_api_2_73a_release/bpy.types.UILayout.html#bpy.types.UILayout
UI description: http://www.blenderui.com/Blender_UI.html
useful: http://elfnor.com/drop-down-and-button-select-menus-for-blender-operator-add-ons.html
'''

class ModuleTypeSelection(bpy.types.Operator) :
    bl_idname = "object.moduletypeselection"
    bl_label = "Module type selection"
    bl_options = {"REGISTER", "UNDO"}

    fixed_items = bpy.props.EnumProperty(items= (('Empty', 'Empty', 'The zeroth item'),
                                                 ('Hull', 'Hull', 'The first item'),
                                                 ('Turret', 'Turret', 'The second item'),
                                                 ('Mantlet', 'Mantlet', 'The second item'),
                                                 ('Gun', 'Gun', 'The third item'),
                                                 ('Suspension', 'Suspension', 'The third item')
                                                 ),
                                                 name = "fixed list")
    def execute(self, context) :
        print("fixed item", self.fixed_items)
        obj = context.object
        print(obj.name)
        return {"FINISHED"}

class OBJECT_PT_tank_module(bpy.types.Panel):
    """Object Cursor Array"""
    bl_label = "Tank Modules"
    bl_idname = "OBJECT_PT_tank_module"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_options = {'DEFAULT_CLOSED'}
    bl_context = "object"

    calibers = bpy.props.IntVectorProperty(name = "calibers", default = (100, 105, 120, 125, 128, 135, 150))

    def draw(self, context):
        layout = self.layout
        obj = context.object

        self.commonProperties(obj, layout.box())
        self.techInfo(obj, layout.box())
        self.specificProperties(obj, layout.box())
        self.setModuleType(context, layout)

    def commonProperties(self, obj, layout):
        column = layout.column()
        column.label(text="Common properties")
        column = layout.column()
        column.prop(obj, "name")
        column = layout.column()
        column.prop(obj.common, "type")

    def setModuleType(self, context, layout):
        layout.operator_menu_enum("object.moduletypeselection", "fixed_items", text="Add Module Type")

    def techInfo(self, obj, layout):
        column = layout.column()
        column.label(text="Tech properties")

        techInfo = obj.techInfo
        column = layout.column()
        column.prop(techInfo, "price")
        column = layout.column()
        column.prop(techInfo, "requiredExp")
        pass

    def specificProperties(self, obj, layout):
        column = layout.column()
        column.label(text="Module specific")
        pass

def register():
    print('\nregistering ', 'Tank Modules')
    bpy.utils.register_class(ModuleTypeSelection)
    bpy.utils.register_class(OBJECT_PT_tank_module)

def unregister():
    bpy.utils.unregister_class(OBJECT_PT_tank_module)
    bpy.utils.unregister_class(ModuleTypeSelection)

if __name__ == "__main__":
    register()