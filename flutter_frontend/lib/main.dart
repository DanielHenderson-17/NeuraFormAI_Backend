import 'package:flutter/material.dart';
import 'package:url_launcher/url_launcher.dart';
import 'package:webview_flutter/webview_flutter.dart';
import 'widgets/chat_window.dart';
import 'widgets/vrm_container.dart';
import 'widgets/user_menu_widget.dart';
import 'widgets/voice_toggle_switch.dart';
import 'widgets/chat_input_widget.dart';
import 'widgets/persona_selection_dialog.dart';
import 'widgets/login_screen.dart';
import 'models/persona.dart';
import 'models/chat_message.dart';
import 'services/auth_service.dart';
import 'services/persona_service.dart';
import 'services/voice_player.dart';
import 'services/conversation_manager.dart';
import 'services/chat_manager.dart';

void main() {
  runApp(const MyApp());
}

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'NeuraPal AI',
      theme: ThemeData(
        colorScheme: ColorScheme.fromSeed(seedColor: Colors.deepPurple),
        useMaterial3: true,
      ),
      home: const MyHomePage(),
    );
  }
}

class MyHomePage extends StatefulWidget {
  const MyHomePage({super.key});

  @override
  State<MyHomePage> createState() => _MyHomePageState();
}

class _MyHomePageState extends State<MyHomePage> {
  Persona? _currentPersona;
  bool _isUserMenuOpen = false;
  bool _isNeuraPalsOpen = false;
  bool _isChatWindowVisible = true;
  List<Map<String, dynamic>> _availablePersonas = [];
  
  // Conversation list state
  List<Map<String, dynamic>> _conversations = [];
  String? _activeConversationId;
  bool _isLoadingConversations = false;
  
  // Shared messaging state
  final List<ChatMessage> _messages = [];
  final TextEditingController _centerInputController = TextEditingController();
  final FocusNode _centerInputFocusNode = FocusNode();
  final GlobalKey<State<ChatWindow>> _chatWindowKey = GlobalKey<State<ChatWindow>>();
  final GlobalKey<State<VRMContainer>> _vrmContainerKey = GlobalKey<State<VRMContainer>>();
  bool _isLoading = false;
  bool _isVoiceEnabled = false;
  
  // Method to force scroll to bottom
  void _scrollChatToBottom() {
    // Give a small delay to ensure the UI is updated
    Future.delayed(const Duration(milliseconds: 50), () {
      final chatState = _chatWindowKey.currentState;
      if (chatState != null) {
        (chatState as dynamic).scrollToBottom?.call();
      }
    });
  }
  
  // Auth state
  bool _isSignedIn = false;
  bool _isCheckingAuth = true;
  
  @override
  void initState() {
    super.initState();
      _loadInitialPersona();
  }
  
  Future<void> _loadInitialPersona() async {
    try {
      // Check if user is signed in
      bool isSignedIn = await AuthService.isSignedIn();
      
      setState(() {
        _isSignedIn = isSignedIn;
        _isCheckingAuth = false;
      });
      
      if (isSignedIn) {
        // Set the user ID in PersonaService
        final userId = AuthService.userId;
        if (userId != null) {
          PersonaService.setUserId(userId);
        }
        
        // Load conversations list
        await _loadConversations();
        
        // Load the active persona
        final activePersonaData = await PersonaService.getActivePersona();
        if (activePersonaData.isNotEmpty) {
          final persona = Persona.fromJson(activePersonaData);
          setState(() {
            _currentPersona = persona;
          });
          
          // Get conversation ID for the active persona
          if (userId != null) {
            final conversationId = await PersonaService.getConversationForPersona(userId, persona.name);
            setState(() {
              _activeConversationId = conversationId;
            });
              
            // Load conversation history if conversation exists
            if (conversationId != null) {
              await _loadConversationHistory();
            }
          }
        }
      }
    } catch (e) {
      print("❌ [MyHomePage] Error loading initial persona: $e");
      setState(() {
        _isCheckingAuth = false;
      });
    }
  }
  
