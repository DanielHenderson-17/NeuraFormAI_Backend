// appTest.js - VRM Animation Test Environment
import * as THREE from "three";
import { GLTFLoader } from "three/addons/loaders/GLTFLoader.js";
import { OrbitControls } from "three/addons/controls/OrbitControls.js";
import { VRMLoaderPlugin, VRMUtils } from "@pixiv/three-vrm";
import {
  createVRMAnimationClip,
  VRMAnimationLoaderPlugin,
  VRMLookAtQuaternionProxy,
} from "@pixiv/three-vrm-animation";

// Global state
let renderer, camera, scene, controls, loader;
let vrm = null;
let vrmAnimation = null;
let animationClip = null;
let mixer = null;
let lookAtQuatProxy = null;
let isPlaying = false;
let clock;

// Performance monitoring
let lastTime = performance.now();
let frameCount = 0;
let fps = 0;

// Console logging function
function logToConsole(message, type = "info") {
  const timestamp = new Date().toLocaleTimeString();
  const consoleContent = document.getElementById("console-content");
  const logEntry = document.createElement("div");

  let color = "#00ff00";
  if (type === "error") color = "#ff4444";
  if (type === "warn") color = "#ffff00";
  if (type === "success") color = "#44ff44";
  if (type === "debug") color = "#8888ff";

  logEntry.innerHTML = `<span style="color: #888">[${timestamp}]</span> <span style="color: ${color}">[${type.toUpperCase()}]</span> ${message}`;
  consoleContent.appendChild(logEntry);
  consoleContent.scrollTop = consoleContent.scrollHeight;

  // Also log to browser console
  console.log(`[VRM Test] [${type.toUpperCase()}] ${message}`);
}

// Clear console function
window.clearConsole = function () {
  document.getElementById("console-content").innerHTML = "";
  logToConsole("Console cleared", "info");
};

// Update status displays
function updateStatus(status, type = "ready") {
  const statusElement = document.getElementById("system-status");
  statusElement.textContent = status;
  statusElement.className = `status ${type}`;
}

function updateStats() {
  document.getElementById("vrm-loaded").textContent = vrm !== null;
  document.getElementById("animation-loaded").textContent =
    vrmAnimation !== null;
  document.getElementById("animation-playing").textContent = isPlaying;
  document.getElementById("current-animation").textContent = vrmAnimation
    ? "Loaded"
    : "None";
  document.getElementById("mixer-time").textContent = mixer
    ? mixer.time.toFixed(2)
    : "0.00";
  document.getElementById("fps").textContent = fps;
}

