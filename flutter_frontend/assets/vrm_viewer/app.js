// Import all dependencies from node_modules
import * as THREE from "three";
import { GLTFLoader } from "three/examples/jsm/loaders/GLTFLoader.js";
import { OrbitControls } from "three/examples/jsm/controls/OrbitControls.js";
import { VRMLoaderPlugin, VRMUtils } from "@pixiv/three-vrm";
import {
  createVRMAnimationClip,
  VRMAnimationLoaderPlugin,
  VRMLookAtQuaternionProxy,
} from "@pixiv/three-vrm-animation";

// Expose Three.js classes globally for testing
window.THREE = THREE;
window.Scene = THREE.Scene;
window.PerspectiveCamera = THREE.PerspectiveCamera;
window.WebGLRenderer = THREE.WebGLRenderer;
window.BoxGeometry = THREE.BoxGeometry;
window.MeshBasicMaterial = THREE.MeshBasicMaterial;
window.Mesh = THREE.Mesh;

// Expose VRM animation imports globally for verification
window.createVRMAnimationClip = createVRMAnimationClip;
window.VRMAnimationLoaderPlugin = VRMAnimationLoaderPlugin;
window.VRMLookAtQuaternionProxy = VRMLookAtQuaternionProxy;
window.VRMLoaderPlugin = VRMLoaderPlugin;
window.VRMUtils = VRMUtils;
window.GLTFLoader = GLTFLoader;

// Expose VRM state variables globally for verification
window.vrm = null;
window.mixer = null;
window.animationClip = null;
window.isPlaying = false;

// The rest of your VRM viewer code goes here
let scene, camera, renderer, vrm, controls, clock;
let blinkTimer = 0;
let isBlinking = false;
let lastBlinkTime = 0;

// Animation-related variables
let vrmAnimation = null;
let animationClip = null;
let mixer = null;
let lookAtQuatProxy = null;
let isPlaying = false;
let animationLoader = null;

