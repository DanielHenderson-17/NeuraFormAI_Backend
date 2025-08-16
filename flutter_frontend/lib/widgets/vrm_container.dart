import 'dart:convert';
import 'dart:io';
import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:webview_flutter/webview_flutter.dart';
import 'package:webview_windows/webview_windows.dart';
import 'package:path_provider/path_provider.dart';
import '../services/vrm_expression_manager.dart';
import 'vrm_animation_controls.dart';
import 'vrm_fallback.dart';
import 'vrm_expression_controls.dart';
import '../helpers/vrm_logic.dart';
import '../helpers/vrm_helpers.dart';

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

  // Public methods to access VRM functions from parent widgets
  static _VRMContainerState? of(BuildContext context) {
    return context.findAncestorStateOfType<_VRMContainerState>();
  }
}

class _VRMContainerState extends State<VRMContainer> {
  WebViewController? _webViewController;
  WebviewController? _desktopWebviewController;
  VRMExpressionManager? _expressionManager;
  bool _isWebViewReady = false;
  bool _isWebViewSupported = true;
  bool _useDesktopWebview = false;
  bool _isLoadingVRM = false;
  String? _currentVrmModel;
  String? _htmlPath;
  String? _errorMessage;
  List<Map<String, String>> _availableAnimations = [];
  bool _animationsDiscovered = false;
  
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
      
      // Initialize expression manager with the webview controller
      _expressionManager = VRMExpressionManager();
      await _expressionManager!.initialize(_desktopWebviewController!);
      
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
    
    // Discover available animations
    final animations = await VRMLogic.discoverAvailableAnimations();
    setState(() {
      _availableAnimations = animations;
      _animationsDiscovered = true;
    });
    
