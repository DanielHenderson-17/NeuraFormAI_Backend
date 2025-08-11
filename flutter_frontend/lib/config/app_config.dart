class AppConfig {
  // Backend configuration
  static const String backendBaseUrl = 'http://127.0.0.1:8000';
  
  // Google OAuth configuration
  // Make sure these match your Google Cloud Console OAuth 2.0 client credentials
  static const String googleClientId = '707698270630-julh23dsa6nl1jeph38lelp7bihra0qv.apps.googleusercontent.com';
  static const String googleClientSecret = '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';
  
  // Local GSI server configuration
  static const String localGsiHost = '127.0.0.1';
  static const int localGsiPort = 8787; // Use the same port as Python implementation
  
  // Validate configuration
  static bool get isValid {
    return googleClientId.isNotEmpty && 
           googleClientId != 'YOUR_GOOGLE_CLIENT_ID' &&
           backendBaseUrl.isNotEmpty;
  }
  
  // Get authorized origins for Google OAuth
  static List<String> get authorizedOrigins => [
    'http://127.0.0.1:8787',
    'http://127.0.0.1:8788',
    'http://127.0.0.1:8789',
    'http://127.0.0.1:8790',
    'http://127.0.0.1:8791',
    'http://localhost:8787',
    'http://localhost:8788',
    'http://localhost:8789',
    'http://localhost:8790',
    'http://localhost:8791',
  ];
}