function init() {
  console.log("Starting VRM viewer initialization...");

  // Clear any existing canvases
  const existingCanvases = document.querySelectorAll("canvas");
  existingCanvases.forEach((canvas) => canvas.remove());

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
  // Add alpha: true to enable transparency, but use a visible background initially
  renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
  renderer.setSize(window.innerWidth, window.innerHeight);
  // Use a dark background to see VRM models better
  renderer.setClearColor(0x2a2a2a, 1.0); // Dark gray, fully opaque
  document.body.appendChild(renderer.domElement);
  console.log("VRM viewer renderer created and added to DOM");
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

  // Update animation mixer
  if (mixer) {
    mixer.update(delta);
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

// ✅ Global function for Flutter
window.loadVRM = function (vrmPath) {
  console.log("🤖 [DEBUG] ============ VRM LOAD START ============");
  console.log("🤖 [DEBUG] Loading VRM:", vrmPath);
  console.log("🤖 [DEBUG] Existing VRM:", !!vrm);

  if (vrm) {
    console.log("🤖 [DEBUG] Disposing existing VRM...");
    VRMUtils.deepDispose(vrm.scene);
    scene.remove(vrm.scene);
    vrm = null;
    window.vrm = null;
  }

  // Clear animation state
  if (mixer && isPlaying) {
    console.log("🤖 [DEBUG] Stopping existing animation...");
    mixer.stopAllAction();
    isPlaying = false;
    window.isPlaying = false;
  }
  vrmAnimation = null;
  animationClip = null;
  mixer = null;
  window.animationClip = null;
  window.mixer = null;

  const loader = new GLTFLoader();
  loader.register((parser) => new VRMLoaderPlugin(parser));
  loader.register((parser) => new VRMAnimationLoaderPlugin(parser));

  // Initialize animation loader if not already done
  if (!animationLoader) {
    console.log("🤖 [DEBUG] Creating animation loader...");
    // Use the same loader that has both plugins (like appTest.js)
    animationLoader = loader;
    console.log(
      "🤖 [DEBUG] Animation loader set to main loader with both plugins"
    );
  } else {
    console.log("🤖 [DEBUG] Animation loader already exists");
  }

  console.log("🤖 [DEBUG] Available imports check:");
  console.log("🤖 [DEBUG] - VRMLoaderPlugin:", typeof VRMLoaderPlugin);
  console.log(
    "🤖 [DEBUG] - VRMAnimationLoaderPlugin:",
    typeof VRMAnimationLoaderPlugin
  );
  console.log(
    "🤖 [DEBUG] - createVRMAnimationClip:",
    typeof createVRMAnimationClip
  );
  console.log(
    "🤖 [DEBUG] - VRMLookAtQuaternionProxy:",
    typeof VRMLookAtQuaternionProxy
  );

  loader.load(
    vrmPath,
    function (gltf) {
      console.log("🤖 [DEBUG] VRM file loaded, processing...");
      vrm = gltf.userData.vrm;
      if (vrm) {
        console.log("🤖 [DEBUG] VRM data extracted successfully");
        VRMUtils.rotateVRM0(vrm);

        // Update global reference
        window.vrm = vrm;

        // Add look at quaternion proxy for animation support
        if (lookAtQuatProxy) {
          console.log("🤖 [DEBUG] Removing existing lookAt proxy...");
          vrm.scene.remove(lookAtQuatProxy);
        }
        console.log("🤖 [DEBUG] Creating lookAt quaternion proxy...");
        lookAtQuatProxy = new VRMLookAtQuaternionProxy(vrm.lookAt);
        lookAtQuatProxy.name = "lookAtQuaternionProxy";
        vrm.scene.add(lookAtQuatProxy);
        console.log("🤖 [DEBUG] LookAt quaternion proxy added");

        scene.add(vrm.scene);
        console.log("🤖 [DEBUG] VRM added to scene");

        // Reset blink state for new model
        isBlinking = false;
        blinkTimer = 0;
        lastBlinkTime = clock.getElapsedTime();

        // Log available expressions for debugging
        if (vrm.expressionManager) {
          console.log(
            "🤖 [DEBUG] Available expressions:",
            vrm.expressionManager.expressions.map((exp) => exp.expressionName)
          );
        }

        console.log("🤖 [DEBUG] ============ VRM LOAD SUCCESS ============");
        console.log("🤖 [DEBUG] VRM ready for animations!");
      } else {
        console.error("🤖 [DEBUG] The loaded GLTF is not a valid VRM.", gltf);
      }
    },
    undefined,
    function (error) {
      console.error("🤖 [DEBUG] ============ VRM LOAD FAILED ============");
      console.error("🤖 [DEBUG] Error loading VRM:", error);
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

// ✅ Global function to set lip sync expression with smooth transitions
window.setLipSync = function (phoneme) {
  const phonemeMap = {
    // Map Flutter phonemes to actual VRM expressions
    aa: "aa",
    ah: "aa",
    a: "aa",
    ih: "ih",
    i: "ih",
    ee: "ee",
    e: "ee",
    ou: "ou",
    u: "ou",
    oo: "ou",
    oh: "oh",
    o: "oh",
  };

  const expressionName = phonemeMap[phoneme.toLowerCase()];
  if (expressionName) {
    // Smoothly transition to the new phoneme instead of hard reset
    const targetPhoneme = vrm.expressionManager.getExpression(expressionName);
    if (targetPhoneme) {
      // Gradually reduce other phonemes and increase target
      ["aa", "ih", "ou", "ee", "oh"].forEach((phonemeName) => {
        const expr = vrm.expressionManager.getExpression(phonemeName);
        if (expr) {
          if (phonemeName === expressionName) {
            expr.weight = 1.0; // Set target phoneme to full weight
          } else {
            expr.weight = Math.max(0.0, expr.weight * 0.3); // Reduce others gradually
          }
        }
      });
      return true;
    }
  } else {
    console.warn(`Unknown phoneme: ${phoneme}`);
    return false;
  }
};

// ✅ Global function to clear lip sync
window.clearLipSync = function () {
  ["aa", "ih", "ou", "ee", "oh"].forEach((phoneme) => {
    const expr = vrm.expressionManager.getExpression(phoneme);
    if (expr) expr.weight = 0.0;
  });
  console.log("Cleared lip sync expressions");
};

// ✅ Animation Functions
window.loadAnimation = async function (animationPath) {
  console.log("🎬 [DEBUG] ============ LOAD ANIMATION START ============");
  console.log("🎬 [DEBUG] Animation path:", animationPath);
  console.log("🎬 [DEBUG] Animation path type:", typeof animationPath);
  console.log("🎬 [DEBUG] Animation path length:", animationPath?.length);
  console.log(
    "🎬 [DEBUG] Animation path starts with blob:",
    animationPath?.startsWith("blob:")
  );
  console.log(
    "🎬 [DEBUG] Animation path starts with http:",
    animationPath?.startsWith("http")
  );
  console.log(
    "🎬 [DEBUG] Animation path starts with file:",
    animationPath?.startsWith("file:")
  );
  console.log("🎬 [DEBUG] VRM available:", !!vrm);
  console.log("🎬 [DEBUG] Animation loader available:", !!animationLoader);

  if (!vrm) {
    console.warn("🎬 [DEBUG] Cannot load animation: No VRM model loaded");
    return false;
  }

  console.log("🎬 [DEBUG] Loading VRM animation from:", animationPath);

  try {
    // Stop any existing animation
    if (mixer && isPlaying) {
      console.log("🎬 [DEBUG] Stopping existing animation");
      mixer.stopAllAction();
      isPlaying = false;
    }

    console.log("🎬 [DEBUG] Starting animation file load...");
    console.log("🎬 [DEBUG] Using animationLoader:", !!animationLoader);
    console.log("🎬 [DEBUG] animationLoader type:", typeof animationLoader);

    // Add a timeout to prevent hanging
    console.log("🎬 [DEBUG] Calling animationLoader.loadAsync...");
    const startTime = performance.now();
    const gltf = await animationLoader.loadAsync(animationPath);
    const loadTime = performance.now() - startTime;

    console.log(
      "🎬 [DEBUG] Animation file loaded successfully in",
      loadTime.toFixed(2),
      "ms"
    );
    console.log("🎬 [DEBUG] GLTF object type:", typeof gltf);
    console.log("🎬 [DEBUG] GLTF has userData:", !!gltf.userData);
    console.log(
      "🎬 [DEBUG] GLTF userData keys:",
      gltf.userData ? Object.keys(gltf.userData) : "none"
    );
    console.log("🎬 [DEBUG] GLTF userData:", gltf.userData);
    console.log(
      "🎬 [DEBUG] VRM animations available:",
      gltf.userData?.vrmAnimations?.length || 0
    );

    // Extract VRM Animation
    if (
      !gltf.userData.vrmAnimations ||
      gltf.userData.vrmAnimations.length === 0
    ) {
      console.error("🎬 [DEBUG] No VRM animations found in loaded file");
      console.log("🎬 [DEBUG] Full GLTF structure:");
      console.log("🎬 [DEBUG] - scene:", !!gltf.scene);
      console.log("🎬 [DEBUG] - scenes:", gltf.scenes?.length || 0);
      console.log("🎬 [DEBUG] - animations:", gltf.animations?.length || 0);
      console.log("🎬 [DEBUG] - userData:", gltf.userData);
      console.log(
        "🎬 [DEBUG] Available userData keys:",
        Object.keys(gltf.userData)
      );
      throw new Error("No VRM animations found in loaded file");
    }

    vrmAnimation = gltf.userData.vrmAnimations[0];
    console.log(
      "🎬 [DEBUG] VRM animation extracted:",
      vrmAnimation.name || "unnamed"
    );
    console.log("🎬 [DEBUG] Animation duration:", vrmAnimation.duration);
    console.log("🎬 [DEBUG] Animation tracks:", {
      humanoid: vrmAnimation.humanoid
        ? Object.keys(vrmAnimation.humanoid).length
        : 0,
      expressions: vrmAnimation.expressions
        ? Object.keys(vrmAnimation.expressions).length
        : 0,
      lookAt: vrmAnimation.lookAt ? Object.keys(vrmAnimation.lookAt).length : 0,
    });

    // Create animation clip
    console.log("🎬 [DEBUG] Creating VRM animation clip...");
    console.log(
      "🎬 [DEBUG] createVRMAnimationClip function available:",
      typeof createVRMAnimationClip
    );
    animationClip = createVRMAnimationClip(vrmAnimation, vrm);
    window.animationClip = animationClip;
    console.log("🎬 [DEBUG] Animation clip created:", !!animationClip);
    if (!animationClip) {
      console.error("🎬 [DEBUG] Failed to create animation clip");
      throw new Error("Failed to create animation clip");
    }
    console.log(
      `🎬 [DEBUG] Animation clip duration: ${animationClip.duration.toFixed(
        2
      )}s`
    );
    console.log(
      "🎬 [DEBUG] Animation clip tracks:",
      animationClip.tracks.length
    );

    // Create or update mixer
    if (mixer) {
      console.log("🎬 [DEBUG] Updating existing animation mixer...");
      mixer.stopAllAction();
    } else {
      console.log("🎬 [DEBUG] Creating new animation mixer...");
      mixer = new THREE.AnimationMixer(vrm.scene);
      window.mixer = mixer;
    }
    console.log("🎬 [DEBUG] Mixer created/updated successfully");

    console.log("🎬 [DEBUG] ============ LOAD ANIMATION SUCCESS ============");
    return true;
  } catch (error) {
    console.error("🎬 [DEBUG] ============ LOAD ANIMATION FAILED ============");
    console.error("🎬 [DEBUG] Animation loading failed:", error.message);
    console.error("🎬 [DEBUG] Stack trace:", error.stack);
    vrmAnimation = null;
    animationClip = null;
    return false;
  }
};

window.playAnimation = function () {
  console.log("🎬 [DEBUG] ============ PLAY ANIMATION START ============");
  console.log("🎬 [DEBUG] Mixer available:", !!mixer);
  console.log("🎬 [DEBUG] Animation clip available:", !!animationClip);
  console.log("🎬 [DEBUG] Is already playing:", isPlaying);

  if (!mixer || !animationClip) {
    console.warn(
      "🎬 [DEBUG] Cannot play animation: No mixer or clip available"
    );
    console.log("🎬 [DEBUG] Mixer:", mixer);
    console.log("🎬 [DEBUG] Animation clip:", animationClip);
    return false;
  }

  console.log("🎬 [DEBUG] Starting animation playback...");

  try {
    // Stop all existing actions
    console.log("🎬 [DEBUG] Stopping all existing actions...");
    mixer.stopAllAction();

    // Create and configure action
    console.log("🎬 [DEBUG] Creating clip action...");
    const action = mixer.clipAction(animationClip);
    console.log("🎬 [DEBUG] Action created:", !!action);
    console.log(
      "🎬 [DEBUG] Action weight before reset:",
      action.getEffectiveWeight()
    );

    action.reset();
    console.log("🎬 [DEBUG] Action reset complete");

    action.setLoop(THREE.LoopRepeat);
    console.log("🎬 [DEBUG] Loop mode set to repeat");

    action.clampWhenFinished = false;
    console.log("🎬 [DEBUG] Clamp when finished set to false");
    console.log(
      "🎬 [DEBUG] Action weight after setup:",
      action.getEffectiveWeight()
    );

    // Play animation
    console.log("🎬 [DEBUG] Calling action.play()...");
    action.play();
    isPlaying = true;
    window.isPlaying = true;
    console.log("🎬 [DEBUG] Action.play() called, isPlaying set to true");

    // Log action state
    console.log("🎬 [DEBUG] Action state after play:");
    console.log("🎬 [DEBUG] - Enabled:", action.enabled);
    console.log("🎬 [DEBUG] - Weight:", action.weight);
    console.log("🎬 [DEBUG] - Time:", action.time);
    console.log("🎬 [DEBUG] - TimeScale:", action.timeScale);
    console.log("🎬 [DEBUG] - Loop:", action.loop);
    console.log("🎬 [DEBUG] - Paused:", action.paused);

    console.log("🎬 [DEBUG] ============ PLAY ANIMATION SUCCESS ============");
    return true;
  } catch (error) {
    console.error("🎬 [DEBUG] ============ PLAY ANIMATION FAILED ============");
    console.error("🎬 [DEBUG] Animation playback failed:", error.message);
    console.error("🎬 [DEBUG] Stack trace:", error.stack);
    isPlaying = false;
    return false;
  }
};

window.stopAnimation = function () {
  if (!mixer) {
    console.warn("No mixer available to stop");
    return false;
  }

  console.log("Stopping animation...");

  try {
    mixer.stopAllAction();
    isPlaying = false;
    console.log("Animation stopped");
    return true;
  } catch (error) {
    console.error("Failed to stop animation:", error.message);
    return false;
  }
};

window.playAnimationByName = async function (animationName) {
  try {
    console.log(
      "🎬 [DEBUG] ============ PLAY ANIMATION BY NAME START ============"
    );
    console.log("🎬 [DEBUG] Animation name requested:", animationName);

    const animationMap = {
      peace: "assets/animations/peace.vrma",
      greeting: "assets/animations/greeting.vrma",
      pose: "assets/animations/pose.vrma",
      squat: "assets/animations/squat.vrma",
      spin: "assets/animations/spin.vrma",
      shoot: "assets/animations/shoot.vrma",
      full: "assets/animations/full.vrma",
    };

    console.log("🎬 [DEBUG] Available animations:", Object.keys(animationMap));
    const animationPath = animationMap[animationName.toLowerCase()];
    console.log("🎬 [DEBUG] Mapped animation path:", animationPath);

    if (!animationPath) {
      console.warn(`🎬 [DEBUG] Unknown animation: ${animationName}`);
      console.log(
        "🎬 [DEBUG] Available animations are:",
        Object.keys(animationMap).join(", ")
      );
      return false;
    }

    console.log(
      `🎬 [DEBUG] Playing animation: ${animationName} from ${animationPath}`
    );

    console.log("🎬 [DEBUG] Calling loadAnimation...");
    const loaded = await window.loadAnimation(animationPath);
    console.log("🎬 [DEBUG] loadAnimation result:", loaded);

    if (loaded) {
      console.log(
        "🎬 [DEBUG] Animation loaded successfully, now calling playAnimation..."
      );
      const played = window.playAnimation();
      console.log("🎬 [DEBUG] playAnimation result:", played);
      console.log(
        "🎬 [DEBUG] ============ PLAY ANIMATION BY NAME COMPLETE ============"
      );
      return played;
    } else {
      console.log("🎬 [DEBUG] Animation loading failed");
      console.log(
        "🎬 [DEBUG] ============ PLAY ANIMATION BY NAME FAILED ============"
      );
      return false;
    }
  } catch (error) {
    console.error("🎬 [ERROR] playAnimationByName failed:", error);
    console.error("🎬 [ERROR] Error stack:", error.stack);
    return false;
  }
};

// ✅ Global function to verify animation support
window.verifyAnimationSupport = function () {
  console.log(
    "🔍 [VERIFICATION] ============ ANIMATION SUPPORT CHECK ============"
  );

  const results = {
    createVRMAnimationClip: typeof createVRMAnimationClip,
    VRMAnimationLoaderPlugin: typeof VRMAnimationLoaderPlugin,
    VRMLookAtQuaternionProxy: typeof VRMLookAtQuaternionProxy,
    GLTFLoader: typeof GLTFLoader,
    mixer: !!mixer,
    vrm: !!vrm,
    animationClip: !!animationClip,
    isPlaying: isPlaying,
  };

  console.log("🔍 [VERIFICATION] Animation imports:", results);
  console.log(
    "🔍 [VERIFICATION] createVRMAnimationClip available:",
    results.createVRMAnimationClip === "function"
  );
  console.log(
    "🔍 [VERIFICATION] VRMAnimationLoaderPlugin available:",
    results.VRMAnimationLoaderPlugin === "function"
  );
  console.log(
    "🔍 [VERIFICATION] VRMLookAtQuaternionProxy available:",
    results.VRMLookAtQuaternionProxy === "function"
  );
  console.log(
    "🔍 [VERIFICATION] GLTFLoader available:",
    results.GLTFLoader === "function"
  );
  console.log("🔍 [VERIFICATION] Mixer instance available:", results.mixer);
  console.log("🔍 [VERIFICATION] VRM model loaded:", results.vrm);
  console.log(
    "🔍 [VERIFICATION] Animation clip loaded:",
    results.animationClip
  );
  console.log("🔍 [VERIFICATION] Animation playing:", results.isPlaying);
  console.log(
    "🔍 [VERIFICATION] ============ VERIFICATION COMPLETE ============"
  );

  return results;
};

init();
// ✅ Global flag for Flutter
window.vrmViewerReady = true;
console.log("VRM Viewer ready signal sent to Flutter.");

// Expose key functions globally for debugging
window.init = init;
window.loadVRM = loadVRM;
window.animate = animate;
