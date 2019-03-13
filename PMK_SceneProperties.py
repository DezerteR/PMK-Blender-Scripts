import os
import bpy
from bpy.props import *

bl_info = {
    "name": "PMK scene properties",
    "author": "Karol Wajs",
    "version": (0, 0, 1),
    "blender": (2, 7, 6),
    "location": "Viewport",
    "description": "Adds panel in object properties that allows editing scene properties.",
    "category": "Object"
    }

class SceneProperties(bpy.types.PropertyGroup):
    '''Common module properties '''
    objectType = EnumProperty(items = (('Regular', 'Regular', 'Standard scene object'),
                                       ('Collider', 'Collider', 'Physic representation'),
                                       ('Glossy', 'Glossy', 'Glossy object'),
                                       ('TerrainChunk', 'TerrainChunk', 'TerrainChunk'),
                                       ('TerrainCollider', 'TerrainCollider', 'TerrainCollider'),
                                 ),
                        name = "ObjectType",
                        default = 'Model')
    is_collider = BoolProperty(name="is_collider", default = False)

def register():
    print('\nregistering ', 'BaseStructs')
    bpy.utils.register_class(SceneProperties)
    bpy.types.Object.scene = PointerProperty(type=SceneProperties)

def unregister():
    del bpy.types.Object.scene
    bpy.utils.unregister_class(SceneProperties)

if __name__ == "__main__":
    register()
