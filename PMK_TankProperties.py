﻿import os
import bpy
from bpy.props import *

bl_info = {
    "name": "PMK tank properties",
    "author": "DezerteR",
    "version": (0, 0, 1),
    "blender": (2, 7, 6),
    "location": "Viewport",
    "description": "Adds panel in object properties that allows editing tank module properties.",
    "category": "Object"
    }

def register():
    print('\nregistering ', 'Tank properties')
    bpy.utils.register_class(SlotProperties)
    bpy.utils.register_class(ModuleProperties)
    bpy.utils.register_class(CollisonModelProperties)
    bpy.utils.register_class(ArmorProperties)
    bpy.utils.register_class(DecalProperties)
    bpy.utils.register_class(MarkerProperties)
    bpy.utils.register_class(TechInfo)
    bpy.utils.register_class(CommonProperties)
    bpy.types.Object.pmk = PointerProperty(type=CommonProperties)

def unregister():
    del bpy.types.Object.pmk
    bpy.utils.unregister_class(CommonProperties)
    bpy.utils.unregister_class(TechInfo)
    bpy.utils.unregister_class(MarkerProperties)
    bpy.utils.unregister_class(DecalProperties)
    bpy.utils.unregister_class(ArmorProperties)
    bpy.utils.unregister_class(CollisonModelProperties)
    bpy.utils.unregister_class(ModuleProperties)
    bpy.utils.unregister_class(SlotProperties)

if __name__ == "__main__":
    register()


class TechInfo(bpy.types.PropertyGroup):
    '''Module technology properties '''
    price = FloatProperty(default = 10000)
    requiredExp = FloatProperty(default = 10000)

def change_module_type(self, context):
    print(self.moduleType, context.object.name)
def dummmy_update(self, context):
    pass

class ModuleProperties(bpy.types.PropertyGroup):
    type = EnumProperty(items = (('Empty', 'Empty', 'The zeroth item'),
                                 ('Hull', 'Hull', 'The first item'),
                                 ('Turret', 'Turret', 'The second item'),
                                 ('Mantlet', 'Mantlet', 'The second item'),
                                 ('Gun', 'Gun', 'The third item'),
                                 ('Suspension', 'Suspension', 'The third item'),
                                 ('MainWheel', 'Main Wheel', 'The third item'),
                                 ('SupportWheel', 'Support Wheel', 'The third item'),
                                 ('DriveWheel', 'Drive Wheel', 'The third item'),
                                 ('Armor', 'Armor', 'Additional armor module'),
                                ),
                        name = "Module Class",
                        default = 'Empty',
                        update = change_module_type)
    """ --------- Common --------- """
    required_exp = FloatProperty(default = 10000)
    hitpoints = FloatProperty(default = 100)
    tier = EnumProperty(items = (('0', 'I', ''),
                                 ('1', 'II', ''),
                                 ('2', 'III', ''),
                                 ('3', 'IV', ''),
                                 ('4', 'V', ''),
                                 ('5', 'VI', ''),
                                 ),
                        name = "Tier",
                        default = '0')
    # collison models
    # armor models

    """ --------- Hull --------- """

    """ --------- Turret --------- """
    rotate_velocity = FloatProperty(default = 1, name = 'Velocity')
    # na update przelicz ilość ammo danego kalibru
    ammo_capacity = FloatProperty(default = 100, name = 'Ammo capacity')

    """ --------- Mantlet --------- """
    min_vertical = FloatProperty(default = -0.2, name = 'Min')
    max_vertical = FloatProperty(default = 0.2, name = 'Max')

    """ --------- GUN --------- """
    dispersion = FloatProperty(default = 0.1, name = 'Dispersion')
    accuracy = FloatProperty(default = 0.03, name = 'Accuracy')
    caliber = EnumProperty(items = (('100', '100mm', ''),
                                    ('105', '105mm', ''),
                                    ('120', '120mm', ''),
                                    ('125', '125mm', ''),
                                    ('135', '135mm', ''),
                                    ('150', '150mm', ''),
                                    ('152', '152mm', ''),
                                 ),
                        name = "Caliber",
                        default = '120')

    """ --------- Suspension --------- """
    stiffness = FloatProperty(default = 60, name = 'Stiffness')
    damping = FloatProperty(default = 0.3, name = 'Damping')
    compression = FloatProperty(default = 0.5, name = 'Compression')
    max_travel = FloatProperty(default = 0.5, name = 'maxTravel')
    max_force = FloatProperty(default = 5000000, name = 'maxForce')
    wheel_friction = FloatProperty(default = 100, name = 'WheelFriction')
    roll_influence = FloatProperty(default = 0.1, name = 'RollInfluence')
    shoe_mesh = StringProperty(default = 'Shoe', name = 'ShoeMesh')

class CollisonModelProperties(bpy.types.PropertyGroup):
    mass = FloatProperty(default = 1, name = 'Mass')

class ArmorProperties(bpy.types.PropertyGroup):
    armor_class = FloatProperty(default = 1, name = 'Class')

class SlotProperties(bpy.types.PropertyGroup):
    slot_name = StringProperty(default = '', name = 'SlotName')

class DecalProperties(bpy.types.PropertyGroup):
    decal_name = StringProperty(default = '', name = 'DecalName')

class MarkerProperties(bpy.types.PropertyGroup):
    type = EnumProperty(items = (('Camera', 'Camera', ''),
                                 ('Light', 'Light', ''),
                                 ('SmokeSource', 'SmokeSource', ''),
                                 ('DustSource', 'DustSource', ''),
                                 ),
                        name = "Type",
                        default = 'Camera')

    """ --------- Camera --------- """
    camera_mode = EnumProperty(items = (('Free', 'Free', 'Free cam'),
                                       ('Follow', 'Follow', 'Only position is pinned'),
                                       ('Pinned', 'Pinned', 'Camera rotates with module'),
                                 ),
                        name = "Type",
                        default = 'Follow')
    """ --------- Light --------- """
    """ --------- SmokeSource --------- """
    """ --------- DustSource --------- """

class CommonProperties(bpy.types.PropertyGroup):
    '''Common module properties '''
    pretty_name = StringProperty(default = '--', name= 'Pretty Name')
    property_type = EnumProperty(items = (('Module', 'Module', 'Module visual model'),
                                          ('Collision', 'Collision', 'Module collison model'),
                                          ('Armor', 'Armor', 'Module armor model'),
                                          ('Slot', 'Slot', 'Module slot to join other modules'),
                                          ('Decal', 'Decal', '...'),
                                          ('Marker', 'Marker', '...'),
                                 ),
                        name = "Property Type",
                        default = 'Module')

    module_properties = PointerProperty(type = ModuleProperties)
    collision_properties = PointerProperty(type = CollisonModelProperties)
    armor_properties = PointerProperty(type = ArmorProperties)
    slot_properties = PointerProperty(type = SlotProperties)
    decal_properties = PointerProperty(type = DecalProperties)
    marker_properties = PointerProperty(type = MarkerProperties)
    tech_info = PointerProperty(type = TechInfo)
