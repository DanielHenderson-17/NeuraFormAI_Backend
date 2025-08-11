import 'dart:convert';
import 'dart:io';
import 'dart:async';
import 'package:http/http.dart' as http;
import 'package:shared_preferences/shared_preferences.dart';
import 'package:url_launcher/url_launcher.dart';
import '../config/app_config.dart';

class AuthService {
  static String? _userId;
  static String? _userEmail;
  static String? _userName;
  static String? _userFirstName;
  static String? _userLastName;
  static String? _userPicture;
  static String? _sessionToken;
  
  // Backend configuration
  static const String _backendBaseUrl = AppConfig.backendBaseUrl;
  
  // Google OAuth configuration
  static const String _googleClientId = AppConfig.googleClientId;
  static const String _googleClientSecret = AppConfig.googleClientSecret;
  
  static String? get userId => _userId;
  static String? get userEmail => _userEmail;
  static String? get userName => _userName;
  static String? get userFirstName => _userFirstName;
  static String? get userLastName => _userLastName;
  static String? get userPicture => _userPicture;
  static String? get sessionToken => _sessionToken;
  
  static Future<bool> isSignedIn() async {
    if (_sessionToken != null) {
      // Validate the stored token
      if (await _validateSession()) {
        return true;
      }
    }
    
    // Check local storage
    try {
      final prefs = await SharedPreferences.getInstance();
      _sessionToken = prefs.getString('session_token');
      _userId = prefs.getString('user_id');
      _userEmail = prefs.getString('user_email');
      _userName = prefs.getString('user_name');
      _userFirstName = prefs.getString('user_first_name');
      _userLastName = prefs.getString('user_last_name');
      _userPicture = prefs.getString('user_picture');
      
      if (_sessionToken != null) {
        return await _validateSession();
      }
    } catch (e) {
      print("❌ [AuthService] Error checking sign-in status: $e");
    }
    
    return false;
  }
  
