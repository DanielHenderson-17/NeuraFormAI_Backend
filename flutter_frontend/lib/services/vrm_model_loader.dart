import 'dart:async';
import 'package:flutter/foundation.dart';
import '../helpers/vrm_logic.dart';

/// Service responsible for loading and managing VRM models
/// Extracted from VRMContainer to reduce complexity
class VRMModelLoader {
  // Callback for JavaScript execution - must be provided by the client
  Future<String> Function(String)? _executeJavaScript;
  
  // Callback for state updates
  void Function(VoidCallback)? _setState;
  
  // Callback to check webview readiness
  bool Function()? _isWebViewReady;
  
  // Callback to check/set loading state
  bool Function()? _isLoadingVRM;
  void Function(bool)? _setLoadingVRM;
  
  // Callback to get/set current VRM model
  String? Function()? _getCurrentVrmModel;
  
  // Callback to set animations
  void Function(List<Map<String, String>>, bool)? _setAnimations;
  
  // Callback to hide loading overlay when animation starts
  VoidCallback? _onAnimationStarted;

  /// Constructor
  VRMModelLoader({
    required Future<String> Function(String) executeJavaScript,
    required void Function(VoidCallback) setState,
    required bool Function() isWebViewReady,
    required bool Function() isLoadingVRM,
    required void Function(bool) setLoadingVRM,
    required String? Function() getCurrentVrmModel,
    required void Function(List<Map<String, String>>, bool) setAnimations,
    VoidCallback? onAnimationStarted,
  }) {
    _executeJavaScript = executeJavaScript;
    _setState = setState;
    _isWebViewReady = isWebViewReady;
    _isLoadingVRM = isLoadingVRM;
    _setLoadingVRM = setLoadingVRM;
    _getCurrentVrmModel = getCurrentVrmModel;
    _setAnimations = setAnimations;
    _onAnimationStarted = onAnimationStarted;
  }

  /// Main method to check VRM viewer readiness and load VRM model
  Future<void> checkAndLoadVRM() async {
    if (_isWebViewReady?.call() != true || _executeJavaScript == null) return;
    
    try {
      // Check if VRM viewer is ready
      await Future.delayed(const Duration(milliseconds: 500));
      await _executeJavaScript!('''
        if (window.vrmViewerReady === true) {
          console.log("VRM Viewer is ready");
          window.postMessage("READY", "*");
        } else {
          console.log("VRM Viewer not ready yet");
          setTimeout(() => {
            if (window.vrmViewerReady === true) {
              window.postMessage("READY", "*");
            }
          }, 1000);
        }
      ''');
      
      // Discover available animations
      final animations = await VRMLogic.discoverAvailableAnimations();
      _setAnimations?.call(animations, true);
      
      // Load VRM model if one is specified
      final currentModel = _getCurrentVrmModel?.call();
      if (currentModel != null && currentModel.isNotEmpty) {
        await loadVRMModel(currentModel);
      } else {
        // Even without a specific VRM model, try to play idle animation
        // (useful if a default VRM is loaded via HTML/JavaScript)
        print("🎭 [VRMModelLoader] No specific VRM model, attempting to auto-play idle animation");
        await Future.delayed(const Duration(milliseconds: 1000)); // Give time for any default VRM to load
        await VRMLogic.playAnimation(
          animationName: 'idle',
          executeJavaScript: _executeJavaScript!,
          isWebViewReady: _isWebViewReady?.call() ?? false,
          loop: true, // Idle animation should loop
        );
        
        // Hide loading overlay after animation starts
        print("✨ [VRMModelLoader] Animation started, hiding loading overlay");
        _onAnimationStarted?.call();
      }
    } catch (e) {
      print("❌ [VRMModelLoader] Error in checkAndLoadVRM: $e");
    }
  }
  
  /// Clear existing VRM model from the scene
  Future<void> clearExistingVRM() async {
    if (_isWebViewReady?.call() != true || _executeJavaScript == null) return;
    
    try {
      print("🧹 [VRMModelLoader] Clearing existing VRM model");
      
      await _executeJavaScript!('''
        if (window.vrm) {
          console.log("Clearing existing VRM model");
          if (window.VRMUtils && window.vrm.scene) {
            window.VRMUtils.deepDispose(window.vrm.scene);
          }
          if (window.scene && window.vrm.scene) {
            window.scene.remove(window.vrm.scene);
          }
          window.vrm = null;
        }
      ''');
    } catch (e) {
      print("❌ [VRMModelLoader] Failed to clear existing VRM: $e");
    }
  }
  
