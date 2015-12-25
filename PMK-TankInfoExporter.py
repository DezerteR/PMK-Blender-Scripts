
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
def vec_to_str_0(vec):
    return '['+str(vec.x)+', '+str(vec.y)+', '+str(vec.z)+', 0.0]'
def vec_to_str_1(vec):
    return '['+str(vec.x)+', '+str(vec.y)+', '+str(vec.z)+', 1.0]'

class TankInfoExporter(bpy.types.Operator, ExportHelper):
    bl_idname       = "vehicle_info.yml"
    bl_label        = "Vehicle info exporter"
    bl_options      = {'PRESET'}
    filename_ext    = ".yml"

    def execute(self, context):
        root = self.find_root(bpy.data.objects)
        file = open(self.filepath, 'w', encoding = 'utf8')
        self.write_first_module(file, root, '')
        file.close()

        return {'FINISHED'}

    def find_root(self, objects):
        for ob in objects:
            if ob.common.moduleType == 'Hull':
                return ob
    def write_tech_info(self, root):
        pass
    def write_first_module(self, file, obj, offset):
        file.write('Model:\n')
        self.write_common_properties(file, obj, offset)
        self.write_module_properties(file, obj, offset)
        self.write_object_slots(file, obj, offset)

    def write_module(self, file, parent_slot, obj, offset):
        self.write_common_properties(file, obj, offset)
        self.write_module_properties(file, obj, offset)
        self.write_object_slots(file, obj, offset)

    def write_common_properties(self, file, obj, offset):
        file.write(offset + '  - Name: ' + obj.name + '\n')
        # if obj.data is not None:
            # file.write(offset + '    Mesh: ' + obj.data.name + '\n')
        file.write(offset + '    Pretty name: ' + obj.common.prettyName + '\n')
    def write_module_properties(self, file, obj, offset):
        if obj.common.moduleType == 'Hull':
            pass
        elif obj.common.moduleType == 'Turret':
            file.write(offset + '   Velocity: ' + obj.common.rotateVelocity + '\n')
            file.write(offset + '   Ammo capacity' + obj.common.rotateVelocity + '\n')
        elif obj.common.moduleType == 'Mantlet':
            file.write(offset + '   Min: ' + obj.common.minVertical + '\n')
            file.write(offset + '   Max: ' + obj.common.maxVertical + '\n')
        elif obj.common.moduleType == 'Gun':
            file.write(offset + '   Dispersion: ' + obj.common.dispersion + '\n')
            file.write(offset + '   Accuracy: ' + obj.common.accuracy + '\n')
            file.write(offset + '   Caliber: ' + obj.common.caliber + '\n')
        elif obj.common.moduleType == 'Suspension':
            write_suspension_properties(file, obj, offset)

    def write_physics_properties(self, file, obj, offset):
        pass
    def get_slots(self, obj):
        out = []
        for child in obj.children:
            if child.common.objectType == 'Slot':
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

        file.write(offset + '  - Name: ' + slot.name + '\n')
        file.write(offset + '    Axis: ' + vec_to_str_0(axis) + '\n')
        file.write(offset + '    Pivot: ' + vec_to_str_1(pivot) + '\n')

        for pinned in slot.children:
            self.write_module(file, slot, pinned, offset + '  ')
            return

    def write_suspension_properties(self, file, obj, offset):
        pass

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
