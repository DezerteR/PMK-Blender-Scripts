import os
import bpy
import PMK_TankProperties

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

class OBJECT_PT_tank_module(bpy.types.Panel):
    """Object Cursor Array"""
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
            self.specificProperties(obj, layout.box())

    def commonProperties(self, obj, layout):

        # layout.column().operator(operator = 'TankInfoExporter.vehicle_info.yml()', text="Export Info")
        layout.column().label(text="Common properties")
        layout.column().prop(obj, "name")
        layout.column().prop(obj.common, "prettyName")
        row = layout.row().prop(obj.common, "objectType", expand=True)
        if obj.common.objectType == 'Mesh':
            column = layout.column().prop(obj.common, "moduleType")
            return True
        return False

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

    def specificProperties(self, obj, layout):
        column = layout.column()
        column.label(text="Module specific")

        layout.row().prop(obj.common, "tier", expand = True)

        if obj.common.moduleType == 'Hull':
            self.drawHull(obj.common, layout)
        elif obj.common.moduleType == 'Turret':
            self.drawTurret(obj.common, layout)
        elif obj.common.moduleType == 'Mantlet':
            self.drawMantlet(obj.common, layout)
        elif obj.common.moduleType == 'Gun':
            self.drawGun(obj.common, layout)
        elif obj.common.moduleType == 'Suspension':
            self.drawSuspension(obj.common, layout)

    def drawHull(self, obj, layout):
        pass

    def drawTurret(self, obj, layout):
        layout.column().prop(obj, "rotateVelocity")
        layout.column().prop(obj, "ammoCapacity")

    def drawMantlet(self, obj, layout):
        layout.column().prop(obj, "minVertical")
        layout.column().prop(obj, "maxVertical")

    def drawGun(self, obj, layout):
        layout.column().prop(obj, "dispersion")
        layout.column().prop(obj, "accuracy")
        layout.column().prop(obj, "caliber")

    def drawSuspension(self, obj, layout):
        layout.column().prop(obj, "stiffness")
        layout.column().prop(obj, "damping")
        layout.column().prop(obj, "compression")
        layout.column().prop(obj, "wheel_friction")
        layout.column().prop(obj, "max_travel")
        layout.column().prop(obj, "max_force")
        layout.column().prop(obj, "roll_influence")
        layout.column().prop(obj, "shoe_mesh")

def register():
    print('\nregistering ', 'Tank Modules')
    bpy.utils.register_class(OBJECT_PT_tank_module)

def unregister():
    bpy.utils.unregister_class(OBJECT_PT_tank_module)

if __name__ == "__main__":
    register()