// Initialize Three.js scene
async function initializeScene() {
  logToConsole("🚀 Initializing Three.js scene...", "info");

  try {
    // Create renderer
    logToConsole("Creating WebGL renderer...", "debug");
    renderer = new THREE.WebGLRenderer({ antialias: true });
    renderer.setSize(window.innerWidth - 300, window.innerHeight);
    renderer.setPixelRatio(window.devicePixelRatio);
    renderer.outputColorSpace = THREE.SRGBColorSpace;
    renderer.shadowMap.enabled = true;
    renderer.shadowMap.type = THREE.PCFSoftShadowMap;

    const canvasContainer = document.getElementById("canvas-container");
    canvasContainer.appendChild(renderer.domElement);
    logToConsole("✅ Renderer created and added to DOM", "success");

    // Create camera
    logToConsole("Setting up camera...", "debug");
    camera = new THREE.PerspectiveCamera(
      45,
      (window.innerWidth - 300) / window.innerHeight,
      0.1,
      100
    );
    camera.position.set(0, 1.5, 3);
    logToConsole("✅ Camera positioned at (0, 1.5, 3)", "success");

    // Create controls
    logToConsole("Initializing orbit controls...", "debug");
    controls = new OrbitControls(camera, renderer.domElement);
    controls.enablePan = true;
    controls.enableZoom = true;
    controls.enableRotate = true;
    controls.target.set(0, 1, 0);
    controls.update();
    logToConsole("✅ Orbit controls initialized", "success");

    // Create scene
    logToConsole("Creating scene...", "debug");
    scene = new THREE.Scene();
    scene.background = new THREE.Color(0x212121);
    logToConsole("✅ Scene created with background color", "success");

    // Add lighting
    logToConsole("Setting up lighting...", "debug");
    const ambientLight = new THREE.AmbientLight(0xffffff, 0.4);
    scene.add(ambientLight);

    const directionalLight = new THREE.DirectionalLight(0xffffff, 1.0);
    directionalLight.position.set(1, 1, 1).normalize();
    directionalLight.castShadow = true;
    directionalLight.shadow.mapSize.width = 2048;
    directionalLight.shadow.mapSize.height = 2048;
    scene.add(directionalLight);
    logToConsole(
      "✅ Lighting setup complete (ambient + directional)",
      "success"
    );

    // Add helpers
    logToConsole("Adding scene helpers...", "debug");
    const gridHelper = new THREE.GridHelper(10, 10, 0x888888, 0x444444);
    scene.add(gridHelper);

    const axesHelper = new THREE.AxesHelper(2);
    scene.add(axesHelper);
    logToConsole("✅ Grid and axes helpers added", "success");

    // Initialize GLTF loader with plugins
    logToConsole("Setting up GLTF loader with VRM plugins...", "debug");
    loader = new GLTFLoader();
    loader.crossOrigin = "anonymous";

    // Register VRM loader plugin
    loader.register((parser) => {
      logToConsole("🔌 Registering VRM loader plugin...", "debug");
      return new VRMLoaderPlugin(parser);
    });

    // Register VRM Animation loader plugin
    loader.register((parser) => {
      logToConsole("🔌 Registering VRM Animation loader plugin...", "debug");
      return new VRMAnimationLoaderPlugin(parser);
    });

    logToConsole("✅ GLTF loader configured with VRM plugins", "success");

    // Initialize clock
    clock = new THREE.Clock();
    clock.start();
    logToConsole("⏰ Animation clock started", "success");

    // Setup window resize handler
    window.addEventListener("resize", onWindowResize, false);
    logToConsole("📱 Window resize handler registered", "debug");

    updateStatus("Scene initialized - Ready to load VRM", "ready");
    enableControls();

    // Start render loop
    logToConsole("🎬 Starting render loop...", "info");
    animate();

    logToConsole("🎉 Scene initialization complete!", "success");
  } catch (error) {
    logToConsole(`❌ Scene initialization failed: ${error.message}`, "error");
    console.error("Scene initialization error:", error);
    updateStatus("Initialization failed", "error");
  }
}

// Window resize handler
function onWindowResize() {
  const width = window.innerWidth - 300;
  const height = window.innerHeight;

  camera.aspect = width / height;
  camera.updateProjectionMatrix();
  renderer.setSize(width, height);

  logToConsole(`📱 Window resized to ${width}x${height}`, "debug");
}

