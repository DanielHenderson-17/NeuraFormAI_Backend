import 'dart:io';
import 'package:flutter/services.dart';
import 'package:path_provider/path_provider.dart';

/// Service responsible for copying VRM viewer assets to temporary directory
/// Extracted from VRMContainer to reduce complexity
class VRMAssetsService {
  String? _htmlPath;
  
  /// Get the path to the copied HTML file
  String? get htmlPath => _htmlPath;
  
  /// Copy VRM viewer assets (HTML and JS) to temporary directory
  Future<void> copyAssetsToTempDirectory() async {
    try {
      final tempDir = await getTemporaryDirectory();
      final vrmViewerDir = Directory('${tempDir.path}/vrm_viewer');
      
      if (!await vrmViewerDir.exists()) {
        await vrmViewerDir.create(recursive: true);
      }
      
      // Copy HTML file
      final htmlContent = await rootBundle.loadString('assets/vrm_viewer/index.html');
      final htmlFile = File('${vrmViewerDir.path}/index.html');
      await htmlFile.writeAsString(htmlContent);
      
      // Copy bundle.js file
      final bundleContent = await rootBundle.loadString('assets/vrm_viewer/bundle.js');
      final bundleFile = File('${vrmViewerDir.path}/bundle.js');
      await bundleFile.writeAsString(bundleContent);
      
      _htmlPath = htmlFile.path;
      print("🟢 [VRMAssetsService] Assets copied to: ${vrmViewerDir.path}");
    } catch (e) {
      print("❌ [VRMAssetsService] Failed to copy assets: $e");
      throw e;
    }
  }
  
  /// Clean up any resources (currently no cleanup needed)
  void dispose() {
    _htmlPath = null;
  }
}
