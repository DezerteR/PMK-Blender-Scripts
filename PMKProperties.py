import os
from bpy.props import *

bl_info = {
    "name": "PMK module properties",
    "author": "DezerteR",
    "version": (0, 0, 1),
    "blender": (2, 7, 6),
    "location": "Viewport",
    "description": "Adds panel in object properties that allows editing tank module properties.",
    "category": "Object"
    }

class TechInfo(bpy.types.PropertyGroup):
    '''Module technology properties '''
    price = FloatProperty(default = 10000)
    requiredExp = FloatProperty(default = 10000)

class CommonProperties(bpy.types.PropertyGroup):
    '''Common module properties '''
    type = EnumProperty(items = (('Empty', 'Empty', 'The zeroth item'),
                                 ('Hull', 'Hull', 'The first item'),
                                 ('Turret', 'Turret', 'The second item'),
                                 ('Mantlet', 'Mantlet', 'The second item'),
                                 ('Gun', 'Gun', 'The third item'),
                                 ('Suspension', 'Suspension', 'The third item')
                                 ),
                        name = "fixed list",
                        default = 'Empty')
    requiredExp = FloatProperty(default = 10000)

def register():
    print('\nregistering ', 'BaseStructs')
    bpy.utils.register_class(TechInfo)
    bpy.types.Object.techInfo = PointerProperty(type=TechInfo)
    bpy.utils.register_class(CommonProperties)
    bpy.types.Object.common = PointerProperty(type=CommonProperties)

def unregister():
    del bpy.types.Object.common
    bpy.utils.unregister_class(CommonProperties)
    del bpy.types.Object.techInfo
    bpy.utils.unregister_class(TechInfo)

if __name__ == "__main__":
    register()