
bl_info = {
    "name":         "PMK vehicle info",
    "author":       "DezerteR",
    "blender":      (2,7,6),
    "version":      (0,0,1),
    "location":     "File > Export > Tank config",
    "description":  "Export vehicle info",
    "category":     "Import-Export"
}

"""
moze dodac jakas automatyczna konwersje nazwy wezykiem z liczbami
do ladnej postaci ze spacjami? uprosci to troche
"""

import bpy
import mathutils
import string
from bpy_extras.io_utils import ExportHelper

def vec_from_to(a, b):
    return b.location - a.location
def obj_z_axis(obj):
    axis = obj.matrix_local*mathutils.Vector((0.0, 0.0, 1.0, 0.0))
    axis.normalize()
    return axis
def strf(number):
    return str("%.5f" %number)
def vec_to_str_0(vec):
    return '['+strf(vec.x)+', '+strf(vec.y)+', '+strf(vec.z)+', 0.0]'
def vec_to_str_1(vec):
    return '['+strf(vec.x)+', '+strf(vec.y)+', '+strf(vec.z)+', 1.0]'

right_vector = mathutils.Vector((1.0, 0.0, 0.0, 0.0))
up_vector = mathutils.Vector((0.0, 0.0, 1.0, 0.0))
forward_vector = mathutils.Vector((0.0, 1.0, 0.0, 0.0))
zero_position = mathutils.Vector((0.0, 0.0, 0.0, 1.0))

