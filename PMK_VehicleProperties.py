import os
import bpy
from bpy.props import *

bl_info = {
    "name": "PMK Vehicle properties",
    "author": "Karol Wajs",
    "version": (0, 0, 1),
    "blender": (2, 7, 6),
    "location": "Viewport",
    "description": "",
    "category": "Object"
    }

def register():
    print('\nregistering ', 'Tank properties')
    bpy.utils.register_class(ModuleProperties)
    bpy.utils.register_class(JointProperties)
    bpy.utils.register_class(ArmorProperties)
    bpy.utils.register_class(DecalProperties)
    bpy.utils.register_class(MarkerProperties)
    bpy.utils.register_class(CommonProperties)
    bpy.types.Object.pmk = PointerProperty(type=CommonProperties)

def unregister():
    del bpy.types.Object.pmk
    bpy.utils.unregister_class(CommonProperties)
    bpy.utils.unregister_class(MarkerProperties)
    bpy.utils.unregister_class(DecalProperties)
    bpy.utils.unregister_class(ArmorProperties)
    bpy.utils.unregister_class(JointProperties)
    bpy.utils.unregister_class(ModuleProperties)

if __name__ == "__main__":
    register()


def change_module_type(self, context):
    print(self.moduleType, context.object.name)

class ModuleProperties(bpy.types.PropertyGroup):
    moduleType = EnumProperty(items = (('Empty', 'Empty', 'The zeroth item', 1),
                                       ('Base', 'Base', 'The first item', 2),
                                       ('Turret', 'Turret', 'The second item', 3),
                                       ('Turret-Part', 'Turret-Part', 'The second item', 12),
                                       ('Mantlet', 'Mantlet', 'The second item', 4),
                                       ('Gun', 'Gun', 'The third item', 5),
                                       ('Suspension', 'Suspension', 'The third item', 6),
                                        # ('RoadWheel', 'Road Wheel', 'The third item', 7),
                                       #  ('SupportWheel', 'Support Wheel', 'The third item', 8),
                                       #  ('DriveSprocket', 'Drive Sprocket', 'The third item', 9),
                                       #  ('IdlerWheel', 'Idler Wheel', 'The third item', 10),
                                       ('Armor', 'Armor', 'Additional armor module', 11),
                                       ('LoosePart', 'LoosePart', 'Don\'t know what it could be', 13),
                                        ),
                                name = "Module Type",
                                default = 'Empty',
                                update = change_module_type)

    """ --------- Hull --------- """

    """ --------- Turret --------- """
    # rotate_velocity = FloatProperty(default = 1, name = 'Velocity', min = 0.0, max = 5.0)

    """ --------- GUN --------- """
    # dispersion = FloatProperty(default = 0.1, name = 'Dispersion', min = 0.0, max = 1.0)
    # accuracy = FloatProperty(default = 0.03, name = 'Accuracy', min = 0.0, max = 1.0)
    # caliber = EnumProperty(items = (('100', '100mm', ''),
    #                                 ('105', '105mm', ''),
    #                                 ('120', '120mm', ''),
    #                                 ('125', '125mm', ''),
    #                                 ('135', '135mm', ''),
    #                                 ('150', '150mm', ''),
    #                                 ('152', '152mm', ''),
    #                              ),
    #                     name = "Caliber",
    #                     default = '120')

    """ --------- Suspension --------- """
    # stiffness = FloatProperty(default = 60, name = 'Stiffness', min = 0.0)
    # damping = FloatProperty(default = 0.3, name = 'Damping', min = 0.0)
    # compression = FloatProperty(default = 0.5, name = 'Compression', min = 0.0)
    # max_travel = FloatProperty(default = 0.5, name = 'maxTravel', min = 0.0)
    # max_force = FloatProperty(default = 5000000, name = 'maxForce', min = 0.0)
    # wheel_friction = FloatProperty(default = 100, name = 'WheelFriction', min = 0.0)
    # roll_influence = FloatProperty(default = 0.1, name = 'RollInfluence', min = 0.0)
    # shoe_mesh = StringProperty(default = 'Shoe', name = 'ShoeMesh')

class JointProperties(bpy.types.PropertyGroup):
    jointType = EnumProperty(items = (('Revolute', 'Revolute', '1DOF rotation around Z axis', 1),
                                      ('Prismatic', 'Prismatic', '1DOF linear movement along Z axis', 2),
                                      ('2DOF', '2DOF', '2DOF connection, primary around Z then around X(assuming targeting with Y axis)', 3),
                                      ('Ball', 'Ball', '3DOF ball connection', 4)
                    ),
                    name = 'Joint Type',
                    default = 'Revolute'
                )

class ArmorProperties(bpy.types.PropertyGroup):
    armorClass = FloatProperty(default = 1, name = 'Class')

class DecalProperties(bpy.types.PropertyGroup):
    decalName = StringProperty(default = '', name = 'DecalName')

class MarkerProperties(bpy.types.PropertyGroup):
    type = EnumProperty(items = (('Camera', 'Camera', '', 1),
                                 ('Light', 'Light', '', 2),
                                 ('SmokeSource', 'SmokeSource', '', 3),
                                 ('DustSource', 'DustSource', '', 4),
                                 ('EndOfBarrel', 'End Of Barrel', '', 5),
                                 ('SpawnPoint', 'Spawn Point', 'oint where object can be spawned at game start', 6),
                                 ),
                        name = "Type",
                        default = 'Camera')

    """ --------- Camera --------- """
    cameraMode = EnumProperty(items = (('Free', 'Free', 'Free cam', 1),
                                       ('CopyPosition', 'CopyPosition', '', 2),
                                       ('CopyPlane', 'CopyPlane', '', 3),
                                       ('CopyTransform', 'CopyTransform', '', 4),
                                 ),
                        name = "Mode",
                        default = 'CopyPosition')
    cameraFOV = FloatProperty(default = 90, name = 'FOV', min = 70, max = 115)
    cameraOffset = FloatVectorProperty(default = (0,0,0), name = 'Offset', min = -5, max = 23)
    cameraInertia  = FloatProperty(default = 1, name = 'Inertia', min = 0, max = 50)
    """ --------- Light --------- """
    """ --------- SmokeSource --------- """
    """ --------- DustSource --------- """
    """ --------- GunType --------- """
    gunType = StringProperty(default = '', name = 'GunType')

class CommonProperties(bpy.types.PropertyGroup):
    '''Common module properties '''
    identifier = StringProperty(default = 'none', name= 'Identifier')
    propertyType = EnumProperty(items = (('Module', 'Module', 'Module visual model', 1),
                                         ('Part', 'Part', 'Have to be fully merged with module. Cant have slots attached', 7),
                                         ('Physical', 'Physical', 'Module physical model', 2),
                                         ('Armor', 'Armor', 'Module armor model', 3),
                                         ('Connector', 'Connector', 'Connects modules', 4),
                                         ('Decal', 'Decal', '...', 5),
                                         ('Marker', 'Marker', '...', 6),
                                         ('Scene', 'Scene', '...', 8),
                                 ),
                        name = "Property Type",
                        default = 'Part')

    moduleProps = PointerProperty(type = ModuleProperties)
    jointProps = PointerProperty(type = JointProperties)
    armorProps = PointerProperty(type = ArmorProperties)
    decalProps = PointerProperty(type = DecalProperties)
    markerProps = PointerProperty(type = MarkerProperties)
    isActive = BoolProperty(name = 'Active', default = True)