  void _onPersonaChanged(Persona persona) {
    setState(() {
      _currentPersona = persona;
    });
  }
  
  void _toggleUserMenu() {
    setState(() {
      _isUserMenuOpen = !_isUserMenuOpen;
    });
  }
  
  Future<void> _openNeuraPals() async {
    try {
      final personas = await PersonaService.getAllPersonas();
      setState(() {
        _availablePersonas = personas;
        _isNeuraPalsOpen = true;
      });
    } catch (e) {
      print("❌ [Main] Error opening NeuraPals: $e");
    }
  }
  
  void _closeNeuraPals() {
    setState(() {
      _isNeuraPalsOpen = false;
    });
  }
  
  Future<void> _loadConversationHistory() async {
    try {
      final historyMessages = await ConversationManager.getConversationHistoryMessages(_currentPersona?.name);
      
      setState(() {
        _messages.clear();
        _messages.addAll(historyMessages);
      });
      _scrollChatToBottom(); // Auto-scroll to show latest messages
      
      print("📚 [Main] Loaded ${historyMessages.length} messages from conversation history");
      
    } catch (e) {
      print("❌ [Main] Error loading conversation history: $e");
    }
  }
  
  // === Conversation Management Methods ===
  
  Future<void> _loadConversations() async {
    if (_isLoadingConversations) return;
    
    setState(() {
      _isLoadingConversations = true;
    });
    
    try {
      final response = await ConversationManager.getConversationsList();
      
      setState(() {
        _conversations = response;
        _isLoadingConversations = false;
      });
      
      print("📂 [Main] Loaded ${_conversations.length} conversations");
      
    } catch (e) {
      print("❌ [Main] Error loading conversations: $e");
      setState(() {
        _isLoadingConversations = false;
      });
    }
  }
  
  Future<void> _renameConversation(String conversationId, String newTitle) async {
    try {
      final success = await ConversationManager.renameConversation(conversationId, newTitle);
      
      if (success) {
        // Update local conversation list
        setState(() {
          final index = _conversations.indexWhere((conv) => conv['id'] == conversationId);
          if (index != -1) {
            _conversations[index]['title'] = newTitle;
          }
        });
        print("✏️ [Main] Conversation renamed to: $newTitle");
      }
      
    } catch (e) {
      print("❌ [Main] Error renaming conversation: $e");
    }
  }
  
  Future<void> _deleteConversation(String conversationId) async {
    try {
      final success = await ConversationManager.deleteConversation(conversationId);
      
      if (success) {
        // Remove from local conversation list
        setState(() {
          _conversations.removeWhere((conv) => conv['id'] == conversationId);
          
          // If this was the active conversation, clear messages
          if (_activeConversationId == conversationId) {
            _activeConversationId = null;
            _messages.clear();
          }
        });
        print("🗑️ [Main] Conversation deleted");
      }
      
    } catch (e) {
      print("❌ [Main] Error deleting conversation: $e");
    }
  }
  
  Future<void> _selectPersona(String personaName) async {
    try {
      await PersonaService.selectPersona(personaName);
      
      // Load the new persona data
      final activePersonaData = await PersonaService.getActivePersona();
      if (activePersonaData.isNotEmpty) {
        final persona = Persona.fromJson(activePersonaData);
        setState(() {
          _currentPersona = persona;
        });
      }
      
      _closeNeuraPals();
      
      // Get conversation ID for this persona (if it exists)
      final userId = AuthService.userId;
      if (userId != null) {
        final conversationId = await PersonaService.getConversationForPersona(userId, personaName);
        
        setState(() {
          _activeConversationId = conversationId;
          _messages.clear(); // Clear current messages
        });
        
        if (conversationId != null) {
          // Load conversation history for existing conversation
          await _loadConversationHistory();
          print("🔄 [Main] Switched to existing conversation for $personaName");
              } else {
          // No conversation exists yet - will be created on first message
          print("🆕 [Main] No conversation exists for $personaName yet");
        }
        
        // Reload conversations list to reflect any changes
        await _loadConversations();
      }
      
    } catch (e) {
      print("❌ [Main] Error selecting persona: $e");
    }
  }
  
