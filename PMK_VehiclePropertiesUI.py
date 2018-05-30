import os
import bpy
import PMK_TankProperties

bl_info = {
    "name": "PMK Panel",
    "author": "Karol Wajs",
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

def register():
    print('\nregistering ', 'Tank properties UI')
    bpy.utils.register_class(OBJECT_PT_tank_module)

def unregister():
    bpy.utils.unregister_class(OBJECT_PT_tank_module)

if __name__ == "__main__":
    register()

class OBJECT_PT_tank_module(bpy.types.Panel):
    bl_label = "Po-Male-Ka"
    bl_idname = "OBJECT_PT_tank_module"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_options = {'DEFAULT_CLOSED'}
    bl_context = "object"

    def draw(self, context):
        layout = self.layout
        obj = context.object

        if self.commonProperties(obj, layout.box()):
            self.techInfo(obj, layout.box())
            # self.specificProperties(obj, layout.box())

    def commonProperties(self, obj, layout):

        layout.column().prop(obj, "name")
        layout.column().prop(obj.pmk, "pretty_name")
        layout.column().prop(obj.pmk, "enabled_to_use")
        row = layout.row().prop(obj.pmk, "property_type", expand=False)
        # layout.operator_menu_enum("object.moduletypeselection", "property_type", text="Add Module Type")

        if 'Module' == obj.pmk.property_type:
            self.layout.box().row().prop(obj.pmk.module_properties, "module_class", expand=False)
            self.edit_module_properties(self.layout.box(), obj.pmk.module_properties)
            self.edit_tech_properties(self.layout.box(), obj.pmk.tech_info)
        elif 'Collision' == obj.pmk.property_type:
            self.layout.box().row().label(text='Collison Model Properties')
        elif 'Armor' == obj.pmk.property_type:
            self.layout.box().row().label(text='Armor Properties')
        elif 'Slot' == obj.pmk.property_type:
            self.layout.box().row().label(text='Slot Properties')
        elif 'Decal' == obj.pmk.property_type:
            box = self.layout.box()
            box.column().label(text='Decal Properties')
            box.column().prop(obj.pmk.decal_properties, 'decal_name')
        elif 'Marker' == obj.pmk.property_type:
            self.edit_marker(self.layout.box(), obj.pmk.marker_properties)
        return False

    def edit_module_properties(self, box, obj):
        if 'Hull' == obj.module_class:
            self.edit_hull(box, obj)
        elif 'Turret' == obj.module_class:
            self.edit_turret(box, obj)
        elif 'Mantlet' == obj.module_class:
            self.edit_mantlet(box, obj)
        elif 'Gun' == obj.module_class:
            self.edit_gun(box, obj)
        elif 'Suspension' == obj.module_class:

            self.edit_suspension(box, obj)
    def edit_hull(self, box, obj):
        box.row().label(text = 'Hull propeties here')
    def edit_turret(self, box, obj):
        box.column().prop(obj, "rotate_velocity")
        box.column().prop(obj, "ammo_capacity")
    def edit_mantlet(self, box, obj):
        box.column().prop(obj, "min_vertical")
        box.column().prop(obj, "max_vertical")
    def edit_gun(self, box, obj):
        box.column().prop(obj, "dispersion")
        box.column().prop(obj, "accuracy")
        box.column().prop(obj, "caliber", expand=False)
    def edit_suspension(self, box, obj):
        box.column().prop(obj, "stiffness")
        box.column().prop(obj, "damping")
        box.column().prop(obj, "compression")
        box.column().prop(obj, "max_travel")
        box.column().prop(obj, "max_force")
        box.column().prop(obj, "wheel_friction")
        box.column().prop(obj, "roll_influence")
        box.column().prop(obj, "shoe_mesh")
    def edit_tech_properties(self, box, obj):
        box.label(text="Tech properties")

        box.prop(obj, "price")
        box.prop(obj, "required_exp")

    def edit_marker(self, box, obj):
        box.row().label(text='Marker Properties')
        box.row().prop(obj, 'type')
        if 'Camera' == obj.type:
            box.row().prop(obj, 'camera_mode')
        elif 'Light' == obj.type:
            pass
        elif 'SmokeSource' == obj.type:
            pass
        elif 'DustSource' == obj.type:
            pass
