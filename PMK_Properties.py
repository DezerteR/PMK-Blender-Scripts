﻿import os
import bpy
from bpy.props import *

bl_info = {
    'name': 'PMK Object Properties',
    'author': 'Karol Wajs',
    'version': (0, 0, 1),
    'blender': (2, 80, 0),
    'location': 'Viewport',
    'description': '',
    'category': 'Object'
    }

if __name__ == '__main__':
    register()

class SceneObjectProps(bpy.types.PropertyGroup):
    objectType: EnumProperty(items = (('Regular', 'Regular', 'Regular object', 1),
                                      ('RegularSubPart', 'Terrain', 'Terrain', 2),
                                      ('Terrain', 'Terrain', 'Terrain', 2),
                                      ('Collider', 'Collider', 'Collider for module', 3),
                                      ('Foliage', 'Foliage', 'Foliage', 4),
                                 ),
                        name = 'Type',
                        default = 'Regular')

class ModuleProps(bpy.types.PropertyGroup):
    objectType: EnumProperty(items = (('Base', 'Base', 'Main object, building starts from it', 1),
                                      ('Module', 'Module', 'Functional module', 2),
                                      ('Part', 'Part', 'Separate object being part of Module. Cannot have slots', 3),
                                      ('Collider', 'Collider', 'Collider for module', 4),
                                      ('Armor', 'Armor', 'Armor definition for Module', 5),
                                 ),
                        name = 'Type',
                        default = 'Module')

    armorClass: FloatProperty(default = 1, name = 'Class')

class EmptyProps(bpy.types.PropertyGroup):
    objectType: EnumProperty(items = (('Joint', 'Joint', 'Connects modules', 1),
                                      ('Marker', 'Marker', '...', 2),
                                      ('Decal', 'Decal', '...', 3),
                                 ),
                        name = 'Type',
                        default = 'Marker')
    jointType: EnumProperty(items = (('Revolute', 'Revolute', '1DOF rotation around Z axis', 1),
                                      ('Prismatic', 'Prismatic', '1DOF linear movement along Z axis', 2),
                                      ('2DOF', '2DOF', '2DOF connection, primary around Z then around X(assuming targeting with Y axis)', 3),
                                      ('Ball', 'Ball', '3DOF ball connection', 4)
                    ),
                    name = 'Joint Type',
                    default = 'Revolute'
                )
    markerType: EnumProperty(items = (('Camera', 'Camera', '', 1),
                                       ('SmokeSource', 'SmokeSource', '', 3),
                                       ('DustSource', 'DustSource', '', 4),
                                       ('EndOfBarrel', 'End Of Barrel', '', 5),
                                       ('SpawnPoint', 'Spawn Point', 'Point where object can be spawned at game start', 6),
                                       ),
                        name = 'Marker Type',
                        default = 'Camera')
    decalName: StringProperty(default = '', name = 'DecalName')

class CameraProps(bpy.types.PropertyGroup):
    mode: EnumProperty(items = (('Free', 'Free', 'Free cam', 1),
                                ('CopyPosition', 'CopyPosition', '', 2),
                                ('CopyPlane', 'CopyPlane', '', 3),
                                ('CopyTransform', 'CopyTransform', '', 4),
                                 ),
                        name = 'Mode',
                        default = 'CopyPosition')
    offset: FloatVectorProperty(default = (0,0,0), name = 'Offset', min = -5, max = 23)
    inertia: FloatProperty(default = 1, name = 'Inertia', min = 0, max = 50)

class ObjectProps(bpy.types.PropertyGroup):
    identifier: StringProperty(default = 'none', name= 'Identifier')
    sceneObjectProps: PointerProperty(type = SceneObjectProps)
    moduleProps: PointerProperty(type = ModuleProps)
    emptyProps: PointerProperty(type = EmptyProps)
    cameraProps: PointerProperty(type = CameraProps)
    isActive: BoolProperty(name = 'Active', default = True)

class SceneProps(bpy.types.PropertyGroup):
    editingMode: EnumProperty(items = (('Scene', 'Scene', 'Currently game scene is created', 1),
                                       ('Vehicle', 'Vehicle', 'Building vehicle', 2),
                                 ),
                        name = 'Editing Mode',
                        default = 'Scene')

classes = (
    SceneObjectProps,
    ModuleProps,
    EmptyProps,
    CameraProps,
    ObjectProps,
    SceneProps,
)

def register():
    from bpy.utils import register_class
    for cls in classes:
        register_class(cls)
    bpy.types.Scene.pmk = PointerProperty(type=SceneProps)
    bpy.types.Object.pmk = PointerProperty(type=ObjectProps) # CollectionProperty reportedly better

def unregister():
    del bpy.types.Object.pmk
    del bpy.types.Scene.pmk
    from bpy.utils import unregister_class
    for cls in reversed(classes):
        unregister_class(cls)