// Load VRM model
async function loadVRM(url) {
  logToConsole(`🤖 Loading VRM model from: ${url}`, "info");
  updateStatus("Loading VRM...", "loading");

  try {
    // Clear existing VRM
    if (vrm) {
      logToConsole("🧹 Clearing existing VRM from scene...", "debug");
      scene.remove(vrm.scene);
      vrm = null;
    }

    logToConsole("📥 Starting GLTF load...", "debug");
    const gltf = await loader.loadAsync(url);
    logToConsole("✅ GLTF loaded successfully", "success");

    // Extract VRM
    vrm = gltf.userData.vrm;
    if (!vrm) {
      throw new Error("No VRM data found in loaded file");
    }
    logToConsole(
      `✅ VRM extracted from GLTF: ${
        vrm.meta?.metaVersion || "unknown version"
      }`,
      "success"
    );

    // Log VRM info
    logVRMInfo();

    // Optimize VRM
    logToConsole("⚡ Optimizing VRM performance...", "debug");
    VRMUtils.removeUnnecessaryVertices(vrm.scene);
    VRMUtils.removeUnnecessaryJoints(vrm.scene);
    logToConsole("✅ VRM optimization complete", "success");

    // Disable frustum culling
    logToConsole("🔧 Configuring VRM rendering settings...", "debug");
    vrm.scene.traverse((obj) => {
      obj.frustumCulled = false;
    });
    logToConsole("✅ Frustum culling disabled for all VRM objects", "success");

    // Add look at quaternion proxy for animation support
    logToConsole("👀 Setting up look-at quaternion proxy...", "debug");
    if (lookAtQuatProxy) {
      vrm.scene.remove(lookAtQuatProxy);
    }
    lookAtQuatProxy = new VRMLookAtQuaternionProxy(vrm.lookAt);
    lookAtQuatProxy.name = "lookAtQuaternionProxy";
    vrm.scene.add(lookAtQuatProxy);
    logToConsole("✅ Look-at quaternion proxy added", "success");

    // Add VRM to scene
    scene.add(vrm.scene);
    logToConsole("🎭 VRM added to scene", "success");

    // Position camera to view VRM
    logToConsole("📷 Adjusting camera position for VRM...", "debug");
    controls.target.set(0, 1, 0);
    camera.position.set(0, 1.5, 3);
    controls.update();

    updateStatus("VRM loaded successfully", "ready");
    enableAnimationControls();

    logToConsole(
      `🎉 VRM loading complete! Model ready for animation.`,
      "success"
    );
  } catch (error) {
    logToConsole(`❌ VRM loading failed: ${error.message}`, "error");
    console.error("VRM loading error:", error);
    updateStatus("VRM loading failed", "error");
    vrm = null;
  }

  updateStats();
}

// Load VRM Animation
async function loadAnimation(url) {
  if (!vrm) {
    logToConsole("⚠️ Cannot load animation: No VRM model loaded", "warn");
    return;
  }

  logToConsole(`💃 Loading VRM animation from: ${url}`, "info");
  updateStatus("Loading animation...", "loading");

  try {
    // Stop any existing animation
    if (mixer && isPlaying) {
      stopAnimation();
    }

    logToConsole("📥 Starting VRMA load...", "debug");
    const gltf = await loader.loadAsync(url);
    logToConsole("✅ VRMA loaded successfully", "success");

    // Extract VRM Animation
    if (
      !gltf.userData.vrmAnimations ||
      gltf.userData.vrmAnimations.length === 0
    ) {
      throw new Error("No VRM animations found in loaded file");
    }

    vrmAnimation = gltf.userData.vrmAnimations[0];
    logToConsole(
      `✅ VRM animation extracted: ${vrmAnimation.name || "unnamed"}`,
      "success"
    );

    // Log animation info
    logAnimationInfo();

    // Create animation clip
    logToConsole("🎬 Creating VRM animation clip...", "debug");
    animationClip = createVRMAnimationClip(vrmAnimation, vrm);
    if (!animationClip) {
      throw new Error("Failed to create animation clip");
    }
    logToConsole(
      `✅ Animation clip created: duration ${animationClip.duration.toFixed(
        2
      )}s`,
      "success"
    );

    // Create or update mixer
    if (mixer) {
      logToConsole("🔄 Updating existing animation mixer...", "debug");
      mixer.stopAllAction();
    } else {
      logToConsole("🎛️ Creating new animation mixer...", "debug");
      mixer = new THREE.AnimationMixer(vrm.scene);
    }

    logToConsole("✅ Animation mixer ready", "success");

    updateStatus("Animation loaded successfully", "ready");
    enablePlayControls();

    logToConsole(`🎉 Animation loading complete! Ready to play.`, "success");
  } catch (error) {
    logToConsole(`❌ Animation loading failed: ${error.message}`, "error");
    console.error("Animation loading error:", error);
    updateStatus("Animation loading failed", "error");
    vrmAnimation = null;
    animationClip = null;
  }

  updateStats();
}

