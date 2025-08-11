import 'package:flutter/material.dart';
import '../services/auth_service.dart';
import '../widgets/neurapals_dialog.dart';
import '../models/persona.dart';

class UserMenuWidget extends StatefulWidget {
  final Function(Persona)? onPersonaChanged;
  
  const UserMenuWidget({
    Key? key,
    this.onPersonaChanged,
  }) : super(key: key);

  @override
  State<UserMenuWidget> createState() => _UserMenuWidgetState();
}

class _UserMenuWidgetState extends State<UserMenuWidget> {
  bool _isSignedIn = false;
  String? _userName;
  String? _userEmail;
  String? _userPicture;
  
  @override
  void initState() {
    super.initState();
    _checkAuthStatus();
  }
  
  Future<void> _checkAuthStatus() async {
    final isSignedIn = await AuthService.isSignedIn();
    if (isSignedIn) {
      setState(() {
        _isSignedIn = true;
        _userName = AuthService.userName;
        _userEmail = AuthService.userEmail;
        _userPicture = AuthService.userPicture;
      });
    }
  }
  
  Future<void> _signIn() async {
    final success = await AuthService.signInWithGoogle();
    if (success) {
      await _checkAuthStatus();
    } else {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text('Sign in failed. Please try again.'),
            backgroundColor: Colors.red,
          ),
        );
      }
    }
  }
  
  Future<void> _signOut() async {
    await AuthService.signOut();
    setState(() {
      _isSignedIn = false;
      _userName = null;
      _userEmail = null;
      _userPicture = null;
    });
  }
  
  void _showNeuraPalsDialog() {
    showDialog(
      context: context,
      builder: (context) => NeuraPalsDialog(
        onPersonaSelected: (persona) {
          widget.onPersonaChanged?.call(persona);
        },
      ),
    );
  }
  
  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(12),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.1),
            blurRadius: 10,
            offset: const Offset(0, 5),
          ),
        ],
      ),
      child: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          if (_isSignedIn) ...[
            // User info
            Row(
              children: [
                // Profile picture
                Container(
                  width: 50,
                  height: 50,
                  decoration: BoxDecoration(
                    shape: BoxShape.circle,
                    image: _userPicture != null
                        ? DecorationImage(
                            image: NetworkImage(_userPicture!),
                            fit: BoxFit.cover,
                          )
                        : null,
                  ),
                  child: _userPicture == null
                      ? Icon(
                          Icons.person,
                          size: 30,
                          color: Colors.grey.shade400,
                        )
                      : null,
                ),
                
                const SizedBox(width: 12),
                
                // User details
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        _userName ?? 'User',
                        style: const TextStyle(
                          fontSize: 16,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                      Text(
                        _userEmail ?? '',
                        style: TextStyle(
                          fontSize: 14,
                          color: Colors.grey.shade600,
                        ),
                      ),
                    ],
                  ),
                ),
                
                // Sign out button
                IconButton(
                  onPressed: _signOut,
                  icon: const Icon(Icons.logout),
                  tooltip: 'Sign Out',
                ),
              ],
            ),
            
            const SizedBox(height: 16),
            
            // Menu options
            _buildMenuOption(
              icon: Icons.psychology,
              title: 'Change NeuraPal',
              subtitle: 'Select a different AI personality',
              onTap: _showNeuraPalsDialog,
            ),
            
            _buildMenuOption(
              icon: Icons.settings,
              title: 'Settings',
              subtitle: 'Configure your preferences',
              onTap: () {
                // TODO: Implement settings
                ScaffoldMessenger.of(context).showSnackBar(
                  const SnackBar(content: Text('Settings coming soon!')),
                );
              },
            ),
            
            _buildMenuOption(
              icon: Icons.help_outline,
              title: 'Help & Support',
              subtitle: 'Get help and contact support',
              onTap: () {
                // TODO: Implement help
                ScaffoldMessenger.of(context).showSnackBar(
                  const SnackBar(content: Text('Help coming soon!')),
                );
              },
            ),
            
            _buildMenuOption(
              icon: Icons.info_outline,
              title: 'About',
              subtitle: 'Learn more about NeuraFormAI',
              onTap: () {
                // TODO: Implement about
                ScaffoldMessenger.of(context).showSnackBar(
                  const SnackBar(content: Text('About coming soon!')),
                );
              },
            ),
          ] else ...[
            // Sign in prompt
            Column(
              children: [
                Icon(
                  Icons.account_circle,
                  size: 64,
                  color: Colors.grey.shade400,
                ),
                const SizedBox(height: 16),
                const Text(
                  'Sign in to continue',
                  style: TextStyle(
                    fontSize: 18,
                    fontWeight: FontWeight.w500,
                  ),
                ),
                const SizedBox(height: 8),
                Text(
                  'Sign in with Google to access all features',
                  style: TextStyle(
                    fontSize: 14,
                    color: Colors.grey.shade600,
                  ),
                  textAlign: TextAlign.center,
                ),
                const SizedBox(height: 24),
                ElevatedButton.icon(
                  onPressed: _signIn,
                  icon: Image.asset(
                    'assets/legacy/google.svg',
                    height: 20,
                    errorBuilder: (context, error, stackTrace) {
                      return const Icon(Icons.login, size: 20);
                    },
                  ),
                  label: const Text('Sign in with Google'),
                  style: ElevatedButton.styleFrom(
                    backgroundColor: Colors.white,
                    foregroundColor: Colors.black87,
                    elevation: 2,
                    padding: const EdgeInsets.symmetric(
                      horizontal: 24,
                      vertical: 12,
                    ),
                  ),
                ),
              ],
            ),
          ],
        ],
      ),
    );
  }
  
  Widget _buildMenuOption({
    required IconData icon,
    required String title,
    required String subtitle,
    required VoidCallback onTap,
  }) {
    return ListTile(
      leading: Icon(
        icon,
        color: Colors.blue.shade600,
      ),
      title: Text(
        title,
        style: const TextStyle(
          fontSize: 16,
          fontWeight: FontWeight.w500,
        ),
      ),
      subtitle: Text(
        subtitle,
        style: TextStyle(
          fontSize: 14,
          color: Colors.grey.shade600,
        ),
      ),
      trailing: const Icon(
        Icons.chevron_right,
        color: Colors.grey,
      ),
      onTap: onTap,
      contentPadding: EdgeInsets.zero,
    );
  }
}