  // Get user display name from AuthService
  String _getUserDisplayName() {
    final firstName = AuthService.userFirstName ?? '';
    final lastName = AuthService.userLastName ?? '';
    final fullName = (firstName + (lastName.isNotEmpty ? ' $lastName' : '')).trim();
    return fullName.isNotEmpty ? fullName : 'User';
  }

  // Get user first initial for avatar
  String _getUserInitial() {
    final firstName = AuthService.userFirstName ?? '';
    return (firstName.isNotEmpty ? firstName[0] : 'U').toUpperCase();
  }

  // Build menu button matching Python styling
  Widget _buildMenuButton(String text, VoidCallback onPressed) {
    return Expanded(
      child: MouseRegion(
        cursor: SystemMouseCursors.click,
        child: GestureDetector(
          onTap: () {
            // Call the action and prevent event bubbling
            onPressed();
          },
          child: Container(
            padding: const EdgeInsets.all(8),
            alignment: Alignment.centerLeft,
                  decoration: BoxDecoration(
              color: Colors.transparent,
            ),
            child: Text(
              text,
              style: const TextStyle(
                    color: Colors.white,
                fontSize: 14,
              ),
            ),
                          ),
                        ),
      ),
    );
  }
  
  // Messaging functionality using ChatManager
  Future<void> _sendMessage() async {
    final message = _centerInputController.text.trim();
    if (message.isEmpty || _isLoading) return;
    
    // Clear input and maintain focus
    _centerInputController.clear();
    _centerInputFocusNode.requestFocus();
    
    setState(() => _isLoading = true);
    
    try {
      // Check for persona switching commands first
      final switchMatch = RegExp(r'^(?:switch|swap)\s+to\s+(.+)$', caseSensitive: false).firstMatch(message);
      if (switchMatch != null) {
        final personaName = switchMatch.group(1)?.trim();
        if (personaName != null && personaName.isNotEmpty) {
          print("🔄 [Main] Typed command detected — switching to persona: $personaName");
          
          // Handle persona switching (this involves complex state management)
          final hadExistingConversation = _activeConversationId != null;
          await _selectPersona(personaName);
          
          // Use ChatManager for welcome/intro messages after persona switch
          final result = await ChatManager.handlePersonaSwitch(
            personaName: personaName,
            currentPersona: _currentPersona,
            voiceEnabled: _isVoiceEnabled,
            activeConversationId: _activeConversationId,
            currentMessages: _messages,
            onVrmLipSync: (response, audioDuration, {double? durationPerWord}) {
              final vrmState = _vrmContainerKey.currentState as dynamic;
              if (audioDuration != null) {
                vrmState?.startVoiceLipSync(response, audioDuration: audioDuration);
              } else if (durationPerWord != null) {
                vrmState?.startTextLipSync(response, durationPerWord: durationPerWord);
              }
            },
          );
          
          if (result.newMessages.isNotEmpty) {
            setState(() => _messages.addAll(result.newMessages));
            _scrollChatToBottom();
          }
        }
      } else {
        // Regular message - use ChatManager
        final result = await ChatManager.processMessage(
          message: message,
          currentPersona: _currentPersona,
          voiceEnabled: _isVoiceEnabled,
          activeConversationId: _activeConversationId,
          onVrmLipSync: (response, audioDuration, {double? durationPerWord}) {
            final vrmState = _vrmContainerKey.currentState as dynamic;
            if (audioDuration != null) {
              vrmState?.startVoiceLipSync(response, audioDuration: audioDuration);
            } else if (durationPerWord != null) {
              vrmState?.startTextLipSync(response, durationPerWord: durationPerWord);
            }
          },
        );
        
        // Update UI state based on result
        if (result.newMessages.isNotEmpty) {
          setState(() => _messages.addAll(result.newMessages));
          _scrollChatToBottom();
        }
        
        if (result.conversationId != null) {
          setState(() => _activeConversationId = result.conversationId);
        }
        
        if (result.shouldReloadConversations) {
          await _loadConversations();
        }
      }
    } finally {
      setState(() => _isLoading = false);
    }
  }

