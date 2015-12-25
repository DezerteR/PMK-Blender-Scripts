import os
import bpy
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

def change_module_type(self, context):
    print(self.moduleType, context.object.name)

class CommonProperties(bpy.types.PropertyGroup):
    '''Common module properties '''
    prettyName = StringProperty(default = '--')
    objectType = EnumProperty(items = (('Mesh', 'Mesh', 'The zeroth item'),
                                       ('Collision', 'Collision', 'The second item'),
                                       ('Armor', 'Armor', 'The first item'),
                                       ('Slot', 'Slot', 'The first item'),
                                 ),
                        name = "ObjectType",
                        default = 'Mesh')
    moduleType = EnumProperty(items = (('Empty', 'Empty', 'The zeroth item'),
                                       ('Hull', 'Hull', 'The first item'),
                                       ('Turret', 'Turret', 'The second item'),
                                       ('Mantlet', 'Mantlet', 'The second item'),
                                       ('Gun', 'Gun', 'The third item'),
                                       ('Suspension', 'Suspension', 'The third item'),
                                       ('Armor', 'Armor', 'The third item'),
                                       ('Camera', 'Camera', 'The third item'),
                                 ),
                        name = "Type",
                        default = 'Empty',
                        update = change_module_type)
    requiredExp = FloatProperty(default = 10000)
    hitpoints = FloatProperty(default = 100)
    tier = EnumProperty(items = (('0', 'I', 'The zeroth item'),
                                 ('1', 'II', 'The first item'),
                                 ('2', 'III', 'The second item'),
                                 ('3', 'IV', 'The second item'),
                                 ('4', 'V', 'The third item'),
                                 ('5', 'VI', 'The third item'),
                                 ),
                        name = "Tier",
                        default = '0')

    """ --------- Hull --------- """
    """ --------- Turret --------- """
    rotateVelocity = FloatProperty(default = 1, name = 'Velocity')
    # na update przelicz ilość ammo danego kalibru
    ammoCapacity = FloatProperty(default = 100, name = 'Ammo capacity')
    """ --------- Mantlet --------- """
    minVertical = FloatProperty(default = -0.2, name = 'Min')
    maxVertical = FloatProperty(default = 0.2, name = 'Max')
    """ --------- GUN --------- """
    dispersion = FloatProperty(default = 0.1, name = 'Dispersion')
    accuracy = FloatProperty(default = 0.03, name = 'Accuracy')
    caliber = EnumProperty(items = (('100', '100mm', 'The zeroth item'),
                                    ('105', '105mm', 'The second item'),
                                    ('120', '120mm', 'The first item'),
                                    ('125', '125mm', 'The first item'),
                                    ('135', '135mm', 'The first item'),
                                    ('150', '150mm', 'The first item'),
                                    ('152', '152mm', 'The first item'),
                                 ),
                        name = "Caliber",
                        default = '120')
    """ --------- Suspension --------- """
    """ --------- Camera --------- """

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