import bpy
import bmesh
import csv
import mathutils
from bpy_extras.io_utils import axis_conversion, orientation_helper
from bpy.props import (
    BoolProperty,
    IntProperty,
    IntVectorProperty,
    StringProperty,
)


bl_info = {
    "name": "CSV Importer",
    "author": "Puxtril",
    "version": (1, 0, 0),
    "blender": (2, 80, 0),
    "location": "File > Import-Export",
    "description": "Import CSV mesh dump",
    "category": "Import-Export",
}


@orientation_helper(axis_forward="Z", axis_up="Y")
class Import_CSV(bpy.types.Operator):
    """Imports .csv meshes"""
    bl_idname = "object.import_csv"
    bl_label = "Import csv"
    bl_options = {"PRESET", "UNDO"}
    filepath: bpy.props.StringProperty(subtype="FILE_PATH")
    filter_glob: StringProperty(default="*.csv", options={"HIDDEN"})

########################################################################
# General Properties

    mirrorVertX: bpy.props.BoolProperty(
        name="Mirror X",
        description="Mirror all the vertices across X axis",
        default=True,
    )
    vertexOrder: bpy.props.BoolProperty(
        name="Flip Winding",
        description="Reorder vertices in counter-clockwise order",
        default=False,
    )
    mirrorUV: bpy.props.BoolProperty(
        name="Mirror V",
        description="Flip UV Maps vertically",
        default=True,
    )
    cleanMesh: bpy.props.BoolProperty(
        name="Clean Mesh",
        description="Remove doubles and enable smooth shading",
        default=True,
    )
    positionIndex: bpy.props.IntVectorProperty(
        name="Positions",
        description="Column numbers (0 indexed) of vertex positions",
        size=3,
        min=0,
        soft_max=20,
        default=(2, 3, 4),
    )
    normalIndex: bpy.props.IntVectorProperty(
        name="Normals",
        description="Column numbers (0 indexed) of vertex normals",
        size=3,
        min=0,
        soft_max=20,
        default=(6, 7, 8),
    )

########################################################################
# UV properties

    uvCount: bpy.props.IntProperty(
        name="UV Map Count",
        description="Number of UV maps to import",
        min=0,
        max=5,
        default=1,
    )
    uvIndex0: bpy.props.IntVectorProperty(
        name="UV 1",
        description="Column numbers (0 indexed) of UV map",
        size=2,
        min=0,
        soft_max=20,
        default=(14, 15),
    )
    uvIndex1: bpy.props.IntVectorProperty(
        name="UV 2",
        description="Column numbers (0 indexed) of UV map",
        size=2,
        min=0,
        soft_max=20,
        default=(0, 0),
    )
    uvIndex2: bpy.props.IntVectorProperty(
        name="UV 3",
        description="Column numbers (0 indexed) of UV map",
        size=2,
        min=0,
        soft_max=20,
        default=(0, 0),
    )
    uvIndex3: bpy.props.IntVectorProperty(
        name="UV 4",
        description="Column numbers (0 indexed) of UV map",
        size=2,
        min=0,
        soft_max=20,
        default=(0, 0),
    )
    uvIndex4: bpy.props.IntVectorProperty(
        name="UV 5",
        description="Column numbers (0 indexed) of UV map",
        size=2,
        min=0,
        soft_max=20,
        default=(0, 0),
    )

########################################################################
# Vertex Color3 Properties

    color3Count: bpy.props.IntProperty(
        name="Vertex Color RGB Count",
        description="Number of Vertex Colors (RGB) to import",
        min=0,
        max=5,
        default=0,
    )
    color3Index0: bpy.props.IntVectorProperty(
        name="Vertex Color RGB 1",
        description="Column numbers (0 indexed) of Vertex Colors (RGB)",
        size=3,
        min=0,
        soft_max=20,
        default=(10, 11, 12),
    )
    color3Index1: bpy.props.IntVectorProperty(
        name="Vertex Color RGB 2",
        description="Column numbers (0 indexed) of Vertex Colors (RGB)",
        size=3,
        min=0,
        soft_max=20,
        default=(0, 0, 0),
    )
    color3Index2: bpy.props.IntVectorProperty(
        name="Vertex Color RGB 3",
        description="Column numbers (0 indexed) of Vertex Colors (RGB)",
        size=3,
        min=0,
        soft_max=20,
        default=(0, 0, 0),
    )
    color3Index3: bpy.props.IntVectorProperty(
        name="Vertex Color RGB 4",
        description="Column numbers (0 indexed) of Vertex Colors (RGB)",
        size=3,
        min=0,
        soft_max=20,
        default=(0, 0, 0),
    )
    color3Index4: bpy.props.IntVectorProperty(
        name="Vertex Color RGB 5",
        description="Column numbers (0 indexed) of Vertex Colors (RGB)",
        size=3,
        min=0,
        soft_max=20,
        default=(0, 0, 0),
    )

