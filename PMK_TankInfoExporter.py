
bl_info = {
    "name":         "PMK vehicle info",
    "author":       "DezerteR",
    "blender":      (2,7,7),
    "version":      (0,1,0),
    "location":     "config > Export > Tank config",
    "description":  "Export vehicle info",
    "category":     "Import-Export"
}

import bpy
import mathutils
import string
import SimpleYaml
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
    bl_idname       = "vehicle_info.yaml"
    bl_label        = "Vehicle info exporter"
    bl_options      = {'PRESET'}
    filename_ext    = ".yml"

    def execute(self, context):
        root = self.find_root(bpy.data.objects)
        config = {}
        config["Model"] = self.write_module(root, None)

        with open(self.filepath, 'w') as fp:
            SimpleYaml.write_yaml_to(fp, config)

        # dump =  yaml.dump(config, default_flow_style=False)
        # file = open(self.filepath, 'w', encoding = 'utf8')
        # file.write(dump)
        # file.close()

        return {'FINISHED'}

    def find_root(self, objects):
        for ob in objects:
            if ob.pmk.module_properties.module_class == 'Hull':
                return ob

    def write_module(self, obj, parent_slot):
        module = self.create_module(obj)
        module["Name"] =  obj.name
        if obj.data is not None:
            module["Mesh"] = obj.data.name
        module["PrettyName"] = obj.pmk.pretty_name
        module["Module"] = str(obj.pmk.property_type)
        module["Enabled"] = str(obj.pmk.enabled_to_use)

        self.append_decals(module, obj)
        self.append_markers(module, obj)
        self.append_physical(module, obj)
        self.append_slots(module, obj)

        if parent_slot is not None:
            to_origin = vec_from_to(parent_slot, obj)
            module["Connection"] = self.get_connection(obj, vec_to_str_0(to_origin))

        return module

    def create_module(self, obj):
        config = {}
        info = obj.pmk.module_properties
        config["Class"] = str(info.module_class)

        if info.module_class == 'Hull':
            pass
        elif info.module_class == 'Turret':
            config["AmmoCapacity"] = info.ammo_capacity
        elif info.module_class == 'Mantlet':
            pass
        elif info.module_class == 'Gun':
            config["GameplaySpecific"] = {}
            config["GameplaySpecific"]["Dispersion"] = info.dispersion
            config["GameplaySpecific"]["Accuracy"] = info.accuracy
            config["GameplaySpecific"]["Caliber"] = info.caliber
        elif info.module_class == 'Suspension':
            self.write_suspension_properties(config, obj)

        return config

    def find_collision(self, obj):
        for c in obj.children:
            if c.pmk.property_type == 'Collision':
                return c.name
        return "none"

    def append_physical(self, config, obj):
        config["Physical"] = {}
        config["Physical"]["Mass"] = strf(obj.pmk.collision_properties.mass)
        config["Physical"]["Collision"] = self.find_collision(obj)
    def get_slots(self, obj):
        out = []
        for child in obj.children:
            if child.pmk.property_type == 'Slot':
                out.append(child)
        return out
    def append_slots(self, config, parent):
        slots = self.get_slots(parent)
        if len(slots) > 0:
            config["Slots"] = {}
            for slot in slots:
                config["Slots"][slot.name] = self.get_slot(slot, parent)

    def get_slot(self, slot, parent):
        res = {}
        axis = obj_z_axis(slot)
        to_pivot = vec_from_to(parent, slot)

        res["Axis"] = vec_to_str_0(axis)
        res["toPivot"] = vec_to_str_1(to_pivot)

        if len(slot.children) > 0:
            res["Pinned"] = []
            for pinned in slot.children:
                res["Pinned"] = self.write_module(pinned, slot)

        return res
    # first left side, from begining
    def get_connection(self, obj, to_origin):
        res = {}
        res["toOrigin"] = to_origin
        res["MaxV"] = 15
        res["Limits"] = [-15, 15]

        return res
    def sort_wheels(self, wheels):
        return sorted(wheels, key = lambda x: (-x.location.y, x.location.x))
    def get_type(self, obj, type):
        out = []
        for child in obj.children:
            if child.pmk.module_properties.module_class == type:
                out.append(child)
        return self.sort_wheels(out)
    def write_suspension_properties(self, config, obj):
        road_wheels = self.get_type(obj, 'RoadWheel')
        support_wheels = self.get_type(obj, 'SupportWheel')
        drive_sprocket = self.get_type(obj, 'DriveSprocket')
        idler_wheel = self.get_type(obj, 'IdlerWheel')

        config["ShoeMesh"] = obj.pmk.module_properties.shoe_mesh
        config["toOrigin"] = vec_to_str_1(obj.location)
        config["Stiffness"] = 10 #obj.pmk.stiffness
        config["Damping"] = 1 #obj.pmk.damping
        config["Compression"] = 1 #obj.pmk.compression
        config["MaxTravel"] = 0.5 #obj.pmk.max_travel

        config["RoadWheels"] = []
        for it in road_wheels:
            config["RoadWheels"].append({
                "Name"      : it.name,
                "Axis"      : vec_to_str_0(it.matrix_world*right_vector),
                "Dimension" : vec_to_str_0(it.dimensions),
                "Position"  : vec_to_str_1(it.location)
            })
        config["SupportWheels"] = []
        for it in road_wheels:
            config["SupportWheels"].append({
                "Name"      : it.name,
                "Axis"      : vec_to_str_0(it.matrix_world*right_vector),
                "Dimension" : vec_to_str_0(it.dimensions),
                "Position"  : vec_to_str_1(it.location)
            })
        config["DriveSprocket"] = []
        for it in road_wheels:
            config["DriveSprocket"].append({
                "Name"      : it.name,
                "Axis"      : vec_to_str_0(it.matrix_world*right_vector),
                "Dimension" : vec_to_str_0(it.dimensions),
                "Position"  : vec_to_str_1(it.location)
            })
        config["IdlerWheel"] = []
        for it in road_wheels:
            config["IdlerWheel"].append({
                "Name"      : it.name,
                "Axis"      : vec_to_str_0(it.matrix_world*right_vector),
                "Dimension" : vec_to_str_0(it.dimensions),
                "Position"  : vec_to_str_1(it.location)
            })

    def append_decals(self, config, obj):
        decals = []
        for child in obj.children:
            if child.pmk.property_type == 'Decal':
                decals.append(child);
        if len(decals) == 0:
            return

        config["Decals"] = []
        for decal in decals:
            locx = decal.matrix_local*right_vector
            locx.normalize()
            locz = decal.matrix_local*up_vector
            locz.normalize()
            config["Decals"].append({
                "Layer"     : decal.pmk.decal_properties.decal_name,
                "Scale"     : vec_to_str_0(decal.scale),
                "Position"  : vec_to_str_1(vec_from_to(decal, obj)),
                "LocX"      :  vec_to_str_0(locx),
                "LocZ"      : vec_to_str_0(locz)
            })

    def append_markers(self, config, obj):
        markers = []
        for child in obj.children:
            if child.pmk.property_type == 'Marker':
                markers.append(child);
        if len(markers) == 0:
            return

        config["Markers"] = []
        for marker in markers:
            locx = marker.matrix_local*right_vector
            locx.normalize()
            locz = marker.matrix_local*up_vector
            locz.normalize()
            config["Markers"].append({
                "Type" : marker.pmk.marker_properties.type,
                "Position" : vec_to_str_1(vec_from_to(obj, marker)),
                "LocX" : vec_to_str_0(locx),
                "LocZ" : vec_to_str_0(locz)
            })

            if 'Camera' == marker.pmk.marker_properties.type:
                config["Markers"][-1]["Mode"] = marker.pmk.marker_properties.camera_mode

def menu_func(self, context):
    self.layout.operator(TankInfoExporter.bl_idname, text="PMK Tank Info(.yml)")

def register():
    bpy.utils.register_class(TankInfoExporter)
    bpy.types.INFO_MT_file_export.append(menu_func)
def unregister():
    bpy.utils.unregister_class(TankInfoExporter)
    bpy.types.INFO_MT_file_export.remove(menu_func)
if __name__ == "__main__":
    register()
