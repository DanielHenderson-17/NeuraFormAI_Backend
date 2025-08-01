// Import all dependencies from node_modules
import * as THREE from "three";
import { GLTFLoader } from "three/examples/jsm/loaders/GLTFLoader.js";
import { OrbitControls } from "three/examples/jsm/controls/OrbitControls.js";
import { VRMLoaderPlugin, VRMUtils } from "@pixiv/three-vrm";

// The rest of your VRM viewer code goes here
let scene, camera, renderer, vrm, controls, clock;

function init() {
  console.log("Starting script execution.");
  scene = new THREE.Scene();
  camera = new THREE.PerspectiveCamera(
    45,
    window.innerWidth / window.innerHeight,
    0.1,
    1000
  );
  camera.position.set(0, 1.5, 3);
  clock = new THREE.Clock();

  renderer = new THREE.WebGLRenderer({ antialias: true });
  renderer.setSize(window.innerWidth, window.innerHeight);
  renderer.setClearColor(0x00ff00);
  document.body.appendChild(renderer.domElement);

  controls = new OrbitControls(camera, renderer.domElement);
  controls.target.set(0, 1.4, 0);
  controls.update();

  const light = new THREE.DirectionalLight(0xffffff, 1);
  light.position.set(5, 10, 7.5);
  scene.add(light);
  const ambientLight = new THREE.AmbientLight(0xffffff, 0.5);
  scene.add(ambientLight);

  window.addEventListener("resize", onWindowResize, false);

  animate();
}

function animate() {
  requestAnimationFrame(animate);
  const delta = clock.getDelta();
  if (vrm) {
    vrm.update(delta);
  }
  controls.update();
  renderer.render(scene, camera);
}

function onWindowResize() {
  camera.aspect = window.innerWidth / window.innerHeight;
  camera.updateProjectionMatrix();
  renderer.setSize(window.innerWidth, window.innerHeight);
}

// ✅ Global function for Python
window.loadVRM = function (vrmPath) {
  console.log("Loading VRM:", vrmPath);
  if (vrm) {
    VRMUtils.deepDispose(vrm.scene);
    scene.remove(vrm.scene);
    vrm = null;
  }

  const loader = new GLTFLoader();
  loader.register((parser) => new VRMLoaderPlugin(parser));

  loader.load(
    vrmPath,
    function (gltf) {
      vrm = gltf.userData.vrm;
      if (vrm) {
        VRMUtils.rotateVRM0(vrm);
        scene.add(vrm.scene);
        console.log("VRM loaded successfully!");
      } else {
        console.error("The loaded GLTF is not a valid VRM.", gltf);
      }
    },
    undefined,
    function (error) {
      console.error("Error loading VRM:", error);
    }
  );
};

init();
// ✅ Global flag for Python
window.vrmViewerReady = true;
console.log("VRM Viewer ready signal sent to Python.");