########################################################################
# Vertex Color Properties

    colorCount: bpy.props.IntProperty(
        name="Vertex Color Alpha Count",
        description="Number of Vertex Colors (Alpha) to import",
        min=0,
        max=5,
        default=0,
    )
    colorIndex0: bpy.props.IntProperty(
        name="Vertex Color Alpha 1",
        description="Column number (0 indexed) of Vertex Color (Alpha)",
        min=0,
        soft_max=20,
        default=0,
    )
    colorIndex1: bpy.props.IntProperty(
        name="Vertex Color Alpha 2",
        description="Column number (0 indexed) of Vertex Color (Alpha)",
        min=0,
        soft_max=20,
        default=0,
    )
    colorIndex2: bpy.props.IntProperty(
        name="Vertex Color Alpha 3",
        description="Column number (0 indexed) of Vertex Color (Alpha)",
        min=0,
        soft_max=20,
        default=0,
    )
    colorIndex3: bpy.props.IntProperty(
        name="Vertex Color Alpha 4",
        description="Column number (0 indexed) of Vertex Color (Alpha)",
        min=0,
        soft_max=20,
        default=0,
    )
    colorIndex4: bpy.props.IntProperty(
        name="Vertex Color Alpha 5",
        description="Column number (0 indexed) of Vertex Color (Alpha)",
        min=0,
        soft_max=20,
        default=0,
    )

########################################################################
# Operator Functions

    def execute(self, context):
        transformMatrix = axis_conversion(
            from_forward=self.axis_forward,
            from_up=self.axis_up,
        ).to_4x4()

        uvArgs = [self.uvIndex0, self.uvIndex1, self.uvIndex2, self.uvIndex3, self.uvIndex4,]
        color3Args = [self.color3Index0, self.color3Index1, self.color3Index2, self.color3Index3, self.color3Index4]
        colorArgs = [self.colorIndex0, self.colorIndex1, self.colorIndex2, self.colorIndex3, self.colorIndex4,]

        verts, faces, normals, uvs, color3s, colors = importCSV(
            self.filepath,
            self.positionIndex,
            self.normalIndex,
            uvArgs[: self.uvCount],
            color3Args[: self.color3Count],
            colorArgs[: self.colorCount],
            self.mirrorVertX,
            self.mirrorUV,
            self.vertexOrder,
        )

        meshObj = createMesh(verts, faces, normals, uvs, color3s, colors, transformMatrix)

        if self.cleanMesh:
            tempBmesh = bmesh.new()
            tempBmesh.from_mesh(meshObj.data)
            bmesh.ops.remove_doubles(tempBmesh, verts=tempBmesh.verts, dist=0.0001)
            for face in tempBmesh.faces:
                face.smooth = True
            tempBmesh.to_mesh(meshObj.data)
            tempBmesh.clear()
            meshObj.data.update()

        return {"FINISHED"}

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {"RUNNING_MODAL"}

    def draw(self, context):
        generalBox = self.layout.box()
        generalBox.prop(self, "axis_forward")
        generalBox.prop(self, "axis_up")
        row1 = generalBox.row()
        row1.prop(self, "mirrorVertX")
        row1.prop(self, "mirrorUV")
        row2 = generalBox.row()
        row2.prop(self, "cleanMesh")
        row2.prop(self, "vertexOrder")

        indexBox = self.layout.box()
        indexBoxRow = indexBox.row()
        indexBoxRow.column().prop(self, "positionIndex")
        indexBoxRow.column().prop(self, "normalIndex")

        uvBox = self.layout.box()
        uvBox.prop(self, "uvCount")
        for i in range(self.uvCount):
            uvBox.prop(self, f"uvIndex{i}")

        color3Box = self.layout.box()
        color3Box.prop(self, "color3Count")
        for i in range(self.color3Count):
            color3Box.prop(self, f"color3Index{i}")

        colorBox = self.layout.box()
        colorBox.prop(self, "colorCount")
        for i in range(self.colorCount):
            colorBox.prop(self, f"colorIndex{i}")


