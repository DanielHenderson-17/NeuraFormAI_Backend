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

  /// Constructor
  VRMModelLoader({
    required Future<String> Function(String) executeJavaScript,
    required void Function(VoidCallback) setState,
    required bool Function() isWebViewReady,
    required bool Function() isLoadingVRM,
    required void Function(bool) setLoadingVRM,
    required String? Function() getCurrentVrmModel,
    required void Function(List<Map<String, String>>, bool) setAnimations,
  }) {
    _executeJavaScript = executeJavaScript;
    _setState = setState;
    _isWebViewReady = isWebViewReady;
    _isLoadingVRM = isLoadingVRM;
    _setLoadingVRM = setLoadingVRM;
    _getCurrentVrmModel = getCurrentVrmModel;
    _setAnimations = setAnimations;
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
      
    } catch (e) {
      print("❌ [VRMModelLoader] Failed to load VRM model: $e");
    } finally {
      _setLoadingVRM?.call(false);
    }
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