  static Future<bool> _validateSession() async {
    if (_sessionToken == null) return false;
    
    try {
      final response = await http.get(
        Uri.parse('$_backendBaseUrl/api/auth/profile'),
        headers: _getHeaders(),
      ).timeout(const Duration(seconds: 10));
      
      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        _userId = data['id']?.toString();
        _userEmail = data['email'];
        _userName = data['name'];
        _userFirstName = data['first_name'];
        _userLastName = data['last_name'];
        _userPicture = data['picture'];
        return true;
      } else {
        // Token is invalid, clear it
        await _clearSession();
        return false;
      }
    } catch (e) {
      print("❌ [AuthService] Session validation error: $e");
      await _clearSession();
      return false;
    }
  }
  
  static Map<String, String> _getHeaders() {
    if (_sessionToken == null) {
      return {'Content-Type': 'application/json'};
    }
    return {
      'Content-Type': 'application/json',
      'Authorization': 'Bearer $_sessionToken',
    };
  }
  
  static Future<bool> signInWithGoogle() async {
    try {
      print("🔐 [AuthService] Starting Google Sign-In...");
      
      // Use the local GSI approach like Python implementation
      final idToken = await _getGoogleIdToken();
      if (idToken == null) {
        print("❌ [AuthService] Failed to get Google ID token");
        return false;
      }
      
      // Send to backend for authentication
      final loginResult = await _authenticateWithBackend(idToken);
      if (loginResult.success) {
        // Set the user info before saving session
        _userFirstName = loginResult.tokenFirstName;
        _userLastName = loginResult.tokenLastName;
        _userEmail = loginResult.tokenEmail;
        
        await _saveSession(loginResult.sessionToken!);
        return true;
      } else if (loginResult.requiresRegistration) {
        // Handle registration
        return await _handleRegistration(loginResult);
      } else {
        print("❌ [AuthService] Login failed: ${loginResult.message}");
        return false;
      }
    } catch (e) {
      print("❌ [AuthService] Google Sign-In error: $e");
      return false;
    }
  }
  
  static LocalGsiServer? _currentServer;
  
  static Future<String?> _getGoogleIdToken() async {
    try {
      print("🔐 [AuthService] Using desktop OAuth flow (like Python frontend)");
      
      // Use desktop OAuth flow - open browser directly to Google OAuth
      // This matches the Python InstalledAppFlow behavior
      final authUrl = _buildDesktopOAuthUrl();
      print("🌐 [AuthService] Opening Google OAuth: $authUrl");
      
      // Start local server to receive the authorization code
      final server = await _startOAuthCallbackServer();
      if (server == null) return null;
      
      _currentServer = server;
      
      // Open browser to Google OAuth
      bool launched = false;
      try {
        launched = await launchUrl(
          Uri.parse(authUrl),
          mode: LaunchMode.externalApplication,
        );
      } catch (e) {
        print("⚠️ [AuthService] Failed to open browser: $e");
      }
      
      if (!launched) {
        print("❌ [AuthService] Failed to open browser");
        print("🔧 [AuthService] Please manually open: $authUrl");
      }
      
      // Wait for authorization code
      print("⏳ [AuthService] Waiting for authorization code...");
      final authCode = await server.waitForAuthCode(const Duration(minutes: 2));
      
      if (authCode == null) {
        print("❌ [AuthService] No authorization code received");
        await server.stop();
        _currentServer = null;
        return null;
      }
      
      print("✅ [AuthService] Received authorization code");
      
      // Exchange authorization code for ID token
      final idToken = await _exchangeCodeForIdToken(authCode, server.port!);
      
      await server.stop();
      _currentServer = null;
      
      return idToken;
    } catch (e) {
      print("❌ [AuthService] Error in desktop OAuth flow: $e");
      if (_currentServer != null) {
        await _currentServer!.stop();
        _currentServer = null;
      }
      return null;
    }
  }
  
  static Future<LoginResult> _authenticateWithBackend(String idToken) async {
    try {
      print("🔑 [AuthService] Sending auth request to backend...");
      print("🔑 [AuthService] URL: $_backendBaseUrl/api/auth/login");
      print("🔑 [AuthService] Token length: ${idToken.length}");
      
      final response = await http.post(
        Uri.parse('$_backendBaseUrl/api/auth/login'),
        headers: {'Content-Type': 'application/json'},
        body: json.encode({
          'provider': 'google',
          'token': idToken,
          'device_info': {'platform': 'desktop', 'ui': 'flutter'},
        }),
      ).timeout(const Duration(seconds: 20));
      
      print("🔑 [AuthService] Backend response status: ${response.statusCode}");
      
      if (response.statusCode != 200) {
        return LoginResult(
          success: false,
          message: 'login_http_${response.statusCode}',
        );
      }
      
      final data = json.decode(response.body);
      if (data['success'] == true && data['session_token'] != null) {
        return LoginResult(
          success: true,
          sessionToken: data['session_token'],
        );
      }
      
      if (data['requires_registration'] == true || data['message'] == 'additional_info_required') {
        return LoginResult(
          success: false,
          requiresRegistration: true,
          idToken: idToken,
          tokenEmail: data['token_email'],
          tokenSub: data['token_sub'],
          tokenFirstName: data['token_first_name'],
          tokenLastName: data['token_last_name'],
        );
      }
      
      return LoginResult(
        success: false,
        message: data['message'],
      );
    } catch (e) {
      print("❌ [AuthService] Backend authentication error: $e");
      return LoginResult(
        success: false,
        message: 'network_error',
      );
    }
  }
  
  static Future<bool> _handleRegistration(LoginResult result) async {
    try {
      // For now, use default values - in a real app, you'd show a registration form
      final response = await http.post(
        Uri.parse('$_backendBaseUrl/api/auth/register'),
        headers: {'Content-Type': 'application/json'},
        body: json.encode({
          'provider': 'google',
          'provider_user_id': result.tokenSub ?? '',
          'first_name': result.tokenFirstName ?? '',
          'last_name': result.tokenLastName ?? '',
          'email': result.tokenEmail ?? '',
          'birthdate': '1990-01-01', // Default birthdate
        }),
      ).timeout(const Duration(seconds: 20));
      
      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        final token = data['session_token'];
        if (token != null) {
          // Set the user info before saving session
          _userFirstName = result.tokenFirstName;
          _userLastName = result.tokenLastName;
          _userEmail = result.tokenEmail;
          
          await _saveSession(token);
          return true;
        }
      }
      
      print("❌ [AuthService] Registration failed");
      return false;
    } catch (e) {
      print("❌ [AuthService] Registration error: $e");
      return false;
    }
  }
  
  static Future<void> _saveSession(String token) async {
    _sessionToken = token;
    
    try {
      final prefs = await SharedPreferences.getInstance();
      await prefs.setString('session_token', token);
      await prefs.setString('user_id', _userId ?? '');
      await prefs.setString('user_email', _userEmail ?? '');
      await prefs.setString('user_name', _userName ?? '');
      await prefs.setString('user_first_name', _userFirstName ?? '');
      await prefs.setString('user_last_name', _userLastName ?? '');
      await prefs.setString('user_picture', _userPicture ?? '');
    } catch (e) {
      print("❌ [AuthService] Error saving session: $e");
    }
  }
  
  static Future<void> signOut() async {
    try {
      // Invalidate backend session
      if (_sessionToken != null) {
        try {
          await http.post(
            Uri.parse('$_backendBaseUrl/api/auth/logout'),
            headers: _getHeaders(),
          ).timeout(const Duration(seconds: 10));
        } catch (e) {
          // Ignore backend logout errors
        }
      }
      
      await _clearSession();
      print("✅ [AuthService] Signed out successfully");
    } catch (e) {
      print("❌ [AuthService] Sign out error: $e");
    }
  }
  
  static Future<void> _clearSession() async {
    _sessionToken = null;
    _userId = null;
    _userEmail = null;
    _userName = null;
    _userFirstName = null;
    _userLastName = null;
    _userPicture = null;
    
    try {
      final prefs = await SharedPreferences.getInstance();
      await prefs.remove('session_token');
      await prefs.remove('user_id');
      await prefs.remove('user_email');
      await prefs.remove('user_name');
      await prefs.remove('user_first_name');
      await prefs.remove('user_last_name');
      await prefs.remove('user_picture');
    } catch (e) {
      print("❌ [AuthService] Error clearing session: $e");
    }
  }

  // Desktop OAuth flow methods (matching Python InstalledAppFlow)
  static String _buildDesktopOAuthUrl() {
    final params = {
      'client_id': _googleClientId,
      'redirect_uri': 'http://localhost:8787',
      'scope': 'openid email profile',
      'response_type': 'code',
      'access_type': 'offline',
      'include_granted_scopes': 'true',
    };
    
    final query = params.entries
        .map((e) => '${Uri.encodeComponent(e.key)}=${Uri.encodeComponent(e.value)}')
        .join('&');
    
    return 'https://accounts.google.com/o/oauth2/auth?$query';
  }

  static Future<LocalGsiServer?> _startOAuthCallbackServer() async {
    final server = LocalGsiServer();
    return await server.startOAuthServer();
  }

  static Future<String?> _exchangeCodeForIdToken(String authCode, int redirectPort) async {
    try {
      print("🔄 [AuthService] Exchanging authorization code for tokens...");
      
      final response = await http.post(
        Uri.parse('https://oauth2.googleapis.com/token'),
        headers: {'Content-Type': 'application/x-www-form-urlencoded'},
        body: {
          'code': authCode,
          'client_id': _googleClientId,
          'client_secret': _googleClientSecret,
          'redirect_uri': 'http://localhost:$redirectPort',
          'grant_type': 'authorization_code',
        },
      );

      if (response.statusCode != 200) {
        print("❌ [AuthService] Token exchange failed: ${response.statusCode}");
        print("❌ [AuthService] Response: ${response.body}");
        return null;
      }

      final data = json.decode(response.body);
      final idToken = data['id_token'];

      if (idToken != null) {
        print("✅ [AuthService] Successfully obtained ID token");
        return idToken;
      } else {
        print("❌ [AuthService] No ID token in response");
        return null;
      }
    } catch (e) {
      print("❌ [AuthService] Error exchanging code for token: $e");
      return null;
    }
  }
}