def importCSV(
    filepath: str,
    posIndicies: tuple,
    normIndicies: tuple,
    uvMapsIndicies: list,
    color3sIndicies: list,
    colorsIndicies: list,
    mirrorVertX: bool,
    mirrorUV: bool,
    flipVertOrder: bool,
):
    # list<tuple3<float>>
    vertices = []
    # list<tuple3<float>>
    normals = []
    # list<tuple3<int>>
    faces = []
    # list<list<tuple2<int>>>
    uvs = []
    for _ in range(len(uvMapsIndicies)):
        uvs.append([])
    # list<list<tuple3<float>>>
    color3s = []
    for _ in range(len(color3sIndicies)):
        color3s.append([])
    # list<list<float>>
    colors = []
    for _ in range(len(colorsIndicies)):
        colors.append([])

    x_mod = -1 if mirrorVertX else 1

    with open(filepath) as f:
        reader = csv.reader(f)
        next(reader)

        curFace = []
        for rowIndex, row in enumerate(reader):
            curVertexIndex = rowIndex

            # Position
            curPos = (
                float(row[posIndicies[0]]) * x_mod,
                float(row[posIndicies[1]]),
                float(row[posIndicies[2]]),
            )
            vertices.append(curPos)

            # Normals
            curNormal = (
                float(row[normIndicies[0]]),
                float(row[normIndicies[1]]),
                float(row[normIndicies[2]]),
            )
            normals.append(curNormal)

            # UV Maps
            for i in range(len(uvMapsIndicies)):
                curUV = (
                    float(row[uvMapsIndicies[i][0]]),
                    float(row[uvMapsIndicies[i][1]]),
                )
                if mirrorUV:
                    curUV = (curUV[0], 1 - curUV[1])
                uvs[i].append(curUV)

            # Vertex Colors3
            for i in range(len(color3sIndicies)):
                curColor3 = (
                    float(row[color3sIndicies[i][0]]),
                    float(row[color3sIndicies[i][1]]),
                    float(row[color3sIndicies[i][2]]),
                )
                color3s[i].append(curColor3)

            # Vertex Colors
            for i in range(len(colorsIndicies)):
                curColor = float(row[colorsIndicies[i]])
                colors[i].append(curColor)

            # Append Faces
            curFace.append(curVertexIndex)
            if len(curFace) > 2:
                if flipVertOrder:
                    faces.append((curFace[2], curFace[1], curFace[0]))
                else:
                    faces.append(curFace)
                curFace = []

        return vertices, faces, normals, uvs, color3s, colors


def createMesh(vertices, faces, normals, uvs, color3s, colors, transformMatrix):
    mesh = bpy.data.meshes.new("name")
    mesh.from_pydata(vertices, [], faces)

    # Normals
    for vertexIndex in range(len(mesh.vertices)):
        mesh.vertices[vertexIndex].normal = normals[vertexIndex]

    # UV Maps
    for uvIndex in range(len(uvs)):
        uvLayer = mesh.uv_layers.new(name=f"UV{uvIndex}")
        for vertexIndex in range(len(uvLayer.data)):
            uvLayer.data[vertexIndex].uv = uvs[uvIndex][vertexIndex]

    # Vertex Colors3
    for color3Index in range(len(color3s)):
        color3Layer = mesh.vertex_colors.new(name=f"rgb{color3Index}")
        for vertexIndex in range(len(color3Layer.data)):
            curCol3 = color3s[color3Index][vertexIndex]
            color3Layer.data[vertexIndex].color = [curCol3[0], curCol3[1], curCol3[2], 0]

    # Vertex Colors
    for colorIndex in range(len(colors)):
        colorLayer = mesh.vertex_colors.new(name=f"alpha{colorIndex}")
        for vertexIndex in range(len(colorLayer.data)):
            curCol = colors[colorIndex][vertexIndex]
            colorLayer.data[vertexIndex].color = [curCol, curCol, curCol, 0]

    obj = bpy.data.objects.new("name", mesh)
    obj.data.transform(transformMatrix)
    obj.matrix_world = mathutils.Matrix()
    bpy.context.scene.collection.objects.link(obj)
    return obj


def menuItem(self, context):
    self.layout.operator(Import_CSV.bl_idname, text="Mesh CSV (.csv)")


def register():
    bpy.utils.register_class(Import_CSV)
    bpy.types.TOPBAR_MT_file_import.append(menuItem)


def unregister():
    bpy.utils.unregister_class(Import_CSV)
    bpy.types.TOPBAR_MT_file_import.remove(menuItem)


if __name__ == "__main__":
    register()
