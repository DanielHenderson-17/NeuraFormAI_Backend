import 'dart:convert';
import 'dart:io';
import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:webview_flutter/webview_flutter.dart';
import 'package:webview_windows/webview_windows.dart';
import 'package:path_provider/path_provider.dart';

class VRMContainer extends StatefulWidget {
  final String? vrmModel;
  final Function(String)? onVrmModelChanged;
  
  const VRMContainer({
    Key? key,
    this.vrmModel,
    this.onVrmModelChanged,
  }) : super(key: key);

  @override
  State<VRMContainer> createState() => _VRMContainerState();
}

class _VRMContainerState extends State<VRMContainer> {
  WebViewController? _webViewController;
  WebviewController? _desktopWebviewController;
  bool _isWebViewReady = false;
  bool _isWebViewSupported = true;
  bool _useDesktopWebview = false;
  String? _currentVrmModel;
  String? _htmlPath;
  String? _errorMessage;
  
  @override
  void initState() {
    super.initState();
    _currentVrmModel = widget.vrmModel;
    _useDesktopWebview = Platform.isWindows || Platform.isLinux || Platform.isMacOS;
    _setupVRMViewer();
  }
  
  Future<void> _setupVRMViewer() async {
    try {
      print("🔧 [VRMContainer] Starting VRM viewer setup...");
      print("🔧 [VRMContainer] Platform: ${Platform.operatingSystem}");
      print("🔧 [VRMContainer] Using desktop webview: $_useDesktopWebview");
      
      await _copyAssetsToTempDirectory();
      if (_useDesktopWebview) {
        await _initializeDesktopWebView();
      } else {
        await _initializeWebView();
      }
    } catch (e) {
      print("❌ [VRMContainer] Failed to setup VRM viewer: $e");
      print("❌ [VRMContainer] Stack trace: ${StackTrace.current}");
      setState(() {
        _isWebViewSupported = false;
        _errorMessage = "VRM Viewer not supported on this platform: $e";
      });
    }
  }
  
