import bpy, bmesh
from bpy import context as C
from mathutils import Vector


def scene_bounds():
    meshes = [o for o in bpy.data.objects if o.type == 'MESH']

    minV = Vector((min([min([co[0] for co in m.bound_box]) for m in meshes]),
                   min([min([co[1] for co in m.bound_box]) for m in meshes]),
                   min([min([co[2] for co in m.bound_box]) for m in meshes])))

    maxV = Vector((max([max([co[0] for co in m.bound_box]) for m in meshes]),
                   max([max([co[1] for co in m.bound_box]) for m in meshes]),
                   max([max([co[2] for co in m.bound_box]) for m in meshes])))

    return minV, maxV

bpy.ops.object.mode_set(mode='EDIT')

bm = bmesh.from_edit_mesh(C.object.data)

edges = []

parts = 32

minV, maxV = scene_bounds()
print("**", minV)
print("**", maxV)

dim = max(maxV.x - minV.x, maxV.y - minV.y) + 4
center = (maxV + minV)/2.0
step = dim/parts

start = center - Vector((dim*0.5, dim*0.5, 0))

parts = 0

for i in range(parts):
        ret = bmesh.ops.bisect_plane(bm, geom=bm.verts[:]+bm.edges[:]+bm.faces[:], plane_co=(start.x + i * step,0,0), plane_no=(-1,0,0))
        bmesh.ops.split_edges(bm, edges=[e for e in ret['geom_cut'] if isinstance(e, bmesh.types.BMEdge)])

for i in range(parts):
        ret = bmesh.ops.bisect_plane(bm, geom=bm.verts[:]+bm.edges[:]+bm.faces[:], plane_co=(0,start.y + i * step,0), plane_no=(0,1,0))
        bmesh.ops.split_edges(bm, edges=[e for e in ret['geom_cut'] if isinstance(e, bmesh.types.BMEdge)])

bmesh.update_edit_mesh(C.object.data)

bpy.ops.mesh.separate(type='LOOSE')
bpy.ops.object.mode_set(mode='OBJECT')
