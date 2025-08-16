import 'package:webview_flutter/webview_flutter.dart';
import 'package:webview_windows/webview_windows.dart';

/// Service responsible for executing JavaScript in WebViews across different platforms
/// Extracted from VRMContainer to reduce complexity and provide cross-platform JS execution
class WebViewJSExecutor {
  WebViewController? _webViewController;
  WebviewController? _desktopWebviewController;
  bool _useDesktopWebview;
  
  /// Constructor
  WebViewJSExecutor({
    required bool useDesktopWebview,
  }) : _useDesktopWebview = useDesktopWebview;
  
  /// Set the mobile WebView controller
  void setMobileWebViewController(WebViewController? controller) {
    _webViewController = controller;
  }
  
  /// Set the desktop WebView controller
  void setDesktopWebViewController(WebviewController? controller) {
    _desktopWebviewController = controller;
  }
  
  /// Execute JavaScript code in the appropriate WebView
  Future<String> executeJavaScript(String script) async {
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
      print("❌ [WebViewJSExecutor] JavaScript execution error: $e");
      return '';
    }
  }
  
  /// Check if a WebView controller is available for execution
  bool get isReady {
    if (_useDesktopWebview) {
      return _desktopWebviewController != null;
    } else {
      return _webViewController != null;
    }
  }
  
  /// Clean up resources
  void dispose() {
    _webViewController = null;
    _desktopWebviewController = null;
  }
}
