import 'package:flutter/material.dart';
import 'package:webview_flutter/webview_flutter.dart';
import '../models/chat_message.dart';
import '../models/persona.dart';
import '../services/persona_service.dart';
import '../services/voice_player.dart';
import '../services/auth_service.dart';
import 'chat_bubble.dart';
import 'vrm_container.dart';

class ChatWindow extends StatefulWidget {
  final List<ChatMessage> messages;

  const ChatWindow({
    Key? key,
    required this.messages,
  }) : super(key: key);

  @override
  State<ChatWindow> createState() => _ChatWindowState();
}

class _ChatWindowState extends State<ChatWindow> {
  final ScrollController _scrollController = ScrollController();
  
  Persona? _activePersona;
  bool _isVoiceEnabled = true;
  String? _currentVrmModel;
  
  @override
  void initState() {
    super.initState();
    _initializeChat();
    _setupPersonaCallbacks();
  }
  
  void _setupPersonaCallbacks() {
    PersonaService.setPersonaChangedCallback((personaId) {
      _loadPersona(personaId);
    });
    
    PersonaService.setVrmModelChangedCallback((vrmModel) {
      setState(() {
        _currentVrmModel = vrmModel;
      });
    });
  }
  
  Future<void> _initializeChat() async {
    // Check if user is signed in
    final isSignedIn = await AuthService.isSignedIn();
    if (!isSignedIn) {
      _showLoginDialog();
      return;
    }
    
    // Set user ID in persona service
    PersonaService.setUserId(AuthService.userId!);
    
    // Load default persona
    await _loadPersona('default');
    
    // No initial greeting message - start with clean chat
  }
  
  Future<void> _loadPersona(String personaId) async {
    try {
      final personaData = await PersonaService.getActivePersona();
      final persona = Persona.fromJson(personaData);
      if (persona != null) {
        setState(() {
          _activePersona = persona;
          _currentVrmModel = persona.vrmModel;
        });
        
        // Update VRM model in container
        if (mounted) {
          // This will be handled by the VRM container
        }
      }
    } catch (e) {
      print("❌ Error loading persona: $e");
      _showErrorSnackBar("Failed to load persona: $e");
    }
  }
  
  void scrollToBottom() {
    // Use a small delay to ensure the new message is fully rendered
    Future.delayed(const Duration(milliseconds: 100), () {
      if (_scrollController.hasClients) {
        _scrollController.animateTo(
          _scrollController.position.maxScrollExtent,
          duration: const Duration(milliseconds: 300),
          curve: Curves.easeOut,
        );
      }
    });
  }
  
  // Keep the old private method for backwards compatibility
  void _scrollToBottom() => scrollToBottom();

  @override
  void didUpdateWidget(ChatWindow oldWidget) {
    super.didUpdateWidget(oldWidget);
    // Scroll to bottom when new messages are added
    if (widget.messages.length != oldWidget.messages.length) {
      _scrollToBottom();
    }
  }

  void _updatePersonaVisuals(Persona persona) {
    // Update VRM model if available
    setState(() {
      _activePersona = persona;
      _currentVrmModel = persona.vrmModel;
    });
    print("🎭 Updated persona visuals for: ${persona.name}");
  }
  
  void _handleVrmResponse(Map<String, dynamic> response) {
    // Extract emotion and gesture data
    final emotion = response['emotion'];
    final gesture = response['gesture'];
    
    if (emotion != null) {
      // Update VRM expression
      // This will be handled by the VRM container
      print("😊 Setting VRM expression: $emotion");
    }
    
    if (gesture != null) {
      // Update VRM gesture
      // This will be handled by the VRM container
      print("👋 Setting VRM gesture: $gesture");
    }
  }
  
  void _toggleVoice() {
    setState(() {
      _isVoiceEnabled = !_isVoiceEnabled;
    });
    
    if (!_isVoiceEnabled) {
      // TODO: Implement stop functionality when VoicePlayer is fully implemented
      print("🔊 Voice disabled");
    }
  }
  
  void _showLoginDialog() {
    showDialog(
      context: context,
      barrierDismissible: false,
      builder: (context) => AlertDialog(
        title: const Text('Sign In Required'),
        content: const Text('Please sign in with Google to continue.'),
        actions: [
          TextButton(
            onPressed: () async {
              Navigator.of(context).pop();
              final success = await AuthService.signInWithGoogle();
              if (success) {
                _initializeChat();
              }
            },
            child: const Text('Sign In with Google'),
          ),
        ],
      ),
    );
  }
  
  void _showErrorSnackBar(String message) {
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text(message),
        backgroundColor: Colors.red,
      ),
    );
  }
  
  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        // Chat messages area
        Expanded(
          child: widget.messages.isEmpty
              ? const Center(
                  child: Text(
                    'Start a conversation with your NeuraPal!',
                    style: TextStyle(
                      fontSize: 16,
                      color: Colors.grey,
                    ),
                  ),
                )
              : ListView.builder(
                  controller: _scrollController,
                  padding: const EdgeInsets.symmetric(horizontal: 2, vertical: 16),
                  itemCount: widget.messages.length,
                  itemBuilder: (context, index) {
                    final message = widget.messages[index];
                    return ChatBubble(
                      message: message,
                      key: ValueKey(message.id),
                    );
                  },
                ),
        ),
        

      ],
    );
  }
  
  @override
  void dispose() {
    _scrollController.dispose();
    VoicePlayer.dispose();
    super.dispose();
  }
}