  // Build chat input for center column (extracted from ChatWindow)
  Widget _buildChatInput() {
    return ChatInputWidget(
      controller: _centerInputController,
      focusNode: _centerInputFocusNode,
      isLoading: _isLoading,
      isVoiceEnabled: _isVoiceEnabled,
      isChatWindowVisible: _isChatWindowVisible,
      onSendMessage: _sendMessage,
      onVoiceToggle: (bool value) {
        setState(() {
          _isVoiceEnabled = value;
        });
        print("🎤 Voice toggle: ${value ? 'enabled' : 'disabled'}");
      },
      onChatToggle: () {
        setState(() {
          _isChatWindowVisible = !_isChatWindowVisible;
        });
        print("🔄 Chat toggle pressed - ${_isChatWindowVisible ? 'shown' : 'hidden'}");
      },
      onMicrophonePressed: () {
        print("🎤 Microphone pressed");
      },
    );
  }

  // Build conversation list for left column
  Widget _buildConversationList() {
    return ConversationManager.buildConversationList(
      conversations: _conversations,
      activeConversationId: _activeConversationId,
      isLoadingConversations: _isLoadingConversations,
      onConversationSelected: (personaName) async {
        await _selectPersona(personaName);
      },
      onRename: _renameConversation,
      onDelete: _deleteConversation,
      context: context,
    );
  }  @override