    // Load VRM model if one is specified
    if (_currentVrmModel != null && _currentVrmModel!.isNotEmpty) {
      await _loadVRMModel(_currentVrmModel!);
    }
  }
  
  Future<void> _clearExistingVRM() async {
    if (!_isWebViewReady) return;
    
    try {
      print("🧹 [VRMContainer] Clearing existing VRM model");
      
      await _executeJavaScript('''
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
      print("❌ [VRMContainer] Failed to clear existing VRM: $e");
    }
  }
  
  Future<void> _loadVRMModel(String vrmModel) async {
    if (!_isWebViewReady || _isLoadingVRM) return;
    _isLoadingVRM = true;
    try {
      // Use VRMLogic helper to get base64 data
      final base64Data = await VRMLogic.loadVRMModel(vrmModel);
      print("🟢 [VRMContainer] Loading VRM model: $vrmModel");
      await _executeJavaScript('''
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
      print("❌ [VRMContainer] Failed to load VRM model: $e");
    } finally {
      _isLoadingVRM = false;
    }
  }
  
  Future<String> _executeJavaScript(String script) async {
    try {
      if (_useDesktopWebview && _desktopWebviewController != null) {
        final result = await _desktopWebviewController!.executeScript(script);
        return result ?? '';
      } else if (_webViewController != null) {
        // For mobile WebView, runJavaScript returns void, so we need to use runJavaScriptReturningResult
        try {
          final result = await _webViewController!.runJavaScriptReturningResult(script);
          return result?.toString() ?? '';
        } catch (e) {
          // Fallback to regular runJavaScript if the returning result method fails
          await _webViewController!.runJavaScript(script);
          return '';
        }
      }
      return '';
    } catch (e) {
      print("❌ [VRMContainer] JavaScript execution error: $e");
      return '';
    }
  }
  
  // Expression control methods (now using VRMExpressionManager)
  Future<void> triggerBlink() async {
    if (_expressionManager != null) {
      await _expressionManager!.triggerBlink();
    } else {
      // Fallback for when expression manager is not available
      if (!_isWebViewReady) return;
      await _executeJavaScript('window.triggerBlink();');
    }
  }
  
  Future<void> setExpression(String expressionName, double weight) async {
    if (!_isWebViewReady) return;
    await _executeJavaScript('window.setExpression("$expressionName", $weight);');
  }
  
  Future<void> setEmotion(String emotion) async {
    if (_expressionManager != null) {
      await _expressionManager!.setEmotion(emotion);
    } else {
      // Fallback
      if (!_isWebViewReady) return;
      await _executeJavaScript('window.setEmotion("$emotion");');
    }
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
    if (_expressionManager != null) {
      await _expressionManager!.clearAllExpressions();
    } else {
      // Fallback
      if (!_isWebViewReady) return;
      await _executeJavaScript('window.resetExpressions();');
    }
  }

  // New methods for voice-synchronized lip sync
  Future<void> startVoiceLipSync(String text, {required double audioDuration}) async {
    if (_expressionManager != null) {
      await _expressionManager!.startVoiceLipSync(text, audioDuration: audioDuration);
    } else {
      print("⚠️ [VRMContainer] Expression manager not available for voice lip sync");
    }
  }

  Future<void> startTextLipSync(String text, {double durationPerWord = 0.15}) async {
    if (_expressionManager != null) {
      await _expressionManager!.startTextLipSync(text, durationPerWord: durationPerWord);
    } else {
      print("⚠️ [VRMContainer] Expression manager not available for text lip sync");
    }
  }

  Future<void> stopLipSync() async {
    if (_expressionManager != null) {
      await _expressionManager!.stopLipSync();
    } else {
      await clearLipSync();
    }
  }


  // Animation control methods
  Future<void> playAnimation(String animationName) async {
    await VRMLogic.playAnimation(
      animationName: animationName,
      executeJavaScript: _executeJavaScript,
      isWebViewReady: _isWebViewReady,
    );
  }

  Future<void> stopAnimation() async {
    await VRMLogic.stopAnimation(
      executeJavaScript: _executeJavaScript,
    );
  }
  
  @override
  void didUpdateWidget(VRMContainer oldWidget) {
    super.didUpdateWidget(oldWidget);
    if (widget.vrmModel != _currentVrmModel) {
      _currentVrmModel = widget.vrmModel;
      if (_currentVrmModel != null && _currentVrmModel!.isNotEmpty) {
        // First clear any existing VRM, then load the new one
        _clearExistingVRM().then((_) {
          _loadVRMModel(_currentVrmModel!);
        });
      } else {
        // If no VRM model specified, just clear existing
        _clearExistingVRM();
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
      return VRMFallback(
        currentVrmModel: _currentVrmModel,
        availableAnimations: _availableAnimations,
        animationsDiscovered: _animationsDiscovered,
        onPlayAnimation: (name) => playAnimation(name),
        onStopAnimation: () => stopAnimation(),
        onSetEmotion: (emotion) => setEmotion(emotion),
        onBlink: () => triggerBlink(),
      );
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
      
      return Stack(
        children: [
          Webview(_desktopWebviewController!),
          VRMAnimationControls(
            animationsDiscovered: _animationsDiscovered,
            availableAnimations: _availableAnimations,
            onPlayAnimation: (name) => playAnimation(name),
            onStopAnimation: () => stopAnimation(),
          ),
          VRMExpressionControls(
            onSetEmotion: (emotion) => setEmotion(emotion),
            onBlink: () => triggerBlink(),
          ),
        ],
      );
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
    
    return Stack(
      children: [
        WebViewWidget(controller: _webViewController!),
        VRMAnimationControls(
          animationsDiscovered: _animationsDiscovered,
          availableAnimations: _availableAnimations,
          onPlayAnimation: (name) => playAnimation(name),
          onStopAnimation: () => stopAnimation(),
        ),
        VRMExpressionControls(
          onSetEmotion: (emotion) => setEmotion(emotion),
          onBlink: () => triggerBlink(),
        ),
      ],
    );
  }
  
  @override
  void dispose() {
    _expressionManager?.dispose();
    super.dispose();
  }
}
