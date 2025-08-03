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

// ✅ Global function to set any expression
window.setExpression = function (expressionName, weight = 1.0) {
  if (!vrm || !vrm.expressionManager) {
    console.warn("VRM or expression manager not available");
    return false;
  }

  const expression = vrm.expressionManager.getExpression(expressionName);
  if (expression) {
    expression.weight = Math.max(0.0, Math.min(1.0, weight));
    console.log(
      `Set expression "${expressionName}" to weight ${expression.weight}`
    );
    return true;
  } else {
    console.warn(`Expression "${expressionName}" not found`);
    return false;
  }
};

// ✅ Global function to reset all expressions to neutral
window.resetExpressions = function () {
  if (!vrm || !vrm.expressionManager) {
    console.warn("VRM or expression manager not available");
    return false;
  }

  // Reset all expressions to 0
  vrm.expressionManager.expressions.forEach((expression) => {
    expression.weight = 0.0;
  });

  // Set neutral to 1.0
  const neutralExpression = vrm.expressionManager.getExpression("neutral");
  if (neutralExpression) {
    neutralExpression.weight = 1.0;
  }

  console.log("Reset all expressions to neutral");
  return true;
};

// ✅ Global function to get list of available expressions
window.getAvailableExpressions = function () {
  if (!vrm || !vrm.expressionManager) {
    return [];
  }

  return vrm.expressionManager.expressions.map((exp) => exp.expressionName);
};

// ✅ Global function to set emotional expression
window.setEmotion = function (emotion) {
  const emotionMap = {
    happy: "happy",
    joy: "happy",
    angry: "angry",
    mad: "angry",
    relaxed: "relaxed",
    fun: "relaxed",
    amused: "relaxed",
    sad: "sad",
    sorrow: "sad",
    Surprised: "Surprised",
    surprised: "Surprised",
    shocked: "Surprised",
  };

  const expressionName = emotionMap[emotion.toLowerCase()];
  if (expressionName) {
    // Reset all emotional expressions first
    ["happy", "angry", "relaxed", "sad", "Surprised"].forEach((emotion) => {
      const expr = vrm.expressionManager.getExpression(emotion);
      if (expr) expr.weight = 0.0;
    });

    // Set the requested emotion
    return window.setExpression(expressionName, 1.0);
  } else {
    console.warn(`Unknown emotion: ${emotion}`);
    return false;
  }
};

// ✅ Global function to set lip sync expression
window.setLipSync = function (phoneme) {
  const phonemeMap = {
    a: "a",
    ah: "a",
    i: "i",
    ee: "i",
    u: "u",
    oo: "u",
    e: "e",
    eh: "e",
    o: "o",
    oh: "o",
  };

  const expressionName = phonemeMap[phoneme.toLowerCase()];
  if (expressionName) {
    // Reset all lip sync expressions first
    ["a", "i", "u", "e", "o"].forEach((phoneme) => {
      const expr = vrm.expressionManager.getExpression(phoneme);
      if (expr) expr.weight = 0.0;
    });

    // Set the requested phoneme
    return window.setExpression(expressionName, 1.0);
  } else {
    console.warn(`Unknown phoneme: ${phoneme}`);
    return false;
  }
};

// ✅ Global function to clear lip sync
window.clearLipSync = function () {
  ["a", "i", "u", "e", "o"].forEach((phoneme) => {
    const expr = vrm.expressionManager.getExpression(phoneme);
    if (expr) expr.weight = 0.0;
  });
  console.log("Cleared lip sync expressions");
};

init();
// ✅ Global flag for Python
window.vrmViewerReady = true;
console.log("VRM Viewer ready signal sent to Python.");