  Widget build(BuildContext context) {
    // Show loading while checking auth status
    if (_isCheckingAuth) {
      return const Scaffold(
        body: Center(
          child: CircularProgressIndicator(),
        ),
      );
    }
    
    // If not signed in, show ONLY login screen
    if (!_isSignedIn) {
      return LoginScreen(
        onSignInSuccess: () async {
          setState(() {
            _isSignedIn = true;
          });
          await _loadInitialPersona();
        },
        onShowError: _showErrorDialog,
      );
    }
    
    // If signed in, show main app
    return GestureDetector(
          // Global click detection (like Python's eventFilter)
          onTap: () {
            if (_isUserMenuOpen) {
              _toggleUserMenu();
            }
            if (_isNeuraPalsOpen) {
              _closeNeuraPals();
            }
          },
          child: Scaffold(
            backgroundColor: Colors.grey.shade100,
            body: Stack(
              children: [
                // Main app layout
                Row(
        children: [
          // Left column (1/4) - Exact copy of Python chat_ui/left structure
          Expanded(
            flex: 1,
            child: Container(
              padding: const EdgeInsets.fromLTRB(0, 0, 100, 0), // Right padding like Python
              child: Column(
                children: [
                  // Conversation list container (smaller when menu open, dark background)
                  Expanded(
                    flex: _isUserMenuOpen ? 2 : 4, // Shrinks when menu opens
                    child: Container(
                      margin: const EdgeInsets.all(10),
                      decoration: const BoxDecoration(
                        color: Color(0xFF2c2c2c), // Exact Python color
                      ),
                      child: _buildConversationList(),
                    ),
                  ),
                  
                  // User container (stretch=1, dark background)
                  Expanded(
                    flex: 1,
                    child: Container(
                      margin: const EdgeInsets.all(10),
                      decoration: const BoxDecoration(
                        color: Color(0xFF2c2c2c), // Exact Python color
                      ),
                      child: Stack(
                        children: [
                          // Main user container content
                          Column(
                            children: [
                              const Spacer(),
                              
                              // Avatar + User name at bottom (always visible)
                              MouseRegion(
                                cursor: SystemMouseCursors.click,
                                child: GestureDetector(
                                  onTap: () {
                                    _toggleUserMenu();
                                  },
                                child: Container(
                                  padding: const EdgeInsets.all(10),
                                  child: Row(
                                    children: [
                                      // Avatar
                                      Container(
                                        width: 30,
                                        height: 30,
                                        decoration: BoxDecoration(
                                          color: Colors.blue,
                                          borderRadius: BorderRadius.circular(15),
                                        ),
                                        child: Center(
                                          child: Text(
                                            _getUserInitial(),
                          style: const TextStyle(
                                              color: Colors.white,
                                              fontSize: 12,
                            fontWeight: FontWeight.bold,
                          ),
                        ),
                                        ),
                                      ),
                                      const SizedBox(width: 8),
                                      // User name
                        Text(
                                        _getUserDisplayName(),
                                        style: const TextStyle(
                                          color: Colors.white,
                                          fontSize: 11,
                                        ),
                                      ),
                                    ],
                                  ),
                                ),
                    ),
                  ),
              ],
                          ),
                          
                          // Menu positioned above avatar (expands upward)
                          if (_isUserMenuOpen)
                            Positioned(
                              bottom: 70, // Above the avatar
                              left: 10,
                              right: 10,
                              child: AnimatedContainer(
                                duration: const Duration(milliseconds: 300),
                                curve: Curves.easeOutCubic,
                                height: 120,
                                decoration: BoxDecoration(
                                  color: const Color(0xFF3a3a3a),
                                  borderRadius: BorderRadius.circular(10),
                                  border: Border.all(color: const Color(0xFF555555)),
                                ),
                                child: Column(
                                  children: [
                                    _buildMenuButton('Settings', () {
                                      print('Settings clicked');
                                      _toggleUserMenu();
                                    }),
                                    _buildMenuButton('NeuraPals', () async {
                                      print('NeuraPals clicked');
                                      _toggleUserMenu();
                                      await _openNeuraPals();
                                    }),
                                                                            _buildMenuButton('Logout', () async {
                                          print('Logout clicked');
                                          _toggleUserMenu();
                                          await AuthService.signOut();
                                          // Update auth state to show login screen
                                          setState(() {
                                            _isSignedIn = false;
                                            _currentPersona = null;
                                            _messages.clear();
                                          });
                                        }),
                                  ],
                                ),
                              ),
                            ),
                        ],
                      ),
                    ),
                  ),
              ],
              ),
            ),
          ),
          
          // Center column (1/2) - VRM viewer + Chat input
          Expanded(
            flex: 2,
            child: Container(
              padding: const EdgeInsets.fromLTRB(20, 16, 20, 0),
              child: Column(
                children: [
                  // VRM container (stretch=3 like Python)
                  Expanded(
                    flex: 3,
                    child: VRMContainer(
                      key: _vrmContainerKey,
                      vrmModel: _currentPersona?.name != null ? '${_currentPersona!.name.toLowerCase()}_model.vrm' : null,
                    ),
                  ),
                  
                  // Chat input (stretch=1 like Python) - moved from ChatWindow
                  Expanded(
                    flex: 1,
                    child: _buildChatInput(),
                  ),
                ],
              ),
            ),
          ),
          
          // Right column (1/4) - Chat bubbles only
          Expanded(
            flex: 1,
            child: Container(
              padding: const EdgeInsets.all(16),
              decoration: const BoxDecoration(
                color: Color(0xFF1e1e1e),
              ),
              child: _isChatWindowVisible 
                ? ChatWindow(
                    key: _chatWindowKey,
                    messages: _messages,
                  )
                : Container(), // Empty container when chat is hidden
            ),
          ),
        ],
        ),
        
        // NeuraPals window overlay (non-modal)
        if (_isNeuraPalsOpen) PersonaSelectionDialog(
          availablePersonas: _availablePersonas,
          currentPersona: _currentPersona,
          onPersonaSelected: _selectPersona,
          onClose: _closeNeuraPals,
        ),
      ],
    ),
      ),
    );
  }
  
  // Show error dialog
  void _showErrorDialog(String message) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Error'),
        content: Text(message),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(context).pop(),
            child: const Text('OK'),
          ),
        ],
      ),
    );
  }

  @override
  void dispose() {
    _centerInputController.dispose();
    _centerInputFocusNode.dispose();
    super.dispose();
  }
}