// Play animation
function playAnimation() {
  if (!mixer || !animationClip) {
    logToConsole(
      "⚠️ Cannot play animation: No mixer or clip available",
      "warn"
    );
    return;
  }

  logToConsole("▶️ Starting animation playback...", "info");

  try {
    // Stop all existing actions
    mixer.stopAllAction();

    // Create and configure action
    const action = mixer.clipAction(animationClip);
    action.reset();
    action.setLoop(THREE.LoopRepeat);
    action.clampWhenFinished = false;

    logToConsole(
      `🎭 Animation action configured: loop=${
        action.loop
      }, weight=${action.getEffectiveWeight()}`,
      "debug"
    );

    // Play animation
    action.play();
    isPlaying = true;

    logToConsole("✅ Animation started successfully", "success");
    updateStatus("Animation playing", "playing");
  } catch (error) {
    logToConsole(`❌ Animation playback failed: ${error.message}`, "error");
    console.error("Animation playback error:", error);
    isPlaying = false;
  }

  updateStats();
}

// Stop animation
function stopAnimation() {
  if (!mixer) {
    logToConsole("⚠️ No mixer available to stop", "warn");
    return;
  }

  logToConsole("⏹️ Stopping animation...", "info");

  try {
    mixer.stopAllAction();
    isPlaying = false;

    logToConsole("✅ Animation stopped", "success");
    updateStatus("Animation stopped", "ready");
  } catch (error) {
    logToConsole(`❌ Failed to stop animation: ${error.message}`, "error");
    console.error("Animation stop error:", error);
  }

  updateStats();
}

// Reset animation
function resetAnimation() {
  if (!mixer) {
    logToConsole("⚠️ No mixer available to reset", "warn");
    return;
  }

  logToConsole("🔄 Resetting animation...", "info");

  try {
    mixer.stopAllAction();
    mixer.setTime(0);
    isPlaying = false;

    logToConsole("✅ Animation reset to beginning", "success");
    updateStatus("Animation reset", "ready");
  } catch (error) {
    logToConsole(`❌ Failed to reset animation: ${error.message}`, "error");
    console.error("Animation reset error:", error);
  }

  updateStats();
}

// Clear VRM
function clearVRM() {
  logToConsole("🧹 Clearing VRM model...", "info");

  if (mixer && isPlaying) {
    stopAnimation();
  }

  if (vrm) {
    scene.remove(vrm.scene);
    vrm = null;
    logToConsole("✅ VRM removed from scene", "success");
  }

  if (lookAtQuatProxy) {
    lookAtQuatProxy = null;
  }

  vrmAnimation = null;
  animationClip = null;
  mixer = null;
  isPlaying = false;

  updateStatus("VRM cleared", "ready");
  disableAnimationControls();
  updateStats();

  logToConsole("🎉 VRM clear complete", "success");
}

// Reset entire scene
function resetScene() {
  logToConsole("🔄 Resetting entire scene...", "info");

  clearVRM();

  // Reset camera
  camera.position.set(0, 1.5, 3);
  controls.target.set(0, 1, 0);
  controls.update();

  // Reset selections
  document.getElementById("vrm-select").value = "";
  document.getElementById("animation-select").value = "";

  updateStatus("Scene reset", "ready");
  logToConsole("🎉 Scene reset complete", "success");
}

