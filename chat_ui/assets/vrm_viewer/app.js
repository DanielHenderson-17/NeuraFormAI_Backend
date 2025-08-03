// Import all dependencies from node_modules
import * as THREE from "three";
import { GLTFLoader } from "three/examples/jsm/loaders/GLTFLoader.js";
import { OrbitControls } from "three/examples/jsm/controls/OrbitControls.js";
import { VRMLoaderPlugin, VRMUtils } from "@pixiv/three-vrm";

// The rest of your VRM viewer code goes here
let scene, camera, renderer, vrm, controls, clock;
let blinkTimer = 0;
let isBlinking = false;
let lastBlinkTime = 0;

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

  // === CORRECTED RENDERER SECTION ===
  // Add alpha: true to enable transparency
  renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
  renderer.setSize(window.innerWidth, window.innerHeight);
  // Set the clear alpha to 0 for a transparent background
  renderer.setClearAlpha(0);
  document.body.appendChild(renderer.domElement);
  // === END CORRECTED RENDERER SECTION ===

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
    updateBlinking(delta);
  }

  controls.update();
  renderer.render(scene, camera);
}

function updateBlinking(delta) {
  if (!vrm || !vrm.expressionManager) return;

  const currentTime = clock.getElapsedTime();

  // Random blink interval between 2-6 seconds
  if (!isBlinking && currentTime - lastBlinkTime > 2 + Math.random() * 4) {
    startBlink();
  }

  if (isBlinking) {
    blinkTimer += delta;

    // Blink duration is about 0.15 seconds
    if (blinkTimer >= 0.15) {
      endBlink();
    }
  }
}

function startBlink() {
  if (!vrm || !vrm.expressionManager) return;

  isBlinking = true;
  blinkTimer = 0;

  // Set blink expression to 1.0 (fully closed eyes)
  const blinkExpression = vrm.expressionManager.getExpression("blink");
  if (blinkExpression) {
    blinkExpression.weight = 1.0;
  }
}

function endBlink() {
  if (!vrm || !vrm.expressionManager) return;

  isBlinking = false;
  lastBlinkTime = clock.getElapsedTime();

  // Set blink expression back to 0.0 (open eyes)
  const blinkExpression = vrm.expressionManager.getExpression("blink");
  if (blinkExpression) {
    blinkExpression.weight = 0.0;
  }
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

        // Reset blink state for new model
        isBlinking = false;
        blinkTimer = 0;
        lastBlinkTime = clock.getElapsedTime();

        // Log available expressions for debugging
        if (vrm.expressionManager) {
          console.log(
            "Available expressions:",
            vrm.expressionManager.expressions.map((exp) => exp.expressionName)
          );
        }

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

// ✅ Global function to manually trigger blink
window.triggerBlink = function () {
  if (vrm && !isBlinking) {
    startBlink();
  }
};

init();
// ✅ Global flag for Python
window.vrmViewerReady = true;
console.log("VRM Viewer ready signal sent to Python.");
