import 'dart:convert';
import 'dart:io';
import 'package:flutter/services.dart';

/// VRM and animation loading logic extracted from VRMContainer
class VRMLogic {
  /// Loads a VRM model from assets and returns the base64 string
  static Future<String> loadVRMModel(String vrmModel) async {
    final vrmData = await rootBundle.load('assets/vrm_models/$vrmModel');
    final bytes = vrmData.buffer.asUint8List();
    return base64Encode(bytes);
  }

  /// Loads an animation file from assets and returns the base64 string
  static Future<String> loadAnimation(String animationName) async {
    final animationData = await rootBundle.load('assets/animations/$animationName.vrma');
    final bytes = animationData.buffer.asUint8List();
    return base64Encode(bytes);
  }

  /// Discovers available animations in assets/animations/
  static Future<List<Map<String, String>>> discoverAvailableAnimations() async {
    final manifestContent = await rootBundle.loadString('AssetManifest.json');
    final Map<String, dynamic> manifestMap = json.decode(manifestContent);
    final List<Map<String, String>> animations = [];
    for (String key in manifestMap.keys) {
      if (key.startsWith('assets/animations/') &&
          key.endsWith('.vrma') &&
          !key.contains('/old/') &&
          key.split('/').length == 3) {
        final fileName = key.split('/').last;
        final animationName = fileName.replaceAll('.vrma', '');
        final displayName = animationName[0].toUpperCase() + animationName.substring(1);
        String emoji = '🎭';
        switch (animationName.toLowerCase()) {
          case 'peace': emoji = '✌️'; break;
          case 'greeting': emoji = '👋'; break;
          case 'pose': emoji = '🤸'; break;
          case 'squat': emoji = '🏃'; break;
          case 'spin': emoji = '🌀'; break;
          case 'shoot': emoji = '🔫'; break;
          case 'full': emoji = '💫'; break;
          default: emoji = '🎭';
        }
        animations.add({
          'name': animationName,
          'displayName': displayName,
          'emoji': emoji,
          'path': key,
        });
      }
    }
    return animations;
  }
}
