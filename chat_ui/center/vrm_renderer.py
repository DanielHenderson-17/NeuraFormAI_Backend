import os
from PyQt6.Qt3DCore import QEntity, QTransform
from PyQt6.Qt3DRender import QCamera, QMesh, QPointLight
from PyQt6.Qt3DExtras import Qt3DWindow, QForwardRenderer, QOrbitCameraController, QPhongMaterial
from PyQt6.QtGui import QColor, QVector3D
from PyQt6.QtCore import QUrl
from PyQt6.QtWidgets import QWidget, QVBoxLayout


class VRMRenderer(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.view = Qt3DWindow()
        self.view.defaultFrameGraph().setClearColor(QColor("white"))
        
        self.root_entity = self._create_scene()
        self.view.setRootEntity(self.root_entity)

        container = QWidget.createWindowContainer(self.view)
        layout = QVBoxLayout(self)
        layout.addWidget(container)
        
        self.vrm_entity = None
        self.camera_entity = None
        self.current_vrm_path = None
        
        print("✅ VRMRenderer initialized.")

    def _create_scene(self):
        """Sets up the basic scene, camera, and camera controller."""
        root = QEntity()

        # Camera
        self.camera_entity = QCamera(root)
        self.camera_entity.lens().setPerspectiveProjection(45.0, 16 / 9, 0.1, 1000.0)
        self.camera_entity.setPosition(QVector3D(0.0, 1.5, 5.0))
        self.camera_entity.setUpVector(QVector3D(0.0, 1.0, 0.0))
        self.camera_entity.setViewCenter(QVector3D(0.0, 1.0, 0.0))

        # Camera controller
        cam_controller = QOrbitCameraController(root)
        cam_controller.setCamera(self.camera_entity)
        cam_controller.setLookSpeed(50.0)
        cam_controller.setLinearSpeed(50.0)

        # Light source
        light_entity = QEntity(root)
        light = QPointLight(light_entity)
        light.setColor(QColor("white"))
        light_entity.addComponent(light)
        light_transform = QTransform(light_entity)
        light_transform.setTranslation(QVector3D(0.0, 5.0, 5.0))
        light_entity.addComponent(light_transform)

        return root

    def load_vrm(self, vrm_path: str):
        """Load VRM or GLB model using QMesh (no manual decoding)."""
        if not os.path.exists(vrm_path):
            print(f"❌ VRM file not found: {vrm_path}")
            return
        
        if self.vrm_entity:
            self.vrm_entity.setParent(None)
            self.vrm_entity = None

        self.current_vrm_path = vrm_path
        print(f"🟢 Loading VRM model via QMesh: {vrm_path}")

        self.vrm_entity = QEntity(self.root_entity)
        
        mesh = QMesh()
        mesh.setSource(QUrl.fromLocalFile(os.path.abspath(vrm_path)))
        self.vrm_entity.addComponent(mesh)

        material = QPhongMaterial(self.vrm_entity)
        material.setDiffuse(QColor("blue"))
        self.vrm_entity.addComponent(material)

        print("✅ VRM file loaded successfully.")
