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
                        name = "Type",
                        default = 'Empty',
                        update = change_module_type)
    """ --------- Common --------- """
    required _exp = FloatProperty(default = 10000)
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
    pass
class SlotProperties(bpy.types.PropertyGroup):
    pass
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
    prettyName = StringProperty(default = '--')
    objectType = EnumProperty(items = (('Mesh', 'Mesh', 'Module visual model'),
                                       ('Collision', 'Collision', 'Module collison model'),
                                       ('Armor', 'Armor', 'Module armor model'),
                                       ('Slot', 'Slot', 'Module slot to join other modules'),
                                       ('Decal', 'Decal', '...'),
                                       ('Marker', 'Marker', '...'),
                                 ),
                        name = "ObjectType",
                        default = 'Mesh')

    module_properties = GroupProperty()
    collision_properties = GroupProperty()
    armor_properties = GroupProperty()
    slot_properties = GroupProperty()
    decal_properties = GroupProperty()
    marker_properties = GroupProperty()

    """ --------- Camera --------- """
    """ --------- Decal --------- """
    decal_name = StringProperty(default = '', name = 'DecalName')
    """ --------- Marker --------- """


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
