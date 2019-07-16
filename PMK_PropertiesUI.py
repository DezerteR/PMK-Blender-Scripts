import os
import bpy
import PMK_Properties

bl_info = {
    'name': 'PMK Properties Panel',
    'author': 'Karol Wajs',
    'version': (0, 0, 1),
    'blender': (2, 80, 0),
    'location': 'Viewport',
    'description': 'Adds panel in object properties that allows editing properties.',
    'category': 'Object'
    }

''' Utils:
panel API: http://www.blender.org/api/blender_python_api_2_73a_release/bpy.types.Panel.html?highlight=panel%20class
UI API: http://www.blender.org/api/blender_python_api_2_73a_release/bpy.types.UILayout.html#bpy.types.UILayout
UI description: http://www.blenderui.com/Blender_UI.html
useful: http://elfnor.com/drop-down-and-button-select-menus-for-blender-operator-add-ons.html
'''

def register():
    print('\nregistering ', 'PMK properties UI')
    bpy.utils.register_class(OBJECT_PT_PropsUI)

def unregister():
    bpy.utils.unregister_class(OBJECT_PT_PropsUI)

if __name__ == '__main__':
    register()

class OBJECT_PT_PropsUI(bpy.types.Panel):
    bl_label = 'Po-Male-Ka'
    bl_idname = 'OBJECT_PT_PropsUI'
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_options = {'DEFAULT_CLOSED'}
    bl_context = 'object'

    def draw(self, context):
        layout = self.layout
        obj = context.object
        scene = context.scene

        if scene.pmk.editingMode == 'Scene':
            self.objectPropsForScene(obj, layout)
        elif scene.pmk.editingMode == 'Vehicle':
            self.objectPropsForVehicle(obj, layout)

    def objectPropsForScene(self, obj, layout):
        if obj.type == 'MESH':
            self.sceneObjectProps(obj.pmk.sceneObjectProps, layout)
        elif obj.type == 'EMPTY':
            self.emptyProps(obj.pmk.emptyProps, layout)
        elif obj.type == 'CAMERA':
            self.cameraProps(obj.pmk.cameraProps, layout)

    def objectPropsForVehicle(self, obj, layout):
        if obj.type == 'MESH':
            self.forModule(obj.pmk.moduleProps, layout)
        elif obj.type == 'EMPTY':
            self.emptyProps(obj.pmk.emptyProps, layout)
        elif obj.type == 'CAMERA':
            self.cameraProps(obj.pmk.cameraProps, layout)

    def forModule(self,  moduleProps, layout):
        layout.prop(moduleProps, 'objectType')
        if moduleProps.objectType == 'Module':
            layout.prop(moduleProps, 'moduleClass')

        layout.prop(moduleProps, 'armorClass')
        layout.prop(moduleProps, 'isActive')
        layout.prop(moduleProps, 'hasServo')




    def sceneObjectProps(self, props, layout):
        layout.prop(props, 'objectType')

    def emptyProps(self, props, layout):
        layout.prop(props, 'objectType')
        if props.objectType == 'Joint':
            layout.prop(props, 'jointType')
            layout.prop(props, 'mainAxis')
        elif props.objectType == 'Marker':
            layout.prop(props, 'markerType')
        elif props.objectType == 'Decal':
            layout.prop(props, 'decalName')
        elif props.objectType == 'Special':
            layout.prop(props, 'specialName')

    def cameraProps(self, props, layout):
            layout.prop(props, 'mode')
            layout.prop(props, 'offset')
            layout.prop(props, 'inertia')
