# Google Authentication Setup Guide

This guide will help you set up Google authentication for your Flutter NeuraFormAI app.

## Prerequisites

1. **Google Cloud Console Project** with OAuth 2.0 credentials
2. **Backend server** running on `http://127.0.0.1:8000`
3. **Flutter development environment** set up

## Step 1: Google Cloud Console Setup

### 1.1 Create OAuth 2.0 Client ID

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Select your project or create a new one
3. Navigate to **APIs & Services** > **Credentials**
4. Click **+ CREATE CREDENTIALS** > **OAuth 2.0 Client IDs**
5. Choose **Desktop application** as the application type
6. Give it a name (e.g., "NeuraFormAI Desktop Client")
7. Click **Create**

### 1.2 Configure Authorized JavaScript Origins

In your OAuth 2.0 client settings, add these **Authorized JavaScript origins**:

```
http://127.0.0.1:8787
http://127.0.0.1:8788
http://127.0.0.1:8789
http://127.0.0.1:8790
http://127.0.0.1:8791
http://localhost:8787
http://localhost:8788
http://localhost:8789
http://localhost:8790
http://localhost:8791
```

### 1.3 Copy Credentials

Copy the **Client ID** and **Client Secret** to your `lib/config/app_config.dart` file:

```dart
static const String googleClientId = 'YOUR_CLIENT_ID_HERE';
static const String googleClientSecret = 'YOUR_CLIENT_SECRET_HERE';
```

## Step 2: Backend Configuration

Ensure your backend server is running and has the Google authentication endpoints:

- `POST /auth/login` - Handles Google ID token authentication
- `POST /auth/register` - Handles user registration
- `GET /auth/profile` - Validates session tokens

## Step 3: Testing the Setup

### 3.1 Test with Standalone Script

Run the test script to verify Google authentication works:

```bash
cd flutter_frontend
dart test_google_auth.dart
```

This will:

1. Start a local server on an available port
2. Open a browser window for Google Sign-In
3. Test the authentication flow
4. Verify backend communication

### 3.2 Test in Flutter App

1. Run your Flutter app: `flutter run`
2. The app will show a sign-in prompt
3. Click "Sign In with Google"
4. Complete the Google authentication flow

## Troubleshooting

### Common Issues

#### 1. "Can't continue with google.com" Error

**Cause**: Google OAuth configuration issue or port conflicts

**Solutions**:

- Verify your Google Client ID is correct
- Check that authorized origins include the local server ports
- Ensure no other services are using ports 8787-8791
- Try manually opening the authentication URL in your browser

#### 2. Browser Won't Open Automatically

**Cause**: URL launcher permissions or system configuration

**Solutions**:

- The app will show the URL to manually open
- Copy and paste the URL into your browser
- Check Windows firewall settings
- Ensure you have a default browser set

#### 3. "No token received" Error

**Cause**: Local server communication issue

**Solutions**:

- Check console logs for detailed error messages
- Verify the local server started successfully
- Ensure the Google Sign-In page loads correctly
- Check browser console for JavaScript errors

#### 4. Backend Authentication Fails

**Cause**: Backend server or configuration issue

**Solutions**:

- Verify backend server is running on port 8000
- Check backend logs for authentication errors
- Ensure Google OAuth is properly configured on backend
- Verify the ID token format and validation

### Debug Steps

1. **Check Console Logs**: Look for detailed error messages in the Flutter console
2. **Browser Developer Tools**: Open browser console to see JavaScript errors
3. **Network Tab**: Check if requests are being made successfully
4. **Port Availability**: Ensure no other services are using the required ports

### Manual Testing

If automatic testing fails:

1. **Start the test server manually**:

   ```bash
   dart test_google_auth.dart
   ```

2. **Open the URL manually** in your browser:

   ```
   http://127.0.0.1:PORT_NUMBER
   ```

3. **Complete Google Sign-In** and check console output

4. **Verify token reception** in the test script

## Configuration Files

### app_config.dart

```dart
class AppConfig {
  static const String backendBaseUrl = 'http://127.0.0.1:8000';
  static const String googleClientId = 'YOUR_CLIENT_ID';
  static const String googleClientSecret = 'YOUR_CLIENT_SECRET';
  static const String localGsiHost = '127.0.0.1';
  static const int localGsiPort = 8787;
}
```

### pubspec.yaml Dependencies

```yaml
dependencies:
  http: ^1.2.2
  url_launcher: ^6.2.5
  shared_preferences: ^2.2.2
```

## Security Notes

- **Never commit** your Google Client Secret to version control
- Use environment variables for production deployments
- The local server is only for development/testing
- Production apps should use proper OAuth flows

## Next Steps

Once authentication is working:

1. **Implement user profile management**
2. **Add session persistence**
3. **Handle user registration flow**
4. **Add logout functionality**
5. **Implement token refresh logic**

## Support

If you continue to have issues:

1. Check the console logs for specific error messages
2. Verify all configuration steps were completed
3. Test with the standalone script first
4. Ensure your backend server is properly configured
5. Check Google Cloud Console for any OAuth errors