  Future<void> _copyAssetsToTempDirectory() async {
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
      print("🟢 [VRMContainer] Assets copied to: ${vrmViewerDir.path}");
    } catch (e) {
      print("❌ [VRMContainer] Failed to copy assets: $e");
      throw e;
    }
  }
  
  Future<void> _initializeDesktopWebView() async {
    if (_htmlPath == null) {
      print("❌ [VRMContainer] HTML path is null, cannot initialize WebView");
      return;
    }
    
    try {
      print("🔧 [VRMContainer] Initializing desktop WebView...");
      print("🔧 [VRMContainer] HTML path: $_htmlPath");
      
      _desktopWebviewController = WebviewController();
      
      print("🔧 [VRMContainer] WebView controller created, initializing...");
      await _desktopWebviewController!.initialize();
      
      print("🔧 [VRMContainer] WebView initialized, loading URL...");
      // Load the HTML file
      await _desktopWebviewController!.loadUrl('file:///${_htmlPath!}');
      
      print("🟢 [VRMContainer] Desktop WebView initialized successfully");
      setState(() {
        _isWebViewReady = true;
      });
      
      _checkAndLoadVRM();
    } catch (e) {
      print("❌ [VRMContainer] Failed to initialize Desktop WebView: $e");
      print("❌ [VRMContainer] WebView error stack trace: ${StackTrace.current}");
      throw e;
    }
  }
  
  Future<void> _initializeWebView() async {
    try {
      if (kIsWeb) {
        // For web, skip WebView and show information instead
        print("🌐 [VRMContainer] Running on web - WebView not supported, using fallback UI");
        setState(() {
          _isWebViewReady = false; // Use fallback UI on web
        });
        return;
      }
      
      _webViewController = WebViewController()
        ..setJavaScriptMode(JavaScriptMode.unrestricted)
        ..setNavigationDelegate(
          NavigationDelegate(
            onPageFinished: (String url) {
              print("🟢 [VRMContainer] WebView page finished loading");
              setState(() {
                _isWebViewReady = true;
              });
              _checkAndLoadVRM();
            },
          ),
        )
        ..enableZoom(false);
      
      if (_htmlPath != null) {
        await _webViewController!.loadFile(_htmlPath!);
      }
    } catch (e) {
      print("❌ [VRMContainer] Failed to initialize WebView: $e");
      throw e;
    }
  }
  
  Future<void> _checkAndLoadVRM() async {
    if (!_isWebViewReady) return;
    
    // Check if VRM viewer is ready
    await Future.delayed(const Duration(milliseconds: 500));
    await _executeJavaScript('''
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
    
    // Load VRM model if one is specified
    if (_currentVrmModel != null && _currentVrmModel!.isNotEmpty) {
      await _loadVRMModel(_currentVrmModel!);
    }
  }
  
  Future<void> _loadVRMModel(String vrmModel) async {
    if (!_isWebViewReady) return;
    
    try {
      // Get the VRM file from assets
      final vrmData = await rootBundle.load('assets/vrm_models/$vrmModel');
      final bytes = vrmData.buffer.asUint8List();
      
      print("🟢 [VRMContainer] Loading VRM model: $vrmModel (${bytes.length} bytes)");
      
      // Convert bytes to base64 for passing to JavaScript
      final base64Data = base64Encode(bytes);
      
      // Load the VRM model in the WebView using base64 data
      await _executeJavaScript('''
        if (window.loadVRM) {
          console.log("Loading VRM from base64 data: ${bytes.length} bytes");
          
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
      print("❌ [VRMContainer] Failed to load VRM model: $e");
    }
  }
  
  Future<void> _executeJavaScript(String script) async {
    if (_useDesktopWebview && _desktopWebviewController != null) {
      await _desktopWebviewController!.executeScript(script);
    } else if (_webViewController != null) {
      await _webViewController!.runJavaScript(script);
    }
  }
  
  // Expression control methods (matching chat_ui functionality)
  Future<void> triggerBlink() async {
    if (!_isWebViewReady) return;
    await _executeJavaScript('window.triggerBlink();');
  }
  
  Future<void> setExpression(String expressionName, double weight) async {
    if (!_isWebViewReady) return;
    await _executeJavaScript('window.setExpression("$expressionName", $weight);');
  }
  
  Future<void> setEmotion(String emotion) async {
    if (!_isWebViewReady) return;
    await _executeJavaScript('window.setEmotion("$emotion");');
  }
  
  Future<void> setLipSync(String phoneme) async {
    if (!_isWebViewReady) return;
    await _executeJavaScript('window.setLipSync("$phoneme");');
  }
  
  Future<void> clearLipSync() async {
    if (!_isWebViewReady) return;
    await _executeJavaScript('window.clearLipSync();');
  }
  
  Future<void> resetExpressions() async {
    if (!_isWebViewReady) return;
    await _executeJavaScript('window.resetExpressions();');
  }
  
  @override
  void didUpdateWidget(VRMContainer oldWidget) {
    super.didUpdateWidget(oldWidget);
    if (widget.vrmModel != _currentVrmModel) {
      _currentVrmModel = widget.vrmModel;
      if (_currentVrmModel != null && _currentVrmModel!.isNotEmpty) {
        _loadVRMModel(_currentVrmModel!);
      }
    }
  }
  
  @override
  Widget build(BuildContext context) {
    return Container(
      decoration: BoxDecoration(
        borderRadius: BorderRadius.circular(12),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.1),
            blurRadius: 10,
            offset: const Offset(0, 5),
          ),
        ],
      ),
      child: ClipRRect(
        borderRadius: BorderRadius.circular(12),
        child: _buildContent(),
      ),
    );
  }
  
  Widget _buildContent() {
    if (!_isWebViewSupported) {
      return _buildVRMFallback();
    }
    
    // Desktop WebView (Windows)
    if (_useDesktopWebview) {
      if (_desktopWebviewController == null) {
        return Container(
          color: const Color(0xFF1e1e1e),
          child: const Center(
            child: Column(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                CircularProgressIndicator(),
                SizedBox(height: 16),
                Text(
                  'Loading VRM Viewer...',
                  style: TextStyle(
                    fontSize: 18,
                    color: Colors.white,
                  ),
                ),
              ],
            ),
          ),
        );
      }
      
      return Webview(_desktopWebviewController!);
    }
    
    // Standard WebView (Mobile/Web)
    if (_htmlPath == null || _webViewController == null) {
      return Container(
        color: const Color(0xFF1e1e1e),
        child: const Center(
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              CircularProgressIndicator(),
              SizedBox(height: 16),
              Text(
                'Loading VRM Viewer...',
                style: TextStyle(
                  fontSize: 18,
                  color: Colors.white,
                ),
              ),
            ],
          ),
        ),
      );
    }
    
    return WebViewWidget(controller: _webViewController!);
  }
  
  Widget _buildVRMFallback() {
    return Container(
      color: const Color(0xFF1e1e1e),
      child: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            // VRM model icon/preview
            Container(
              width: 200,
              height: 200,
              decoration: BoxDecoration(
                color: Colors.purple.withOpacity(0.3),
                borderRadius: BorderRadius.circular(100),
                border: Border.all(color: Colors.purple, width: 2),
              ),
              child: const Icon(
                Icons.person,
                size: 120,
                color: Colors.purple,
              ),
            ),
            const SizedBox(height: 24),
            
            // Current persona/model info
            Text(
              _currentVrmModel != null ? 
                _getPersonaNameFromModel(_currentVrmModel!) : 
                'No Persona Selected',
              style: const TextStyle(
                fontSize: 24,
                fontWeight: FontWeight.bold,
                color: Colors.white,
              ),
            ),
            const SizedBox(height: 8),
            Text(
              _currentVrmModel ?? 'Select a persona to see their VRM model',
              style: const TextStyle(
                fontSize: 14,
                color: Colors.grey,
              ),
            ),
            
            const SizedBox(height: 32),
            
            // Simulation controls
            const Text(
              'VRM Expression Simulator',
              style: TextStyle(
                fontSize: 18,
                fontWeight: FontWeight.bold,
                color: Colors.white,
              ),
            ),
            const SizedBox(height: 16),
            
            // Expression buttons
            Wrap(
              spacing: 8,
              runSpacing: 8,
              children: [
                _buildExpressionButton('😊', 'Happy', () => setEmotion('happy')),
                _buildExpressionButton('😠', 'Angry', () => setEmotion('angry')),
                _buildExpressionButton('😢', 'Sad', () => setEmotion('sad')),
                _buildExpressionButton('😮', 'Surprised', () => setEmotion('surprised')),
                _buildExpressionButton('😌', 'Relaxed', () => setEmotion('relaxed')),
                _buildExpressionButton('😉', 'Blink', () => triggerBlink()),
              ],
            ),
            
            const SizedBox(height: 16),
            
            // Info text
            const Text(
              'VRM 3D viewer not available on this platform.\nUsing fallback persona display.',
              textAlign: TextAlign.center,
              style: TextStyle(
                fontSize: 12,
                color: Colors.grey,
              ),
            ),
          ],
        ),
      ),
    );
  }
  
  Widget _buildExpressionButton(String emoji, String label, VoidCallback onPressed) {
    return ElevatedButton(
      onPressed: () {
        onPressed();
        print("🎭 [VRMContainer] Triggered $label expression (simulated)");
      },
      style: ElevatedButton.styleFrom(
        backgroundColor: Colors.purple.withOpacity(0.3),
        foregroundColor: Colors.white,
        padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Text(emoji, style: const TextStyle(fontSize: 18)),
          const SizedBox(width: 6),
          Text(label, style: const TextStyle(fontSize: 12)),
        ],
      ),
    );
  }
  
  String _getPersonaNameFromModel(String modelFilename) {
    // Extract persona name from model filename
    if (modelFilename.contains('fuka')) return 'Fuka';
    if (modelFilename.contains('gwen')) return 'Gwen';
    if (modelFilename.contains('kenji')) return 'Kenji';
    if (modelFilename.contains('koan')) return 'Koan';
    if (modelFilename.contains('nika')) return 'Nika';
    return modelFilename.replaceAll('.vrm', '').replaceAll('_model', '');
  }
  
  @override
  void dispose() {
    super.dispose();
  }
}