class LoginResult {
  final bool success;
  final String? sessionToken;
  final bool requiresRegistration;
  final String? message;
  final String? idToken;
  final String? tokenEmail;
  final String? tokenSub;
  final String? tokenFirstName;
  final String? tokenLastName;
  
  LoginResult({
    required this.success,
    this.sessionToken,
    this.requiresRegistration = false,
    this.message,
    this.idToken,
    this.tokenEmail,
    this.tokenSub,
    this.tokenFirstName,
    this.tokenLastName,
  });
}

class LocalGsiServer {
  HttpServer? _server;
  String? _idToken;
  String? _authCode;
  Completer<String?>? _tokenCompleter;
  Completer<String?>? _authCodeCompleter;
  int? _port;
  
  int? get port => _port;
  
  Future<LocalGsiServer?> start() async {
    try {
      // Try multiple ports to avoid conflicts
      final ports = [AppConfig.localGsiPort, 8788, 8789, 8790, 8791];
      
      for (final port in ports) {
        try {
          _server = await HttpServer.bind(InternetAddress.loopbackIPv4, port);
          _port = _server!.port;
          print("✅ [LocalGsiServer] Server started on port $_port");
          break;
        } catch (e) {
          print("⚠️ [LocalGsiServer] Port $port is busy, trying next...");
          continue;
        }
      }
      
      if (_server == null) {
        print("❌ [LocalGsiServer] All ports are busy");
        return null;
      }
      
      _server!.listen((HttpRequest request) {
        _handleRequest(request);
      });
      
      return this;
    } catch (e) {
      print("❌ [LocalGsiServer] Failed to start server: $e");
      return null;
    }
  }
  
