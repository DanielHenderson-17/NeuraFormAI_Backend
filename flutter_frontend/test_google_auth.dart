import 'dart:io';
import 'dart:convert';
import 'dart:async';
import 'package:http/http.dart' as http;
import 'lib/config/app_config.dart';

// Simple test script to debug Google authentication
void main() async {
  print('🧪 Testing Google Authentication...');
  
  // Check configuration
  if (!AppConfig.isValid) {
    print('❌ Invalid configuration. Please check your Google OAuth credentials.');
    return;
  }
  
  print('✅ Configuration is valid');
  print('🔑 Google Client ID: ${AppConfig.googleClientId}');
  print('🌐 Backend URL: ${AppConfig.backendBaseUrl}');
  
  // Test local server
  print('\n🚀 Starting local GSI server...');
  final server = await _startTestServer();
  if (server == null) {
    print('❌ Failed to start server');
    return;
  }
  
  print('✅ Server started on port ${server.port}');
  print('🌐 Open this URL in your browser: http://127.0.0.1:${server.port}');
  
  // Wait for token
  print('⏳ Waiting for Google ID token...');
  final token = await server.waitForToken(const Duration(minutes: 2));
  
  if (token != null) {
    print('✅ Successfully received Google ID token!');
    print('🔐 Token length: ${token.length} characters');
    
    // Test backend authentication
    print('\n🔐 Testing backend authentication...');
    final success = await _testBackendAuth(token);
    if (success) {
      print('✅ Backend authentication successful!');
    } else {
      print('❌ Backend authentication failed');
    }
  } else {
    print('❌ No token received within timeout');
  }
  
  // Clean up
  await server.stop();
  print('\n🧹 Test completed');
}

class TestGsiServer {
  HttpServer? _server;
  String? _idToken;
  Completer<String?>? _tokenCompleter;
  int? _port;
  
  int? get port => _port;
  
  Future<TestGsiServer?> start() async {
    try {
      // Try multiple ports
      final ports = [AppConfig.localGsiPort, 8788, 8789, 8790, 8791];
      
      for (final port in ports) {
        try {
          _server = await HttpServer.bind(InternetAddress.loopbackIPv4, port);
          _port = _server!.port;
          print('✅ Server started on port $_port');
          break;
        } catch (e) {
          print('⚠️ Port $port is busy, trying next...');
          continue;
        }
      }
      
      if (_server == null) {
        print('❌ All ports are busy');
        return null;
      }
      
      _server!.listen((HttpRequest request) {
        _handleRequest(request);
      });
      
      return this;
    } catch (e) {
      print('❌ Failed to start server: $e');
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
    request.response
      ..statusCode = HttpStatus.ok
      ..headers.contentType = ContentType.json
      ..write('{"status": "ok"}')
      ..close();
    
    String bodyData = '';
    request.listen((List<int> data) {
      bodyData += String.fromCharCodes(data);
    }, onDone: () {
      try {
        print('📨 Received token data: ${bodyData.length} characters');
        final jsonData = json.decode(bodyData);
        _idToken = jsonData['credential'];
        
        if (_idToken != null) {
          print('✅ Successfully extracted ID token');
          _tokenCompleter?.complete(_idToken);
        } else {
          print('❌ No credential in token data');
          _tokenCompleter?.complete(null);
        }
      } catch (e) {
        print('❌ Error parsing token: $e');
        _tokenCompleter?.complete(null);
      }
    });
  }
  
  String _getSignInHtml() {
    return '''
<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <title>Test Google Sign-In</title>
  <script src="https://accounts.google.com/gsi/client" async defer></script>
  <style>
    body { font-family: Arial, sans-serif; text-align: center; padding: 50px; }
    #gsi { margin: 20px 0; }
    #status { color: #666; }
  </style>
</head>
<body>
  <h2>Test Google Sign-In</h2>
  <div id="gsi"></div>
  <p id="status">Sign in to generate an ID token...</p>
  
  <script>
    function handleCredentialResponse(resp) {
      console.log('Google Sign-In response received');
      
      if (!resp.credential) {
        document.getElementById('status').textContent = 'No credential received';
        return;
      }
      
      console.log('Sending credential to local server...');
      
      fetch('/token', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({credential: resp.credential})
      })
      .then(() => {
        document.getElementById('status').textContent = 'Signed in successfully!';
        console.log('Token sent successfully');
      })
      .catch(error => {
        console.error('Error sending token:', error);
        document.getElementById('status').textContent = 'Error sending token';
      });
    }
    
    window.onload = () => {
      console.log('Initializing Google Sign-In...');
      
      google.accounts.id.initialize({
        client_id: '${AppConfig.googleClientId}',
        callback: handleCredentialResponse
      });
      
      google.accounts.id.renderButton(document.getElementById('gsi'), {
        theme: 'outline',
        size: 'large'
      });
      
      google.accounts.id.prompt();
    };
  </script>
</body>
</html>
''';
  }
  
  Future<String?> waitForToken(Duration timeout) async {
    _tokenCompleter = Completer<String?>();
    
    Timer(timeout, () {
      if (!_tokenCompleter!.isCompleted) {
        print('⏰ Token wait timeout reached');
        _tokenCompleter!.complete(null);
      }
    });
    
    return await _tokenCompleter!.future;
  }
  
  Future<void> stop() async {
    if (_server != null) {
      await _server!.close();
      _server = null;
      print('✅ Server stopped');
    }
  }
}

Future<TestGsiServer?> _startTestServer() async {
  final server = TestGsiServer();
  return await server.start();
}

Future<bool> _testBackendAuth(String idToken) async {
  try {
    final response = await http.post(
      Uri.parse('${AppConfig.backendBaseUrl}/auth/login'),
      headers: {'Content-Type': 'application/json'},
      body: json.encode({
        'provider': 'google',
        'token': idToken,
        'device_info': {'platform': 'desktop', 'ui': 'test_script'},
      }),
    ).timeout(const Duration(seconds: 20));
    
    print('📡 Backend response status: ${response.statusCode}');
    print('📡 Backend response body: ${response.body}');
    
    if (response.statusCode == 200) {
      final data = json.decode(response.body);
      return data['success'] == true;
    }
    
    return false;
  } catch (e) {
    print('❌ Backend auth error: $e');
    return false;
  }
}