// Debug functions
function logVRMInfo() {
  if (!vrm) {
    logToConsole("⚠️ No VRM to analyze", "warn");
    return;
  }

  logToConsole("🔍 VRM Information Analysis:", "debug");
  logToConsole(
    `  📊 Meta Version: ${vrm.meta?.metaVersion || "unknown"}`,
    "debug"
  );
  logToConsole(`  📊 Name: ${vrm.meta?.name || "unnamed"}`, "debug");
  logToConsole(`  📊 Version: ${vrm.meta?.version || "unknown"}`, "debug");
  logToConsole(`  📊 Author: ${vrm.meta?.author || "unknown"}`, "debug");

  // Humanoid info
  if (vrm.humanoid) {
    const bones = Object.keys(vrm.humanoid.humanBones).length;
    logToConsole(`  🦴 Humanoid bones: ${bones}`, "debug");
    logToConsole(`  🦴 Raw humanoid: ${!!vrm.humanoid.rawHumanoid}`, "debug");
  }

  // LookAt info
  if (vrm.lookAt) {
    logToConsole(`  👀 LookAt type: ${vrm.lookAt.type || "none"}`, "debug");
    logToConsole(
      `  👀 LookAt applier: ${vrm.lookAt.applier?.constructor.name || "none"}`,
      "debug"
    );
  }

  // Expression info
  if (vrm.expressionManager) {
    const expressions = vrm.expressionManager.expressionMap
      ? Object.keys(vrm.expressionManager.expressionMap).length
      : 0;
    logToConsole(`  😊 Expressions: ${expressions}`, "debug");
  }

  // Scene info
  logToConsole(`  🎭 Scene children: ${vrm.scene.children.length}`, "debug");
  logToConsole(
    `  🎭 Scene position: (${vrm.scene.position.x.toFixed(
      2
    )}, ${vrm.scene.position.y.toFixed(2)}, ${vrm.scene.position.z.toFixed(
      2
    )})`,
    "debug"
  );
}

function logAnimationInfo() {
  if (!vrmAnimation) {
    logToConsole("⚠️ No VRM animation to analyze", "warn");
    return;
  }

  logToConsole("🔍 VRM Animation Information:", "debug");
  logToConsole(`  📊 Name: ${vrmAnimation.name || "unnamed"}`, "debug");
  logToConsole(
    `  📊 Duration: ${vrmAnimation.duration?.toFixed(2) || "unknown"}s`,
    "debug"
  );

  // Humanoid tracks
  if (vrmAnimation.humanoid) {
    const tracks = Object.keys(vrmAnimation.humanoid).length;
    logToConsole(`  🦴 Humanoid tracks: ${tracks}`, "debug");
    Object.keys(vrmAnimation.humanoid).forEach((bone) => {
      const track = vrmAnimation.humanoid[bone];
      logToConsole(`    🦴 ${bone}: ${track.length || 0} keyframes`, "debug");
    });
  }

  // Expression tracks
  if (vrmAnimation.expressions) {
    const expressions = Object.keys(vrmAnimation.expressions).length;
    logToConsole(`  😊 Expression tracks: ${expressions}`, "debug");
    Object.keys(vrmAnimation.expressions).forEach((expression) => {
      const track = vrmAnimation.expressions[expression];
      logToConsole(
        `    😊 ${expression}: ${track.length || 0} keyframes`,
        "debug"
      );
    });
  }

  // LookAt tracks
  if (vrmAnimation.lookAt) {
    logToConsole(
      `  👀 LookAt tracks: ${Object.keys(vrmAnimation.lookAt).length}`,
      "debug"
    );
  }
}

function testMixer() {
  if (!mixer) {
    logToConsole("⚠️ No mixer to test", "warn");
    return;
  }

  logToConsole("🧪 Mixer Test Information:", "debug");
  logToConsole(`  ⏰ Time: ${mixer.time.toFixed(3)}`, "debug");
  logToConsole(`  ⏰ Time scale: ${mixer.timeScale}`, "debug");
  logToConsole(`  🎬 Actions: ${mixer._actions.length}`, "debug");

  mixer._actions.forEach((action, index) => {
    logToConsole(`    🎬 Action ${index}: ${action._clip.name}`, "debug");
    logToConsole(`      ▶️ Enabled: ${action.enabled}`, "debug");
    logToConsole(`      ⚖️ Weight: ${action.weight}`, "debug");
    logToConsole(`      ⏰ Time: ${action.time.toFixed(3)}`, "debug");
    logToConsole(`      🔄 Loop: ${action.loop}`, "debug");
  });
}