  void _handleRequest(HttpRequest request) {
    if (request.method == 'GET' && request.uri.path == '/') {
      _serveSignInPage(request);
    } else if (request.method == 'POST' && request.uri.path == '/token') {
      _handleTokenPost(request);
    } else {
      request.response
        ..statusCode = HttpStatus.notFound
        ..close();
    }
  }
  
  void _serveSignInPage(HttpRequest request) {
    final html = _getSignInHtml();
    request.response
      ..statusCode = HttpStatus.ok
      ..headers.contentType = ContentType.html
      ..write(html)
      ..close();
  }
  
  void _handleTokenPost(HttpRequest request) {
    // Set response headers first
    request.response
      ..statusCode = HttpStatus.ok
      ..headers.contentType = ContentType.json
      ..headers.add('Access-Control-Allow-Origin', '*')
      ..headers.add('Access-Control-Allow-Methods', 'POST, OPTIONS')
      ..headers.add('Access-Control-Allow-Headers', 'Content-Type');
    
    // Handle preflight OPTIONS request
    if (request.method == 'OPTIONS') {
      request.response.close();
      return;
    }
    
    // Read the request body
    String bodyData = '';
    request.listen((List<int> data) {
      bodyData += String.fromCharCodes(data);
    }, onDone: () {
      try {
        print("📨 [LocalGsiServer] Received token data: $bodyData");
        final jsonData = json.decode(bodyData);
        _idToken = jsonData['credential'];
        
        if (_idToken != null) {
          print("✅ [LocalGsiServer] Successfully extracted ID token");
          print("🔍 [LocalGsiServer] Token starts with: ${_idToken!.substring(0, 20)}...");
          _tokenCompleter?.complete(_idToken);
        } else {
          print("❌ [LocalGsiServer] No credential in token data");
          print("🔍 [LocalGsiServer] Available keys: ${jsonData.keys.toList()}");
          _tokenCompleter?.complete(null);
        }
        
        // Send response
        request.response.write('{"status": "ok", "token_received": ${_idToken != null}}');
        request.response.close();
      } catch (e) {
        print("❌ [LocalGsiServer] Error parsing token: $e");
        _tokenCompleter?.complete(null);
        request.response.write('{"status": "error", "message": "$e"}');
        request.response.close();
      }
    }, onError: (error) {
      print("❌ [LocalGsiServer] Error reading request body: $error");
      _tokenCompleter?.complete(null);
      request.response.write('{"status": "error", "message": "Failed to read request body"}');
      request.response.close();
    });
  }
  
  String _getSignInHtml() {
    return '''
<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <title>Sign in with Google</title>
  <script src="https://accounts.google.com/gsi/client" async defer></script>
  <script>
    function handleCredentialResponse(resp) {
      fetch('/token', {
        method: 'POST', 
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({credential: resp.credential})
      }).then(() => {
        document.getElementById('status').innerText = 'Signed in. Closing…';
        setTimeout(() => { 
          try { window.close(); } catch(e) {} 
          try { window.open('', '_self'); window.close(); } catch(e) {} 
        }, 300);
      });
    }
    window.onload = () => {
      google.accounts.id.initialize({ 
        client_id: '${AuthService._googleClientId}', 
        callback: handleCredentialResponse 
      });
      google.accounts.id.renderButton(document.getElementById('gsi'), { 
        theme: 'outline', 
        size: 'large' 
      });
      google.accounts.id.prompt();
    };
  </script>
</head>
<body>
  <div id="gsi"></div>
  <p id="status">Sign in to generate an ID token…</p>
</body>
</html>
''';
  }
  
