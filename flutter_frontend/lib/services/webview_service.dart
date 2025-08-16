import 'dart:io';
import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';
import 'package:webview_flutter/webview_flutter.dart';
import 'package:webview_windows/webview_windows.dart';
import '../services/vrm_expression_manager.dart';
import '../services/webview_js_executor.dart';
import '../services/vrm_model_loader.dart';

/// Abstract base class for WebView services
abstract class WebViewService {
  /// Initialize the WebView with the given HTML path
  Future<void> initialize(String htmlPath);
  
  /// Check if the WebView is ready
  bool get isReady;
  
  /// Clean up resources
  void dispose();
  
  /// Factory constructor to create the appropriate WebView service
  static WebViewService create({
    required bool useDesktopWebview,
    required VoidCallback onWebViewReady,
    required WebViewJSExecutor jsExecutor,
    required VRMExpressionManager? expressionManager,
    required VRMModelLoader? vrmModelLoader,
  }) {
    if (useDesktopWebview) {
      return DesktopWebViewService(
        onWebViewReady: onWebViewReady,
        jsExecutor: jsExecutor,
        expressionManager: expressionManager,
        vrmModelLoader: vrmModelLoader,
      );
    } else {
      return MobileWebViewService(
        onWebViewReady: onWebViewReady,
        jsExecutor: jsExecutor,
        vrmModelLoader: vrmModelLoader,
      );
    }
  }
}

/// Desktop WebView service implementation
class DesktopWebViewService extends WebViewService {
  WebviewController? _controller;
  final VoidCallback _onWebViewReady;
  final WebViewJSExecutor _jsExecutor;
  final VRMExpressionManager? _expressionManager;
  final VRMModelLoader? _vrmModelLoader;
  bool _isReady = false;

  DesktopWebViewService({
    required VoidCallback onWebViewReady,
    required WebViewJSExecutor jsExecutor,
    required VRMExpressionManager? expressionManager,
    required VRMModelLoader? vrmModelLoader,
  })  : _onWebViewReady = onWebViewReady,
        _jsExecutor = jsExecutor,
        _expressionManager = expressionManager,
        _vrmModelLoader = vrmModelLoader;

  @override
  Future<void> initialize(String htmlPath) async {
    try {
      print("🔧 [DesktopWebViewService] Initializing desktop WebView...");
      print("🔧 [DesktopWebViewService] HTML path: $htmlPath");
      
      _controller = WebviewController();
      
      print("🔧 [DesktopWebViewService] WebView controller created, initializing...");
      await _controller!.initialize();
      
      print("🔧 [DesktopWebViewService] WebView initialized, loading URL...");
      await _controller!.loadUrl('file:///$htmlPath');
      
      print("🟢 [DesktopWebViewService] Desktop WebView initialized successfully");
      _isReady = true;
      
      // Set the controller in the JS executor
      _jsExecutor.setDesktopWebViewController(_controller);
      
      // Initialize expression manager with the webview controller
      if (_expressionManager != null) {
        await _expressionManager!.initialize(_controller!);
      }
      
      // Notify that WebView is ready
      _onWebViewReady();
      
      // Check and load VRM
      await _vrmModelLoader?.checkAndLoadVRM();
    } catch (e) {
      print("❌ [DesktopWebViewService] Failed to initialize Desktop WebView: $e");
      print("❌ [DesktopWebViewService] WebView error stack trace: ${StackTrace.current}");
      throw e;
    }
  }

  @override
  bool get isReady => _isReady;

  /// Get the desktop WebView controller
  WebviewController? get controller => _controller;

  @override
  void dispose() {
    _controller = null;
    _isReady = false;
  }
}

/// Mobile WebView service implementation
class MobileWebViewService extends WebViewService {
  WebViewController? _controller;
  final VoidCallback _onWebViewReady;
  final WebViewJSExecutor _jsExecutor;
  final VRMModelLoader? _vrmModelLoader;
  bool _isReady = false;

  MobileWebViewService({
    required VoidCallback onWebViewReady,
    required WebViewJSExecutor jsExecutor,
    required VRMModelLoader? vrmModelLoader,
  })  : _onWebViewReady = onWebViewReady,
        _jsExecutor = jsExecutor,
        _vrmModelLoader = vrmModelLoader;

  @override
  Future<void> initialize(String htmlPath) async {
    try {
      if (kIsWeb) {
        // For web, skip WebView and show information instead
        print("🌐 [MobileWebViewService] Running on web - WebView not supported, using fallback UI");
        _isReady = false; // Use fallback UI on web
        _onWebViewReady();
        return;
      }
      
      _controller = WebViewController()
        ..setJavaScriptMode(JavaScriptMode.unrestricted)
        ..setNavigationDelegate(
          NavigationDelegate(
            onPageFinished: (String url) {
              print("🟢 [MobileWebViewService] WebView page finished loading");
              _isReady = true;
              
              // Set the controller in the JS executor
              _jsExecutor.setMobileWebViewController(_controller);
              
              // Notify that WebView is ready
              _onWebViewReady();
              
              // Check and load VRM
              _vrmModelLoader?.checkAndLoadVRM();
            },
          ),
        )
        ..enableZoom(false);
      
      await _controller!.loadFile(htmlPath);
    } catch (e) {
      print("❌ [MobileWebViewService] Failed to initialize WebView: $e");
      throw e;
    }
  }

  @override
  bool get isReady => _isReady;

  /// Get the mobile WebView controller
  WebViewController? get controller => _controller;

  @override
  void dispose() {
    _controller = null;
    _isReady = false;
  }
}
