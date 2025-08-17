import 'dart:convert';
import 'dart:io';
import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:webview_flutter/webview_flutter.dart';
import 'package:webview_windows/webview_windows.dart';
import 'package:path_provider/path_provider.dart';
import '../services/vrm_expression_manager.dart';
import '../services/vrm_model_loader.dart';
import '../services/vrm_assets_service.dart';
import '../services/webview_js_executor.dart';
import '../services/webview_service.dart';
import 'vrm_animation_controls.dart';
import 'vrm_fallback.dart';
import 'vrm_expression_controls.dart';
import '../helpers/vrm_logic.dart';
import '../helpers/vrm_helpers.dart';
import 'vrm_loading_overlay.dart';

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
  VRMExpressionManager? _expressionManager;
  VRMModelLoader? _vrmModelLoader;
  VRMAssetsService? _vrmAssetsService;
  WebViewJSExecutor? _jsExecutor;
  WebViewService? _webViewService;
  bool _isWebViewReady = false;
  bool _isWebViewSupported = true;
  bool _useDesktopWebview = false;
  bool _isLoadingVRM = false;
  bool _showLoadingOverlay = true; // Show loading overlay initially
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
    
    // Initialize WebView JS Executor
    _jsExecutor = WebViewJSExecutor(useDesktopWebview: _useDesktopWebview);
    
    // Initialize VRM Assets Service
    _vrmAssetsService = VRMAssetsService();
    
    // Initialize VRM Expression Manager
    _expressionManager = VRMExpressionManager();
    
    // Initialize VRM Model Loader
    _vrmModelLoader = VRMModelLoader(
      executeJavaScript: _executeJavaScript,
      setState: setState,
      isWebViewReady: () => _isWebViewReady,
      isLoadingVRM: () => _isLoadingVRM,
      setLoadingVRM: (loading) => _isLoadingVRM = loading,
      getCurrentVrmModel: () => _currentVrmModel,
      setAnimations: (animations, discovered) {
        setState(() {
          _availableAnimations = animations;
          _animationsDiscovered = discovered;
        });
      },
      onAnimationStarted: () {
        setState(() {
          _showLoadingOverlay = false;
        });
      },
    );
    
    // Initialize WebView Service
    _webViewService = WebViewService.create(
      useDesktopWebview: _useDesktopWebview,
      onWebViewReady: () {
        setState(() {
          _isWebViewReady = true;
        });
      },
      jsExecutor: _jsExecutor!,
      expressionManager: _expressionManager,
      vrmModelLoader: _vrmModelLoader,
    );
    
    _setupVRMViewer();
  }
  
  /// Wrapper method for JavaScript execution using the service
  Future<String> _executeJavaScript(String script) async {
    return await _jsExecutor?.executeJavaScript(script) ?? '';
  }
  
  Future<void> _setupVRMViewer() async {
    try {
      print("🔧 [VRMContainer] Starting VRM viewer setup...");
      print("🔧 [VRMContainer] Platform: ${Platform.operatingSystem}");
      print("🔧 [VRMContainer] Using desktop webview: $_useDesktopWebview");
      
      // Copy assets to temporary directory
      await _vrmAssetsService?.copyAssetsToTempDirectory();
      _htmlPath = _vrmAssetsService?.htmlPath;
      
      if (_htmlPath != null) {
        // Initialize the appropriate WebView service
        await _webViewService?.initialize(_htmlPath!);
      } else {
        throw Exception("HTML path is null after copying assets");
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
  
  // Animation control methods
  Future<void> playAnimation(String animationName, {bool loop = false}) async {
    await VRMLogic.playAnimation(
      animationName: animationName,
      executeJavaScript: _executeJavaScript,
      isWebViewReady: _isWebViewReady,
      loop: loop,
    );
  }

  Future<void> stopAnimation() async {
    await VRMLogic.stopAnimation(
      executeJavaScript: _executeJavaScript,
    );
  }
  
  // Expression control methods
  Future<void> triggerBlink() async => _expressionManager?.triggerBlink();
  Future<void> setExpression(String expressionName, double weight) async => _expressionManager?.setExpression(expressionName, weight);
  Future<void> setEmotion(String emotion) async => _expressionManager?.setEmotion(emotion);
  Future<void> setLipSync(String phoneme) async => _expressionManager?.setLipSync(phoneme);
  Future<void> clearLipSync() async => _expressionManager?.clearLipSync();
  Future<void> resetExpressions() async => _expressionManager?.resetExpressions();
  Future<void> startVoiceLipSync(String text, {required double audioDuration}) async => _expressionManager?.startVoiceLipSync(text, audioDuration: audioDuration);
  Future<void> startTextLipSync(String text, {double durationPerWord = 0.15}) async => _expressionManager?.startTextLipSync(text, durationPerWord: durationPerWord);
  Future<void> stopLipSync() async => _expressionManager?.stopLipSync();
  
  @override
  void didUpdateWidget(VRMContainer oldWidget) {
    super.didUpdateWidget(oldWidget);
    if (widget.vrmModel != _currentVrmModel) {
      _currentVrmModel = widget.vrmModel;
      
      // Show loading overlay when switching VRMs
      setState(() {
        _showLoadingOverlay = true;
      });
      
      if (_currentVrmModel != null && _currentVrmModel!.isNotEmpty) {
        // First clear any existing VRM, then load the new one
        _vrmModelLoader?.clearExistingVRM().then((_) {
          _vrmModelLoader?.loadVRMModel(_currentVrmModel!);
        });
      } else {
        // If no VRM model specified, just clear existing
        _vrmModelLoader?.clearExistingVRM().then((_) {
          // Hide loading overlay if no VRM to load
          setState(() {
            _showLoadingOverlay = false;
          });
        });
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
    // Wrap everything in a Stack to add the loading overlay
    return Stack(
      children: [
        _buildWebViewContent(),
        // Loading overlay
        VRMLoadingOverlayAnimated(
          isVisible: _showLoadingOverlay,
          loadingText: 'Loading VRM...',
        ),
      ],
    );
  }
  
  Widget _buildWebViewContent() {
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
      final desktopService = _webViewService as DesktopWebViewService?;
      if (desktopService?.controller == null) {
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
          Webview(desktopService!.controller!),
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
    final mobileService = _webViewService as MobileWebViewService?;
    if (_htmlPath == null || mobileService?.controller == null) {
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
        WebViewWidget(controller: mobileService!.controller!),
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
    _vrmModelLoader?.dispose();
    _vrmAssetsService?.dispose();
    _jsExecutor?.dispose();
    _webViewService?.dispose();
    super.dispose();
  }
}