// Control functions
function enableControls() {
  document.getElementById("load-vrm-btn").disabled = false;
  document.getElementById("reset-scene-btn").disabled = false;
}

function enableAnimationControls() {
  document.getElementById("clear-vrm-btn").disabled = false;
  document.getElementById("load-animation-btn").disabled = false;
  document.getElementById("log-vrm-info-btn").disabled = false;
}

function enablePlayControls() {
  document.getElementById("play-animation-btn").disabled = false;
  document.getElementById("stop-animation-btn").disabled = false;
  document.getElementById("reset-animation-btn").disabled = false;
  document.getElementById("log-animation-info-btn").disabled = false;
  document.getElementById("test-mixer-btn").disabled = false;
}

function disableAnimationControls() {
  document.getElementById("clear-vrm-btn").disabled = true;
  document.getElementById("load-animation-btn").disabled = true;
  document.getElementById("play-animation-btn").disabled = true;
  document.getElementById("stop-animation-btn").disabled = true;
  document.getElementById("reset-animation-btn").disabled = true;
  document.getElementById("log-vrm-info-btn").disabled = true;
  document.getElementById("log-animation-info-btn").disabled = true;
  document.getElementById("test-mixer-btn").disabled = true;
}

// Animation loop
function animate() {
  requestAnimationFrame(animate);

  // Calculate FPS
  frameCount++;
  const currentTime = performance.now();
  if (currentTime >= lastTime + 1000) {
    fps = Math.round((frameCount * 1000) / (currentTime - lastTime));
    frameCount = 0;
    lastTime = currentTime;
  }

  const deltaTime = clock.getDelta();

  // Update mixer
  if (mixer) {
    mixer.update(deltaTime);
  }

  // Update VRM
  if (vrm) {
    vrm.update(deltaTime);
  }

  // Update controls
  controls.update();

  // Render
  renderer.render(scene, camera);

  // Update stats periodically
  if (frameCount % 30 === 0) {
    updateStats();
  }
}

// Event listeners
document.addEventListener("DOMContentLoaded", () => {
  logToConsole("🌟 VRM Animation Test Environment starting...", "info");

  // Initialize scene
  initializeScene();

  // Set up event listeners
  document.getElementById("load-vrm-btn").addEventListener("click", () => {
    const select = document.getElementById("vrm-select");
    if (select.value) {
      loadVRM(select.value);
    } else {
      logToConsole("⚠️ Please select a VRM model first", "warn");
    }
  });

  document.getElementById("clear-vrm-btn").addEventListener("click", clearVRM);

  document
    .getElementById("load-animation-btn")
    .addEventListener("click", () => {
      const select = document.getElementById("animation-select");
      if (select.value) {
        loadAnimation(select.value);
      } else {
        logToConsole("⚠️ Please select an animation first", "warn");
      }
    });

  document
    .getElementById("play-animation-btn")
    .addEventListener("click", playAnimation);
  document
    .getElementById("stop-animation-btn")
    .addEventListener("click", stopAnimation);
  document
    .getElementById("reset-animation-btn")
    .addEventListener("click", resetAnimation);

  document
    .getElementById("log-vrm-info-btn")
    .addEventListener("click", logVRMInfo);
  document
    .getElementById("log-animation-info-btn")
    .addEventListener("click", logAnimationInfo);
  document
    .getElementById("test-mixer-btn")
    .addEventListener("click", testMixer);
  document
    .getElementById("reset-scene-btn")
    .addEventListener("click", resetScene);

  logToConsole("🎮 Event listeners registered", "success");
});