  /// Load a VRM model into the scene
  Future<void> loadVRMModel(String vrmModel) async {
    if (_isWebViewReady?.call() != true || 
        _isLoadingVRM?.call() == true || 
        _executeJavaScript == null) return;
    
    _setLoadingVRM?.call(true);
    try {
      // Use VRMLogic helper to get base64 data
      final base64Data = await VRMLogic.loadVRMModel(vrmModel);
      print("🟢 [VRMModelLoader] Loading VRM model: $vrmModel");
      
      await _executeJavaScript!('''
        if (window.loadVRM) {
          // Convert base64 to blob URL
          const byteCharacters = atob('$base64Data');
          const byteNumbers = new Array(byteCharacters.length);
          for (let i = 0; i < byteCharacters.length; i++) {
            byteNumbers[i] = byteCharacters.charCodeAt(i);
          }
          const byteArray = new Uint8Array(byteNumbers);
          const blob = new Blob([byteArray], {type: 'application/octet-stream'});
          const blobUrl = URL.createObjectURL(blob);
          window.loadVRM(blobUrl);
        } else {
          console.error("loadVRM function not available");
        }
      ''');
      
      // Wait a moment for VRM to load, then ensure mixer is initialized
      print("⏳ [VRMModelLoader] Waiting for VRM to load and initializing mixer...");
      await Future.delayed(const Duration(seconds: 2));
      
      // Ensure mixer is initialized
      await _executeJavaScript!('''
        if (window.vrm && !window.mixer) {
          console.log("Initializing animation mixer for VRM");
          window.mixer = new THREE.AnimationMixer(window.vrm.scene);
          console.log("Animation mixer initialized");
        }
      ''');
      
      // Wait another moment for mixer to be ready
      await Future.delayed(const Duration(seconds: 1));
      
      // Auto-play idle animation after VRM model loads (with looping)
      print("🎭 [VRMModelLoader] Auto-playing idle animation");
      await VRMLogic.playAnimation(
        animationName: 'idle',
        executeJavaScript: _executeJavaScript!,
        isWebViewReady: _isWebViewReady?.call() ?? false,
        loop: true, // Idle animation should loop
      );
      
      // Hide loading overlay after animation starts
      print("✨ [VRMModelLoader] Animation started, hiding loading overlay");
      _onAnimationStarted?.call();
      
    } catch (e) {
      print("❌ [VRMModelLoader] Failed to load VRM model: $e");
    } finally {
      _setLoadingVRM?.call(false);
    }
  }
  
  /// Wait for VRM to be fully loaded in the JavaScript environment
  Future<void> _waitForVRMLoaded() async {
    if (_executeJavaScript == null) return;
    
    // Poll for VRM loading completion with timeout
    const maxAttempts = 20; // 10 seconds max wait (500ms * 20)
    int attempts = 0;
    
    while (attempts < maxAttempts) {
      try {
        final result = await _executeJavaScript!('''
          (function() {
            var vrmLoaded = !!window.vrm;
            var mixerExists = !!window.mixer;
            var ready = vrmLoaded && mixerExists;
            return "vrmLoaded:" + vrmLoaded + ",mixerExists:" + mixerExists + ",ready:" + ready;
          })();
        ''');
        
        // Parse the result to check if VRM is loaded
        if (result.contains('vrmLoaded:true') && result.contains('mixerExists:true')) {
          print("✅ [VRMModelLoader] VRM fully loaded and ready for animations");
          return;
        }
        
        print("⏳ [VRMModelLoader] VRM loading... attempt ${attempts + 1}/$maxAttempts");
        await Future.delayed(const Duration(milliseconds: 500));
        attempts++;
        
      } catch (e) {
        print("⚠️ [VRMModelLoader] Error checking VRM load status: $e");
        await Future.delayed(const Duration(milliseconds: 500));
        attempts++;
      }
    }
    
    print("⚠️ [VRMModelLoader] Timeout waiting for VRM to load, proceeding anyway");
  }
  
  /// Clean up resources
  void dispose() {
    _executeJavaScript = null;
    _setState = null;
    _isWebViewReady = null;
    _isLoadingVRM = null;
    _setLoadingVRM = null;
    _getCurrentVrmModel = null;
    _setAnimations = null;
  }
}