  Future<String?> waitForToken(Duration timeout) async {
    _tokenCompleter = Completer<String?>();
    
    // Set timeout
    Timer(timeout, () {
      if (!_tokenCompleter!.isCompleted) {
        print("⏰ [LocalGsiServer] Token wait timeout reached");
        _tokenCompleter!.complete(null);
      }
    });
    
    return await _tokenCompleter!.future;
  }

  Future<String?> waitForAuthCode(Duration timeout) async {
    _authCodeCompleter = Completer<String?>();
    
    // Set timeout
    Timer(timeout, () {
      if (!_authCodeCompleter!.isCompleted) {
        print("⏰ [LocalGsiServer] Auth code wait timeout reached");
        _authCodeCompleter!.complete(null);
      }
    });
    
    return await _authCodeCompleter!.future;
  }

  Future<LocalGsiServer?> startOAuthServer() async {
    try {
      // Try multiple ports to avoid conflicts
      final ports = [8787, 8788, 8789, 8790, 8791];
      
      for (final port in ports) {
        try {
          _server = await HttpServer.bind(InternetAddress.loopbackIPv4, port);
          _port = _server!.port;
          print("✅ [LocalGsiServer] OAuth server started on port $_port");
          break;
        } catch (e) {
          print("⚠️ [LocalGsiServer] Port $port is busy, trying next...");
          continue;
        }
      }
      
      if (_server == null) {
        print("❌ [LocalGsiServer] All ports are busy");
        return null;
      }
      
      _server!.listen((HttpRequest request) {
        _handleOAuthRequest(request);
      });
      
      return this;
    } catch (e) {
      print("❌ [LocalGsiServer] Failed to start OAuth server: $e");
      return null;
    }
  }

  void _handleOAuthRequest(HttpRequest request) {
    print("📥 [LocalGsiServer] OAuth request: ${request.method} ${request.uri}");
    
    if (request.method == 'GET' && request.uri.path == '/') {
      // Handle OAuth callback with authorization code
      final code = request.uri.queryParameters['code'];
      final error = request.uri.queryParameters['error'];
      
      if (error != null) {
        print("❌ [LocalGsiServer] OAuth error: $error");
        _authCodeCompleter?.complete(null);
        _sendOAuthResponse(request, false, error: error);
        return;
      }
      
      if (code != null) {
        print("✅ [LocalGsiServer] Received authorization code");
        _authCode = code;
        _authCodeCompleter?.complete(code);
        _sendOAuthResponse(request, true);
      } else {
        print("❌ [LocalGsiServer] No authorization code in callback");
        _authCodeCompleter?.complete(null);
        _sendOAuthResponse(request, false, error: "No authorization code");
      }
    } else {
      request.response
        ..statusCode = HttpStatus.notFound
        ..close();
    }
  }

  void _sendOAuthResponse(HttpRequest request, bool success, {String? error}) {
    final html = '''
<!DOCTYPE html>
<html>
<head>
  <title>NeuraFormAI - OAuth</title>
  <style>
    body { 
      font-family: Arial, sans-serif; 
      text-align: center; 
      padding: 50px; 
      background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
      color: white;
      margin: 0;
      min-height: 100vh;
      display: flex;
      flex-direction: column;
      justify-content: center;
      align-items: center;
    }
    .container {
      background: rgba(255, 255, 255, 0.1);
      padding: 40px;
      border-radius: 20px;
      backdrop-filter: blur(10px);
      box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
      max-width: 400px;
      width: 100%;
    }
    h2 { 
      margin: 0 0 20px 0; 
      font-size: 24px;
      font-weight: 300;
    }
    p {
      font-size: 16px;
      opacity: 0.9;
    }
  </style>
</head>
<body>
  <div class="container">
    <h2>${success ? '✅ Success!' : '❌ Error'}</h2>
    <p>${success ? 'Authentication successful. You can close this window.' : 'Authentication failed: ${error ?? 'Unknown error'}'}</p>
  </div>
  <script>
    setTimeout(() => {
      try { window.close(); } catch(e) { console.log('Could not close window'); }
    }, 2000);
  </script>
</body>
</html>
''';
    
    request.response
      ..statusCode = HttpStatus.ok
      ..headers.contentType = ContentType.html
      ..write(html)
      ..close();
  }
  
  Future<void> stop() async {
    if (_server != null) {
      await _server!.close();
      _server = null;
      print("✅ [LocalGsiServer] Server stopped");
    }
  }
}

Future<LocalGsiServer?> _startLocalGsiServer() async {
  final server = LocalGsiServer();
  return await server.start();
}
