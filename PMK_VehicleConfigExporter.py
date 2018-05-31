﻿
bl_info = {
    "name":         "PMK Vehicle Config File Exporter",
    "author":       "Karol Wajs",
    "blender":      (2,7,7),
    "version":      (0,1,0),
    "location":     "config > Export > Vehicle Config File",
    "description":  "Export vehicle module configuration",
    "category":     "Import-Export"
}

import bpy, mathutils
import string, os
from collections import OrderedDict
import SimpleYaml
from bpy_extras.io_utils import ExportHelper

def vecFromTo(a, b):
    return b.location - a.location
def objUpAxis(thing):
    axis = thing.matrix_local*mathutils.Vector((0.0, 0.0, 1.0, 0.0))
    axis.normalize()
    return axis

vecRight = mathutils.Vector((1.0, 0.0, 0.0, 0.0))
becUp = mathutils.Vector((0.0, 0.0, 1.0, 0.0))
vecForward = mathutils.Vector((0.0, 1.0, 0.0, 0.0))
zeroPosition = mathutils.Vector((0.0, 0.0, 0.0, 1.0))

class TankInfoExporter(bpy.types.Operator, ExportHelper):
    bl_idname       = "vehicle_info.yaml"
    bl_label        = "Vehicle config exporter"
    bl_options      = {'PRESET'}
    filename_ext    = ".yml"

    def execute(self, context):
        root = self.findRoot(bpy.data.objects)
        config = OrderedDict()
        config["Model"] = self.getModule(root, None)

        with open(self.filepath, 'w') as fp:
            SimpleYaml.writeYamlTo(fp, config)


        path = os.path.dirname(self.filepath)
        name = os.path.splitext(os.path.split(self.filepath)[1])[0]

        bpy.ops.wm.collada_export(
            filepath = os.path.join(path, name+".dae"),
            check_existing = False,
            apply_modifiers = True,
            triangulate = True,
            use_object_instantiation = False
        )

        return {'FINISHED'}

    def findRoot(self, objects):
        for ob in objects:
            if ob.pmk.moduleProps.moduleType == 'Base':
                return ob

    # * recursively construct module
    def getModule(self, thing, parentSlot):
        module = self.createModule(thing)
        module["Name"] =  thing.name
        if thing.data is not None:
            module["Models"] = self.getMeshes(thing)
        module["Identifier"] = thing.pmk.identifier
        module["Type"] = thing.pmk.propertyType
        module["Active"] = thing.pmk.isActive

        self.appendDecals(module, thing)
        self.appendMarkers(module, thing)
        self.appendPhysical(module, thing)
        print(parentSlot)
        if parentSlot:
            self.appendConstraints(module, parentSlot, thing)
        self.appendConnectors(module, thing)

        return module

    def createModule(self, thing):
        config = OrderedDict()
        info = thing.pmk.moduleProps
        config["ModuleType"] = str(info.moduleType)

        if info.moduleType == 'Suspension':
            self.writeSuspensionProperties(config, thing)

        return config

    # * find all meshes with type{Module, Part} directly connected to object, they have to be merged in one in engine
    def getMeshes(self, thing):
        # // out = [thing.data.name] 'cos using object names, not mesh names
        out = [thing.name]
        for child in thing.children:
            if child.pmk.propertyType == 'Part' and child.data is not None:
                # // out.append(child.data.name) 'cos using object names, not mesh names
                out.append(child.name)
        return out

    def appendPhysical(self, config, thing):
        if thing.rigid_body is None: return

        config["Physical"] = {}
        config["Physical"]["Mass"] = thing.rigid_body.mass
        config["Physical"]["CollisionModels"] = self.findPhysicalModels(thing)
        # TODO: add bounding box

    def findPhysicalModels(self, thing):
        out = []
        for c in thing.children:
            if c.pmk.propertyType == 'Collision':
                # // out.append(c.data.name) 'cos using object names, not mesh names
                out.append(c.name)
        return "none"

    def getConnectors(self, thing):
        out = []
        for child in thing.children:
            if child.pmk.propertyType == 'Connector':
                out.append(child)
        return out
    def appendConnectors(self, config, parentThing):
        slots = self.getConnectors(parentThing)
        if len(slots) > 0:
            config["Connector"] = []
            for slot in slots:
                config["Connector"].append(self.getConnectorProperties(slot, parentThing))

    # * I didn't found usage for linear constraints
    def appendConstraints(self, config, parentSlot, thing):
        config["FromParentToOrigin"] = vecFromTo(parentSlot, thing)

        if not "Limit Rotation" in thing.constraints:
            return

        c = thing.constraints["Limit Rotation"]

        config["hasLimits"] = [c.use_limit_x, c.use_limit_y, c.use_limit_z]
        config["Min"] = [c.min_x, c.min_y, c.min_z]
        config["Max"] = [c.max_x, c.max_y, c.max_z]

    # * axis of rotation is coded in slot Z axis
    # * constraints in object constraints
    def getConnectorProperties(self, slot, parentThing):
        out = OrderedDict()
        out["Name"] = slot.name
        out["Axis"] = objUpAxis(slot) # * useful only for visuals?
        out["FromParentOrigin"] = vecFromTo(parentThing, slot)

        if len(slot.children) > 0:
            constraintAxis = mathutils.Vector()
            out["Pinned"] = []
            for pinned in slot.children:
                out["Pinned"].append(self.getModule(pinned, slot))

        return out

    # * first left side, from begining
    def get_connection(self, thing, to_origin):
        res = OrderedDict()
        res["toOrigin"] = to_origin
        res["MaxV"] = 15
        res["Limits"] = [-15, 15]

        return res
    def sort_wheels(self, wheels):
        return sorted(wheels, key = lambda x: (-x.location.y, x.location.x))
    def get_type(self, thing, type):
        out = []
        for child in thing.children:
            if child.pmk.moduleProps.moduleType == type:
                out.append(child)
        return self.sort_wheels(out)
    def writeSuspensionProperties(self, config, thing):
        road_wheels = self.get_type(thing, 'RoadWheel')
        support_wheels = self.get_type(thing, 'SupportWheel')
        drive_sprocket = self.get_type(thing, 'DriveSprocket')
        idler_wheel = self.get_type(thing, 'IdlerWheel')

        config["ShoeMesh"] = thing.pmk.moduleProps.shoe_mesh
        config["toOrigin"] = vec_to_str_1(thing.location)
        config["Stiffness"] = 10 #thing.pmk.stiffness
        config["Damping"] = 1 #thing.pmk.damping
        config["Compression"] = 1 #thing.pmk.compression
        config["MaxTravel"] = 0.5 #thing.pmk.max_travel

        config["RoadWheels"] = []
        for it in road_wheels:
            config["RoadWheels"].append({
                "Name"      : it.name,
                "Axis"      : it.matrix_world*vecRight,
                "Dimension" : it.dimensions,
                "Position"  : it.location
            })
        config["SupportWheels"] = []
        for it in road_wheels:
            config["SupportWheels"].append({
                "Name"      : it.name,
                "Axis"      : it.matrix_world*vecRight,
                "Dimension" : it.dimensions,
                "Position"  : it.location
            })
        config["DriveSprocket"] = []
        for it in road_wheels:
            config["DriveSprocket"].append({
                "Name"      : it.name,
                "Axis"      : it.matrix_world*vecRight,
                "Dimension" : it.dimensions,
                "Position"  : it.location
            })
        config["IdlerWheel"] = []
        for it in road_wheels:
            config["IdlerWheel"].append({
                "Name"      : it.name,
                "Axis"      : it.matrix_world*vecRight,
                "Dimension" : it.dimensions,
                "Position"  : it.location
            })

    def appendDecals(self, config, thing):
        decals = []
        for child in thing.children:
            if child.pmk.propertyType == 'Decal':
                decals.append(child);
        if len(decals) == 0:
            return

        config["Decals"] = []
        for decal in decals:
            locx = decal.matrix_local*vecRight
            locx.normalize()
            locz = decal.matrix_local*becUp
            locz.normalize()
            config["Decals"].append({
                "Layer"     : decal.pmk.decalProps.decalName,
                "Scale"     : decal.scale,
                "Position"  : vecFromTo(decal, thing),
                "LocX"      : locx,
                "LocZ"      : loc
            })

    def appendMarkers(self, config, thing):
        markers = []
        for child in thing.children:
            if child.pmk.propertyType == 'Marker':
                markers.append(child);
        if len(markers) == 0:
            return

        config["Markers"] = []
        for marker in markers:
            locx = marker.matrix_local*vecRight
            locx.normalize()
            locz = marker.matrix_local*becUp
            locz.normalize()
            config["Markers"].append({
                "Type" : marker.pmk.markerProps.type,
                "Position" : vecFromTo(thing, marker),
                "LocX" : locx,
                "LocZ" : locz
            })

            if 'Camera' == marker.pmk.markerProps.type:
                config["Markers"][-1]["Mode"] = marker.pmk.markerProps.cameraMode

def menu_func(self, context):
    self.layout.operator(TankInfoExporter.bl_idname, text="PMK Vehicle Config(.yml)")

def register():
    bpy.utils.register_class(TankInfoExporter)
    bpy.types.INFO_MT_file_export.append(menu_func)

def unregister():
    bpy.utils.unregister_class(TankInfoExporter)
    bpy.types.INFO_MT_file_export.remove(menu_func)

if __name__ == "__main__":
    register()
