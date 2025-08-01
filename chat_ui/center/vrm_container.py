import struct
import numpy as np
from PyQt6.QtOpenGLWidgets import QOpenGLWidget
from PyQt6.QtWidgets import QSizePolicy
from OpenGL.GL import *
from OpenGL.GLU import *
from pygltflib import GLTF2
import os


class VRMContainer(QOpenGLWidget):
    """
    OpenGL-based VRM container for rendering 3D VRM models.
    Now calculates normals for proper lighting.
    """

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Expanding)
        self.setMinimumHeight(300)

        self.setStyleSheet("background-color: black; border: 2px solid red;")

        self.vrm_path = None
        self.rotation_angle = 0.0
        self.vertices = []
        self.faces = []
        self.normals = []

    def initializeGL(self):
        glEnable(GL_DEPTH_TEST)
        glClearColor(0.1, 0.1, 0.1, 1.0)
        glEnable(GL_LIGHTING)
        glEnable(GL_LIGHT0)
        glEnable(GL_COLOR_MATERIAL)
        glEnable(GL_NORMALIZE)  # Auto normalize normals
        glColorMaterial(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE)

    def resizeGL(self, width, height):
        glViewport(0, 0, width, height)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(45.0, width / max(1, height), 0.1, 100.0)
        glMatrixMode(GL_MODELVIEW)

    def paintGL(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()
        gluLookAt(0, 1.5, 5, 0, 1, 0, 0, 1, 0)

        self.rotation_angle += 0.2
        glRotatef(self.rotation_angle, 0, 1, 0)

        glColor3f(0.8, 0.8, 1.0)
        glBegin(GL_TRIANGLES)
        for i, face in enumerate(self.faces):
            for j, vertex_index in enumerate(face):
                if vertex_index < len(self.vertices):
                    nx, ny, nz = self.normals[i]
                    glNormal3f(nx, ny, nz)
                    vx, vy, vz = self.vertices[vertex_index]
                    glVertex3f(vx, vy, vz)
        glEnd()

        self.update()

    def load_vrm(self, vrm_path: str):
        if not os.path.exists(vrm_path):
            print(f"❌ VRM file not found: {vrm_path}")
            return

        self.vrm_path = vrm_path
        print(f"🟢 [VRMContainer] Loading VRM: {vrm_path}")

        try:
            model = GLTF2.load_binary(vrm_path)

            all_vertices = []
            all_faces = []

            for mesh in model.meshes:
                for primitive in mesh.primitives:
                    pos_accessor = model.accessors[primitive.attributes.POSITION]
                    pos_buffer_view = model.bufferViews[pos_accessor.bufferView]
                    pos_buffer = model.buffers[pos_buffer_view.buffer]
                    pos_data = model.get_data_from_buffer_uri(pos_buffer.uri)

                    stride = 12
                    base_vertex_index = len(all_vertices)
                    vertices = []
                    for i in range(pos_accessor.count):
                        start = pos_buffer_view.byteOffset + (i * stride)
                        x, y, z = struct.unpack_from("<fff", pos_data, start)
                        vertices.append((x, y, z))
                    all_vertices.extend(vertices)

                    idx_accessor = model.accessors[primitive.indices]
                    idx_buffer_view = model.bufferViews[idx_accessor.bufferView]
                    idx_buffer = model.buffers[idx_buffer_view.buffer]
                    idx_data = model.get_data_from_buffer_uri(idx_buffer.uri)

                    if idx_accessor.componentType == 5121:
                        fmt = "<BBB"
                        step = 3
                        stride_idx = 1
                    elif idx_accessor.componentType == 5123:
                        fmt = "<HHH"
                        step = 6
                        stride_idx = 2
                    else:
                        fmt = "<III"
                        step = 12
                        stride_idx = 4

                    faces = []
                    for i in range(0, idx_accessor.count * stride_idx, step):
                        if i + step <= len(idx_data):
                            v1, v2, v3 = struct.unpack_from(fmt, idx_data, idx_buffer_view.byteOffset + i)
                            faces.append((base_vertex_index + v1, base_vertex_index + v2, base_vertex_index + v3))
                    all_faces.extend(faces)

            xs = [v[0] for v in all_vertices]
            ys = [v[1] for v in all_vertices]
            zs = [v[2] for v in all_vertices]

            center_x = (min(xs) + max(xs)) / 2
            center_y = (min(ys) + max(ys)) / 2
            center_z = (min(zs) + max(zs)) / 2
            max_dim = max(max(xs) - min(xs), max(ys) - min(ys), max(zs) - min(zs))
            scale_factor = 2.0 / max_dim if max_dim > 0 else 1.0

            self.vertices = [
                ((x - center_x) * scale_factor, (y - center_y) * scale_factor, (z - center_z) * scale_factor)
                for x, y, z in all_vertices
            ]
            self.faces = all_faces

            # === NEW: Calculate normals ===
            normals = []
            verts_np = np.array(self.vertices)
            for face in self.faces:
                v1, v2, v3 = [verts_np[idx] for idx in face]
                normal = np.cross(v2 - v1, v3 - v1)
                normal = normal / (np.linalg.norm(normal) + 1e-8)
                normals.append(normal)
            self.normals = normals

            print(f"✅ VRM loaded: {len(self.vertices)} vertices, {len(self.faces)} faces with normals")
        except Exception as e:
            print(f"❌ Failed to load VRM: {e}")
