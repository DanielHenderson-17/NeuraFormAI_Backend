import 'package:flutter/material.dart';
import '../services/auth_service.dart';

class LoginScreen extends StatelessWidget {
  final VoidCallback onSignInSuccess;
  final Function(String) onShowError;

  const LoginScreen({
    super.key,
    required this.onSignInSuccess,
    required this.onShowError,
  });

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.grey.shade100,
      body: Center(
        child: Container(
          constraints: const BoxConstraints(maxWidth: 400),
          padding: const EdgeInsets.all(32),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              // App logo/title
              Icon(
                Icons.psychology,
                size: 80,
                color: Colors.blue.shade600,
              ),
              const SizedBox(height: 24),
              const Text(
                'NeuraFormAI',
                style: TextStyle(
                  fontSize: 32,
                  fontWeight: FontWeight.bold,
                  color: Colors.black87,
                ),
              ),
              const SizedBox(height: 16),
              const Text(
                'Sign in to continue',
                style: TextStyle(
                  fontSize: 16,
                  color: Colors.grey,
                ),
              ),
              const SizedBox(height: 48),
              
              // Google Sign-In Button
              SizedBox(
                width: double.infinity,
                height: 50,
                child: ElevatedButton.icon(
                  onPressed: () async {
                    try {
                      final success = await AuthService.signInWithGoogle();
                      if (success) {
                        onSignInSuccess();
                      } else {
                        onShowError('Sign-in failed. Please try again.');
                      }
                    } catch (e) {
                      onShowError('Sign-in error: $e');
                    }
                  },
                  icon: const Icon(Icons.login, color: Colors.white),
                  label: const Text(
                    'Sign in with Google',
                    style: TextStyle(
                      fontSize: 16,
                      fontWeight: FontWeight.w500,
                      color: Colors.white,
                    ),
                  ),
                  style: ElevatedButton.styleFrom(
                    backgroundColor: Colors.blue.shade600,
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(8),
                    ),
                  ),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
