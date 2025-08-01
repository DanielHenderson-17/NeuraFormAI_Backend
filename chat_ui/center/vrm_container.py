import struct
import base64
import io
from PyQt6.QtOpenGLWidgets import QOpenGLWidget
from PyQt6.QtWidgets import QSizePolicy
from OpenGL.GL import *
from OpenGL.GLU import *
from pygltflib import GLTF2
from PIL import Image
import os


class VRMContainer(QOpenGLWidget):
    """
    OpenGL-based VRM container for rendering 3D VRM models.
    Loads geometry, normals, textures, and UV coordinates.
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
        self.uv_coords = []
        self.face_materials = []

        # Texture handling
        self.pending_textures = []
        self.textures = {}

    def initializeGL(self):
        glEnable(GL_DEPTH_TEST)
        glClearColor(0.1, 0.1, 0.1, 1.0)
        glEnable(GL_LIGHTING)
        glEnable(GL_LIGHT0)
        glEnable(GL_COLOR_MATERIAL)
        glEnable(GL_TEXTURE_2D)
        glColorMaterial(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE)

        # Upload textures now that GL context is ready
        for i, (width, height, tex_data) in enumerate(self.pending_textures):
            tex_id = glGenTextures(1)
            glBindTexture(GL_TEXTURE_2D, tex_id)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
            glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, width, height, 0,
                         GL_RGBA, GL_UNSIGNED_BYTE, tex_data)
            self.textures[i] = tex_id
        self.pending_textures.clear()

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

        if self.textures:
            glEnable(GL_TEXTURE_2D)
            texture_id = next(iter(self.textures.values()))  # first texture
            glBindTexture(GL_TEXTURE_2D, texture_id)

            glBegin(GL_TRIANGLES)
            for face in self.faces:
                for vertex_index in face:
                    if vertex_index < len(self.uv_coords):
                        u, v = self.uv_coords[vertex_index]
                        glTexCoord2f(u, 1 - v)  # flip V-axis if needed
                    vx, vy, vz = self.vertices[vertex_index]
                    glVertex3f(vx, vy, vz)
            glEnd()
            glDisable(GL_TEXTURE_2D)
        else:
            glColor3f(0.6, 0.8, 1.0)
            glBegin(GL_TRIANGLES)
            for face in self.faces:
                for vertex_index in face:
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
            all_vertices, all_faces, all_normals, all_uvs = [], [], [], []
            face_materials = []

            # Load textures (defer OpenGL upload)
            for i, image in enumerate(model.images):
                if image.uri and image.uri.startswith("data:"):
                    _, encoded = image.uri.split(",", 1)
                    img_data = base64.b64decode(encoded)
                elif image.bufferView is not None:
                    bv = model.bufferViews[image.bufferView]
                    buf = model.buffers[bv.buffer]
                    raw = model.get_data_from_buffer_uri(buf.uri)
                    img_data = raw[bv.byteOffset:bv.byteOffset + bv.byteLength]
                else:
                    continue

                pil_img = Image.open(io.BytesIO(img_data)).convert("RGBA")
                tex_data = pil_img.tobytes("raw", "RGBA", 0, -1)
                self.pending_textures.append((pil_img.width, pil_img.height, tex_data))

            # Load mesh data
            for mesh in model.meshes:
                for primitive in mesh.primitives:
                    base_vertex_index = len(all_vertices)

                    # Vertices
                    pos_accessor = model.accessors[primitive.attributes.POSITION]
                    pos_view = model.bufferViews[pos_accessor.bufferView]
                    pos_buf = model.buffers[pos_view.buffer]
                    pos_raw = model.get_data_from_buffer_uri(pos_buf.uri)

                    stride = 12
                    vertices = []
                    for i in range(pos_accessor.count):
                        start = pos_view.byteOffset + (i * stride)
                        x, y, z = struct.unpack_from("<fff", pos_raw, start)
                        vertices.append((x, y, z))
                    all_vertices.extend(vertices)

                    # Normals
                    if getattr(primitive.attributes, "NORMAL", None) is not None:
                        norm_accessor = model.accessors[primitive.attributes.NORMAL]
                        norm_view = model.bufferViews[norm_accessor.bufferView]
                        norm_buf = model.buffers[norm_view.buffer]
                        norm_raw = model.get_data_from_buffer_uri(norm_buf.uri)

                        normals = []
                        for i in range(norm_accessor.count):
                            start = norm_view.byteOffset + (i * stride)
                            nx, ny, nz = struct.unpack_from("<fff", norm_raw, start)
                            normals.append((nx, ny, nz))
                        all_normals.extend(normals)
                    else:
                        all_normals.extend([(0, 0, 1)] * pos_accessor.count)

                    # UV Coordinates
                    uvs = [(0.0, 0.0)] * pos_accessor.count
                    if getattr(primitive.attributes, "TEXCOORD_0", None) is not None:
                        uv_accessor = model.accessors[primitive.attributes.TEXCOORD_0]
                        uv_view = model.bufferViews[uv_accessor.bufferView]
                        uv_buf = model.buffers[uv_view.buffer]
                        uv_raw = model.get_data_from_buffer_uri(uv_buf.uri)

                        for i in range(uv_accessor.count):
                            start = uv_view.byteOffset + (i * 8)
                            u, v = struct.unpack_from("<ff", uv_raw, start)
                            uvs[i] = (u, v)
                    all_uvs.extend(uvs)

                    # Faces
                    idx_accessor = model.accessors[primitive.indices]
                    idx_view = model.bufferViews[idx_accessor.bufferView]
                    idx_buf = model.buffers[idx_view.buffer]
                    idx_raw = model.get_data_from_buffer_uri(idx_buf.uri)

                    if idx_accessor.componentType == 5121:
                        fmt, step = "<BBB", 3
                    elif idx_accessor.componentType == 5123:
                        fmt, step = "<HHH", 6
                    else:
                        fmt, step = "<III", 12

                    for i in range(0, idx_accessor.count * (step // 3), step):
                        if i + step <= len(idx_raw):
                            v1, v2, v3 = struct.unpack_from(fmt, idx_raw, idx_view.byteOffset + i)
                            all_faces.append((base_vertex_index + v1,
                                              base_vertex_index + v2,
                                              base_vertex_index + v3))
                            face_materials.append(primitive.material or 0)

            # Normalize model
            xs = [v[0] for v in all_vertices]
            ys = [v[1] for v in all_vertices]
            zs = [v[2] for v in all_vertices]

            cx = (min(xs) + max(xs)) / 2
            cy = (min(ys) + max(ys)) / 2
            cz = (min(zs) + max(zs)) / 2
            max_dim = max(max(xs) - min(xs), max(ys) - min(ys), max(zs) - min(zs))
            scale = 2.0 / max_dim if max_dim > 0 else 1.0

            self.vertices = [((x - cx) * scale, (y - cy) * scale, (z - cz) * scale)
                             for x, y, z in all_vertices]
            self.faces = all_faces
            self.normals = all_normals
            self.uv_coords = all_uvs
            self.face_materials = face_materials

            print(f"✅ VRM loaded: {len(self.vertices)} vertices, {len(self.faces)} faces, "
                  f"{len(self.pending_textures)} textures pending upload, {len(self.uv_coords)} UVs.")
        except Exception as e:
            print(f"❌ Failed to load VRM with textures: {e}")