class TankInfoExporter(bpy.types.Operator, ExportHelper):
    bl_idname       = "vehicle_info.yml"
    bl_label        = "Vehicle info exporter"
    bl_options      = {'PRESET'}
    filename_ext    = ".yml"

    def execute(self, context):
        root = self.find_root(bpy.data.objects)
        file = open(self.filepath, 'w', encoding = 'utf8')
        self.start_model_exporting(file, root, '')
        file.close()

        return {'FINISHED'}

    def find_root(self, objects):
        for ob in objects:
            if ob.pmk.module_properties.module_class == 'Hull':
                return ob
    def write_tech_info(self, root):
        pass
    def start_model_exporting(self, file, obj, offset):
        file.write('Model:\n')
        self.write_common_properties(file, obj, offset)
        self.write_module_properties(file, obj, offset)
        self.write_object_slots(file, obj, offset)

    def write_module(self, file, parent_slot, obj, offset):
        self.write_common_properties(file, obj, offset)
        position_offset = vec_from_to(parent_slot, obj)
        file.write(offset + '    PositionOffset: ' + vec_to_str_0(position_offset) + '\n')
        self.write_module_properties(file, obj, offset)
        self.write_object_slots(file, obj, offset)

    def write_common_properties(self, file, obj, offset):
        file.write(offset + '  - Name: ' + obj.name + '\n')
        if obj.data is not None:
            file.write(offset + '    Mesh: ' + obj.data.name + '\n')
        file.write(offset + '    PrettyName: ' + obj.pmk.pretty_name + '\n')
        file.write(offset + '    Type: ' + str(obj.pmk.property_type) + '\n')
        file.write(offset + '    Enabled: ' + str(obj.pmk.enabled_to_use) + '\n')
        self.write_decals(file, obj, offset+'    ')
        self.write_markers(file, obj, offset+'    ')
        # self.write_markers(file, obj, offset+'    ')
        self.write_physics_properties(file, obj, offset+'    ')

    def write_module_properties(self, file, obj, offset):
        info = obj.pmk.module_properties
        file.write(offset + '    Class: ' + str(info.module_class) + '\n')
        file.write(offset + '    ClassData: ' + str(info.module_class) + '\n')

        if info.module_class == 'Hull':
            pass
        elif info.module_class == 'Turret':
            file.write(offset + '        Velocity: ' + strf(info.rotate_velocity) + '\n')
            file.write(offset + '        AmmoCapacity: ' + strf(info.ammo_capacity) + '\n')
        elif info.module_class == 'Mantlet':
            file.write(offset + '        Min: ' + strf(info.min_vertical) + '\n')
            file.write(offset + '        Max: ' + strf(info.max_vertical) + '\n')
        elif info.module_class == 'Gun':
            file.write(offset + '        Dispersion: ' + strf(info.dispersion) + '\n')
            file.write(offset + '        Accuracy: ' + strf(info.accuracy) + '\n')
            file.write(offset + '        Caliber: ' + str(info.caliber) + '\n')
        elif info.module_class == 'Suspension':
            self.write_suspension_properties(file, obj, offset+'    ')

    def find_collision(self, obj):
        for c in obj.children:
            if c.pmk.property_type == 'Collision':
                return c.name
        return "none"

    def write_physics_properties(self, file, obj, offset):
        file.write(offset + 'Physical:\n')
        file.write(offset + '    Mass: ' + strf(obj.pmk.collision_properties.mass) + '\n')
        file.write(offset + '    Collision: ' + self.find_collision(obj) + '\n')
    def get_slots(self, obj):
        out = []
        for child in obj.children:
            if child.pmk.property_type == 'Slot':
                out.append(child)
        return out
    def write_object_slots(self, file, obj, offset):
        slots = self.get_slots(obj)
        if len(slots) > 0:
            file.write(offset + '    Slots:' + '\n')
            offset = offset + '    '
            for slot in slots:
                self.write_slot_properties(file, slot, obj, offset)

    def write_slot_properties(self, file, slot, obj, offset):
        axis = obj_z_axis(slot)
        pivot = vec_from_to(obj, slot)

        file.write(offset + '  - SlotName: ' + slot.name + '\n')
        file.write(offset + '    Axis: ' + vec_to_str_0(axis) + '\n')
        file.write(offset + '    Pivot: ' + vec_to_str_1(pivot) + '\n')

        if len(slot.children) > 0:
            file.write(offset + '    Pinned: ' + '\n')

        for pinned in slot.children:
            self.write_module(file, slot, pinned, offset + '    ')


    # first left side, from begining
    def sort_wheels(self, wheels):
        return sorted(wheels, key = lambda x: (-x.location.y, x.location.x))
    def get_type(self, obj, type):
        out = []
        for child in obj.children:
            if child.pmk.module_properties.module_class == type:
                out.append(child)
        return self.sort_wheels(out)
    def write_suspension_properties(self, file, obj, offset):
        road_wheels = self.get_type(obj, 'RoadWheel')
        support_wheels = self.get_type(obj, 'SupportWheel')
        drive_sprocket = self.get_type(obj, 'DriveSprocket')
        idler_wheel = self.get_type(obj, 'IdlerWheel')

        file.write(offset + 'ShoeMesh: ' + obj.pmk.module_properties.shoe_mesh + '\n')
        file.write(offset + 'Origin: ' + vec_to_str_1(obj.location)+ '\n')
        # file.write(offset + 'Stiffness: ' + obj.pmk.stiffness + '\n')
        # file.write(offset + 'Damping: ' + obj.pmk.damping + '\n')
        # file.write(offset + 'Compression: ' + obj.pmk.compression + '\n')
        # file.write(offset + 'MaxTravel: ' + obj.pmk.max_travel + '\n')
        file.write(offset + 'RoadWheels:\n')
        for it in road_wheels:
            file.write(offset + '  - Name: ' + it.name+ '\n')
            file.write(offset + '    Axis: ' + vec_to_str_0(it.matrix_world*right_vector)+ '\n')
            file.write(offset + '    Dimension: ' + vec_to_str_0(it.dimensions)+ '\n')
            file.write(offset + '    Position: ' + vec_to_str_1(it.location)+ '\n')
        file.write(offset + 'SupportWheels:\n')
        for it in support_wheels:
            file.write(offset + '  - Name: ' + it.name+ '\n')
            file.write(offset + '    Axis: ' + vec_to_str_0(it.matrix_world*right_vector)+ '\n')
            file.write(offset + '    Dimension: ' + vec_to_str_0(it.dimensions)+ '\n')
            file.write(offset + '    Position: ' + vec_to_str_1(it.location)+ '\n')
        file.write(offset + 'DriveSprocket:\n')
        for it in drive_sprocket:
            file.write(offset + '  - Name: ' + it.name+ '\n')
            file.write(offset + '    Axis: ' + vec_to_str_0(it.matrix_world*right_vector)+ '\n')
            file.write(offset + '    Dimension: ' + vec_to_str_0(it.dimensions)+ '\n')
            file.write(offset + '    Position: ' + vec_to_str_1(it.location)+ '\n')
        file.write(offset + 'IdlerWheel:\n')
        for it in idler_wheel:
            file.write(offset + '  - Name: ' + it.name+ '\n')
            file.write(offset + '    Axis: ' + vec_to_str_0(it.matrix_world*right_vector)+ '\n')
            file.write(offset + '    Dimension: ' + vec_to_str_0(it.dimensions)+ '\n')
            file.write(offset + '    Position: ' + vec_to_str_1(it.location)+ '\n')
    def write_decals(self, file, obj, offset):
        decals = []
        for child in obj.children:
            if child.pmk.property_type == 'Decal':
                decals.append(child);
        if len(decals) > 0:
            file.write(offset + 'Decals:\n')
        for decal in decals:
            file.write(offset + '  - Layer: ' + decal.pmk.decal_properties.decal_name + '\n')
            file.write(offset + '    Scale: ' + vec_to_str_0(decal.scale) + '\n')
            file.write(offset + '    Position: ' + vec_to_str_1(vec_from_to(decal, obj)) + '\n')
            # file.write(offset + '    Position: ' + vec_to_str_1(decal.matrix_local*zero_position) + '\n')
            locx = decal.matrix_local*right_vector
            locx.normalize()
            locz = decal.matrix_local*up_vector
            locz.normalize()
            file.write(offset + '    LocX: ' + vec_to_str_0(locx) + '\n')
            file.write(offset + '    LocZ: ' + vec_to_str_0(locz) + '\n')
    def write_markers(self, file, obj, offset):
        markers = []
        for child in obj.children:
            if child.pmk.property_type == 'Marker':
                markers.append(child);
        if len(markers) > 0:
            file.write(offset + 'Markers:\n')
        for marker in markers:
            file.write(offset + '  - Type: ' + marker.pmk.marker_properties.type + '\n')
            if 'Camera' == marker.pmk.marker_properties.type:
                file.write(offset + '    Mode: ' + marker.pmk.marker_properties.camera_mode + '\n')

            file.write(offset + '    Position: ' + vec_to_str_1(vec_from_to(obj, marker)) + '\n')
            # file.write(offset + '    Position: ' + vec_to_str_1(marker.matrix_local*zero_position) + '\n')
            locx = marker.matrix_local*right_vector
            locx.normalize()
            locz = marker.matrix_local*up_vector
            locz.normalize()
            file.write(offset + '    LocX: ' + vec_to_str_0(locx) + '\n')
            file.write(offset + '    LocZ: ' + vec_to_str_0(locz) + '\n')


def menu_func(self, context):
    self.layout.operator(TankInfoExporter.bl_idname, text="PMK Tank Info(.yml)")

def register():
    bpy.utils.register_class(TankInfoExporter)
    # bpy.utils.register_module(__name__)
    bpy.types.INFO_MT_file_export.append(menu_func)
def unregister():
    # bpy.utils.unregister_module(__name__)
    bpy.utils.unregister_class(TankInfoExporter)
    bpy.types.INFO_MT_file_export.remove(menu_func)
if __name__ == "__main__":
    register()
