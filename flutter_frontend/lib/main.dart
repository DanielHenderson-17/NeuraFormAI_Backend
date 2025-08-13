import 'package:flutter/material.dart';
import 'package:url_launcher/url_launcher.dart';
import 'package:webview_flutter/webview_flutter.dart';
import 'widgets/chat_window.dart';
import 'widgets/vrm_container.dart';
import 'widgets/user_menu_widget.dart';
import 'widgets/voice_toggle_switch.dart';
import 'models/persona.dart';
import 'models/chat_message.dart';
import 'services/auth_service.dart';
import 'services/persona_service.dart';
import 'services/voice_player.dart';

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
      final historyData = await PersonaService.getConversationHistory();
      final historyMessages = <ChatMessage>[];
      
      for (final msgData in historyData) {
        final message = ChatMessage(
          id: msgData['id'] ?? DateTime.now().millisecondsSinceEpoch.toString(),
          content: msgData['content'] ?? '',
          isUser: msgData['sender_type'] == 'user',
          timestamp: DateTime.tryParse(msgData['created_at'] ?? '') ?? DateTime.now(),
          personaName: _currentPersona?.name ?? 'AI',
        );
        historyMessages.add(message);
      }
      
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
      final userId = AuthService.userId;
      if (userId == null) return;
      
      final response = await PersonaService.getConversations(userId);
      
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
      final success = await PersonaService.updateConversationTitle(conversationId, newTitle);
      
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
      final success = await PersonaService.deleteConversation(conversationId);
      
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
  
  // Messaging functionality extracted from ChatWindow
  Future<void> _sendMessage() async {
    final message = _centerInputController.text.trim();
    if (message.isEmpty || _isLoading) return;
    
    // Clear input and maintain focus
    _centerInputController.clear();
    _centerInputFocusNode.requestFocus();
    
    setState(() => _isLoading = true);
    
    try {
      // Check for persona switching commands (switch to / swap to)
      final switchMatch = RegExp(r'^(?:switch|swap)\s+to\s+(.+)$', caseSensitive: false).firstMatch(message);
      if (switchMatch != null) {
        final personaName = switchMatch.group(1)?.trim();
        if (personaName != null && personaName.isNotEmpty) {
          print("🔄 [Main] Typed command detected — switching to persona: $personaName");
          
          // Don't add the command to chat history - it's a system command
          
          try {
            // Switch to the persona and load their conversation immediately
            final hadExistingConversation = _activeConversationId != null;
            await _selectPersona(personaName);
            
            // Only send welcome/intro messages if this is the first switch and conversation has history
            if (_activeConversationId != null && !hadExistingConversation && _messages.isNotEmpty) {
              // Existing conversation - send welcome back message (hidden from history)
              print("🔄 [Main] Found existing conversation with ${_messages.length} messages - sending welcome back");
              final response = await PersonaService.fetchReply(
                "The user just returned to continue our conversation. Give them a brief, personalized welcome back message that fits your personality.", 
                voiceEnabled: _isVoiceEnabled,
                saveToHistory: false
              );
              
              final aiMessage = ChatMessage(
                id: DateTime.now().millisecondsSinceEpoch.toString(),
                content: response,
                isUser: false,
                timestamp: DateTime.now(),
                personaName: _currentPersona?.name ?? 'AI',
              );
              
              setState(() => _messages.add(aiMessage));
              _scrollChatToBottom(); // Auto-scroll to new message
              
              // Play voice if enabled for welcome back
              if (_isVoiceEnabled) {
                print("🎤 Voice enabled - starting TTS playback for welcome back");
                VoicePlayer.playReplyFromBackend(response, voiceEnabled: true, onStart: (audioDuration) {
                  // Start voice-synchronized lip sync
                  if (audioDuration != null) {
                    final vrmState = _vrmContainerKey.currentState as dynamic;
                    vrmState?.startVoiceLipSync(response, audioDuration: audioDuration);
                  }
                });
              } else {
                // Voice disabled - just do text-based lip sync for welcome back with EXACT Python timing
                final vrmState = _vrmContainerKey.currentState as dynamic;
                vrmState?.startTextLipSync(response, durationPerWord: 0.08); // EXACT Python value
              }
            } else if (_activeConversationId == null && _messages.isEmpty) {
              // New conversation - send introduction (hidden from history)
              print("🔄 [Main] No existing conversation - sending introduction");
              final response = await PersonaService.fetchReply(
                "Introduce yourself briefly as the new persona.", 
                voiceEnabled: _isVoiceEnabled,
                saveToHistory: false
              );
              
              final aiMessage = ChatMessage(
                id: DateTime.now().millisecondsSinceEpoch.toString(),
                content: response,
                isUser: false,
                timestamp: DateTime.now(),
                personaName: _currentPersona?.name ?? 'AI',
              );
              
              setState(() => _messages.add(aiMessage));
              _scrollChatToBottom(); // Auto-scroll to new message
              
              // Play voice if enabled for persona introduction
              if (_isVoiceEnabled) {
                print("🎤 Voice enabled - starting TTS playback for persona introduction");
                VoicePlayer.playReplyFromBackend(response, voiceEnabled: true, onStart: (audioDuration) {
                  // Start voice-synchronized lip sync
                  if (audioDuration != null) {
                    final vrmState = _vrmContainerKey.currentState as dynamic;
                    vrmState?.startVoiceLipSync(response, audioDuration: audioDuration);
                  }
                });
              } else {
                // Voice disabled - just do text-based lip sync for persona introduction with EXACT Python timing
                final vrmState = _vrmContainerKey.currentState as dynamic;
                vrmState?.startTextLipSync(response, durationPerWord: 0.08); // EXACT Python value
              }
            } else {
              print("🔄 [Main] Switched to persona ${personaName} - no welcome message needed (${_messages.length} messages loaded)");
            }
            
          } catch (e) {
            print("❌ [Main] Error during persona switch: $e");
            final errorMessage = ChatMessage(
              id: DateTime.now().millisecondsSinceEpoch.toString(),
              content: "Sorry, I couldn't switch to that persona. Please try again.",
              isUser: false,
              timestamp: DateTime.now(),
            );
            setState(() => _messages.add(errorMessage));
            _scrollChatToBottom(); // Auto-scroll to new message
          }
        }
      } else {
        // Regular message
        final userMessage = ChatMessage(
          id: DateTime.now().millisecondsSinceEpoch.toString(),
          content: message,
          isUser: true,
          timestamp: DateTime.now(),
        );
        
        setState(() => _messages.add(userMessage));
        _scrollChatToBottom(); // Auto-scroll to new message
        
        try {
          final response = await PersonaService.fetchReply(message, voiceEnabled: _isVoiceEnabled);
          
          final aiMessage = ChatMessage(
            id: DateTime.now().millisecondsSinceEpoch.toString(),
            content: response,
            isUser: false,
            timestamp: DateTime.now(),
            personaName: _currentPersona?.name ?? 'AI',
          );
          
          setState(() => _messages.add(aiMessage));
          _scrollChatToBottom(); // Auto-scroll to new message
          
          // Refresh conversation list to show new/updated conversation
          await _loadConversations();
          
          // Update active conversation ID if it wasn't set (new conversation)
          if (_activeConversationId == null && _currentPersona != null) {
            final userId = AuthService.userId;
            if (userId != null) {
              final conversationId = await PersonaService.getConversationForPersona(userId, _currentPersona!.name);
    setState(() {
                _activeConversationId = conversationId;
              });
            }
          }
          
          // Play voice if enabled (matches Python frontend behavior)
          if (_isVoiceEnabled) {
            print("🎤 Voice enabled - starting TTS playback");
            VoicePlayer.playReplyFromBackend(response, voiceEnabled: true, onStart: (audioDuration) {
              // Start voice-synchronized lip sync
              if (audioDuration != null) {
                final vrmState = _vrmContainerKey.currentState as dynamic;
                vrmState?.startVoiceLipSync(response, audioDuration: audioDuration);
              }
            });
          } else {
            // Voice disabled - just do text-based lip sync with EXACT Python timing
            final vrmState = _vrmContainerKey.currentState as dynamic;
            vrmState?.startTextLipSync(response, durationPerWord: 0.08); // EXACT Python value
          }
          
        } catch (e) {
          print("❌ [Main] Error sending message: $e");
          final errorMessage = ChatMessage(
            id: DateTime.now().millisecondsSinceEpoch.toString(),
            content: "Sorry, I couldn't process your message. Please try again.",
            isUser: false,
            timestamp: DateTime.now(),
          );
          setState(() => _messages.add(errorMessage));
          _scrollChatToBottom(); // Auto-scroll to new message
        }
      }
    } finally {
      setState(() => _isLoading = false);
    }
  }

  // Build chat input for center column (extracted from ChatWindow)
  Widget _buildChatInput() {
    return Container(
      padding: const EdgeInsets.fromLTRB(16, 0, 16, 20),
      color: Colors.transparent,
            child: Column(
        mainAxisSize: MainAxisSize.min,
              children: [
          // Voice toggle switch (top right) - matches Python frontend
          Row(
            mainAxisAlignment: MainAxisAlignment.end,
            children: [
                Container(
                margin: const EdgeInsets.only(bottom: 8, right: 6),
                child: VoiceToggleSwitch(
                  initialValue: _isVoiceEnabled,
                  onChanged: (bool value) {
                    setState(() {
                      _isVoiceEnabled = value;
                    });
                    print("🎤 Voice toggle: ${value ? 'enabled' : 'disabled'}");
                  },
                        ),
                      ),
                    ],
          ),
          
          // Chat input bubble
          Expanded(
            child: Container(
              constraints: const BoxConstraints(
                minHeight: 50,
                maxHeight: 140,
              ),
                  decoration: BoxDecoration(
                color: const Color(0xFF333333),
                    borderRadius: BorderRadius.circular(12),
                    ),
                    child: Column(
                      children: [
                  // Text input area
                  Expanded(
                    child: Container(
                      margin: const EdgeInsets.fromLTRB(6, 8, 6, 4),
                      child: TextField(
                        controller: _centerInputController,
                        focusNode: _centerInputFocusNode,
                        style: const TextStyle(
                          color: Colors.white,
                          fontSize: 14,
                        ),
                        decoration: InputDecoration(
                          hintText: _isLoading ? 'AI is typing...' : 'Start typing...',
                          hintStyle: TextStyle(
                            color: Colors.grey.shade400,
                            fontSize: 14,
                          ),
                          border: InputBorder.none,
                          contentPadding: const EdgeInsets.symmetric(horizontal: 6, vertical: 6),
                        ),
                        maxLines: null,
                        textInputAction: TextInputAction.send,
                        onSubmitted: (value) {
                          if (!_isLoading) _sendMessage();
                        },
                      ),
                    ),
                  ),
                  
                  // Bottom button row
                  Container(
                    margin: const EdgeInsets.fromLTRB(6, 0, 6, 6),
                  child: Row(
                    children: [
                        // Left side buttons (future expansion)
                        const Expanded(child: SizedBox()),
                        
                        // Right side buttons
                        Row(
                          mainAxisSize: MainAxisSize.min,
                          children: [
                            // Chat toggle button
                            Container(
                              width: 30,
                              height: 30,
                              margin: const EdgeInsets.only(right: 6),
                              child: Material(
                                color: Colors.transparent,
                                child: InkWell(
                                  borderRadius: BorderRadius.circular(6),
                                  onTap: () {
                                    setState(() {
                                      _isChatWindowVisible = !_isChatWindowVisible;
                                    });
                                    print("🔄 Chat toggle pressed - ${_isChatWindowVisible ? 'shown' : 'hidden'}");
                                  },
                                                                      child: Container(
                                    decoration: BoxDecoration(
                                      color: _isChatWindowVisible ? Colors.grey.withOpacity(0.3) : Colors.transparent,
                                      borderRadius: BorderRadius.circular(6),
                                    ),
                                    child: Icon(
                                      _isChatWindowVisible ? Icons.chat_bubble : Icons.chat_bubble_outline,
                                      color: _isChatWindowVisible ? Colors.blue : Colors.white,
                                      size: 18,
                          ),
                        ),
                      ),
                              ),
                            ),
                            
                            // Microphone button
                            Container(
                              width: 30,
                              height: 30,
                              margin: const EdgeInsets.only(right: 6),
                              child: Material(
                                color: Colors.transparent,
                                child: InkWell(
                                  borderRadius: BorderRadius.circular(6),
                                  onTap: () {
                                    print("🎤 Microphone pressed");
                                  },
                                  child: Container(
                    decoration: BoxDecoration(
                                      color: Colors.transparent,
                                      borderRadius: BorderRadius.circular(6),
                                    ),
                                    child: const Icon(
                                      Icons.mic,
                      color: Colors.white,
                                      size: 18,
                                    ),
                                  ),
                                ),
                              ),
                            ),
                            
                                                          // Send button
                              Container(
                                width: 32,
                                height: 32,
                                child: Material(
                                  color: Colors.transparent,
                                  child: InkWell(
                                    borderRadius: BorderRadius.circular(6),
                                    onTap: _isLoading ? null : _sendMessage,
                                  child: Container(
                                    decoration: BoxDecoration(
                                      color: Colors.transparent,
                                      borderRadius: BorderRadius.circular(6),
                                    ),
                                    child: Icon(
                                      Icons.arrow_upward_rounded,
                                      color: _isLoading ? Colors.grey : Colors.white,
                                      size: 22,
                                    ),
                                  ),
                                ),
                        ),
                      ),
                    ],
                  ),
                      ],
                    ),
                  ),
              ],
              ),
            ),
          ),
        ],
      ),
    );
  }

  // Build conversation list for left column
  Widget _buildConversationList() {
    if (_isLoadingConversations) {
      return const Center(
        child: CircularProgressIndicator(
          color: Colors.grey,
          strokeWidth: 2,
        ),
      );
    }
    
    if (_conversations.isEmpty) {
      return const Center(
        child: Text(
          'No conversations yet',
          style: TextStyle(
            color: Colors.grey,
            fontSize: 14,
          ),
        ),
      );
    }
    
    return ListView.builder(
      padding: const EdgeInsets.all(8),
      itemCount: _conversations.length,
      itemBuilder: (context, index) {
        final conversation = _conversations[index];
        final isActive = conversation['id'] == _activeConversationId;
        
        return Container(
          margin: const EdgeInsets.only(bottom: 4),
                    decoration: BoxDecoration(
            color: isActive ? const Color(0xFF3a3a3a) : Colors.transparent,
            borderRadius: BorderRadius.circular(8),
          ),
          child: Material(
            color: Colors.transparent,
            child: InkWell(
              borderRadius: BorderRadius.circular(8),
              onTap: () async {
                // Switch to this conversation and its corresponding persona
                final personaName = conversation['persona_name'];
                if (personaName != null) {
                  await _selectPersona(personaName);
                  print("📂 [Main] Switched to conversation: ${conversation['title']} (Persona: $personaName)");
                }
              },
              child: Padding(
                padding: const EdgeInsets.all(12),
                child: Row(
                  children: [
                    // Conversation info
                    Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                            conversation['title'] ?? 'Untitled Chat',
                            style: const TextStyle(
                              color: Colors.white,
                            fontSize: 14,
                            fontWeight: FontWeight.w500,
                          ),
                            maxLines: 1,
                            overflow: TextOverflow.ellipsis,
                        ),
                          const SizedBox(height: 2),
                        Text(
                            conversation['persona_name'] ?? 'Unknown',
                            style: TextStyle(
                              color: Colors.grey.shade400,
                              fontSize: 12,
                            ),
                          ),
                        ],
                      ),
                    ),
                    
                    // Three dots menu
                    MouseRegion(
                      cursor: SystemMouseCursors.click,
                      child: GestureDetector(
                        onTap: () => _showConversationMenu(context, conversation),
                        child: Container(
                          padding: const EdgeInsets.all(4),
                          child: Icon(
                            Icons.more_horiz,
                            color: Colors.grey.shade400,
                            size: 18,
                          ),
                        ),
                      ),
                    ),
                  ],
                ),
              ),
            ),
          ),
        );
      },
    );
  }

  // Show conversation context menu (rename/delete)
  void _showConversationMenu(BuildContext context, Map<String, dynamic> conversation) {
    showDialog(
      context: context,
      builder: (BuildContext context) {
        return AlertDialog(
          backgroundColor: const Color(0xFF2c2c2c),
          title: Text(
            conversation['title'] ?? 'Conversation',
            style: const TextStyle(color: Colors.white),
          ),
          content: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              ListTile(
                leading: const Icon(Icons.edit, color: Colors.white),
                title: const Text(
                  'Rename',
                  style: TextStyle(color: Colors.white),
                ),
                onTap: () {
                  Navigator.of(context).pop();
                  _showRenameDialog(context, conversation);
                },
              ),
              ListTile(
                leading: const Icon(Icons.delete, color: Colors.red),
                title: const Text(
                  'Delete',
                  style: TextStyle(color: Colors.red),
                ),
                onTap: () {
                  Navigator.of(context).pop();
                  _showDeleteDialog(context, conversation);
                },
              ),
            ],
          ),
        );
      },
    );
  }

  // Show rename dialog
  void _showRenameDialog(BuildContext context, Map<String, dynamic> conversation) {
    final controller = TextEditingController(text: conversation['title'] ?? '');
    
    showDialog(
      context: context,
      builder: (BuildContext context) {
        return AlertDialog(
          backgroundColor: const Color(0xFF2c2c2c),
          title: const Text(
            'Rename Conversation',
            style: TextStyle(color: Colors.white),
          ),
          content: TextField(
            controller: controller,
            style: const TextStyle(color: Colors.white),
            decoration: const InputDecoration(
              hintText: 'Enter new title',
              hintStyle: TextStyle(color: Colors.grey),
              enabledBorder: UnderlineInputBorder(
                borderSide: BorderSide(color: Colors.grey),
              ),
              focusedBorder: UnderlineInputBorder(
                borderSide: BorderSide(color: Colors.blue),
              ),
            ),
          ),
          actions: [
            TextButton(
              onPressed: () => Navigator.of(context).pop(),
              child: const Text('Cancel'),
            ),
            TextButton(
              onPressed: () {
                Navigator.of(context).pop();
                _renameConversation(conversation['id'], controller.text.trim());
              },
              child: const Text('Rename'),
            ),
          ],
        );
      },
    );
  }

  // Show delete confirmation dialog
  void _showDeleteDialog(BuildContext context, Map<String, dynamic> conversation) {
    showDialog(
      context: context,
      builder: (BuildContext context) {
        return AlertDialog(
          backgroundColor: const Color(0xFF2c2c2c),
          title: const Text(
            'Delete Conversation',
            style: TextStyle(color: Colors.white),
          ),
          content: Text(
            'Are you sure you want to delete "${conversation['title']}"? This action cannot be undone.',
            style: const TextStyle(color: Colors.white),
          ),
          actions: [
            TextButton(
              onPressed: () => Navigator.of(context).pop(),
              child: const Text('Cancel'),
            ),
            TextButton(
              onPressed: () {
                Navigator.of(context).pop();
                _deleteConversation(conversation['id']);
              },
              style: TextButton.styleFrom(foregroundColor: Colors.red),
              child: const Text('Delete'),
            ),
          ],
        );
      },
    );
  }
  
  @override
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
      return _buildLoginScreen();
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
        if (_isNeuraPalsOpen) _buildNeuraPalsWindow(),
      ],
    ),
      ),
    );
  }

  // Build NeuraPals persona selector window
  Widget _buildNeuraPalsWindow() {
    return Center(
      child: GestureDetector(
        onTap: () {}, // Prevent click propagation to background
        child: Container(
          width: 700,
          height: 500,
          padding: const EdgeInsets.all(20),
          decoration: BoxDecoration(
            color: const Color(0xFF2c2c2c),
            borderRadius: BorderRadius.circular(12),
            border: Border.all(color: const Color(0xFF555555)),
            boxShadow: [
              BoxShadow(
                color: Colors.black.withOpacity(0.3),
                blurRadius: 10,
                offset: const Offset(0, 5),
              ),
            ],
          ),
          child: Column(
            children: [
              // Header
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  const Text(
                    'Select NeuraPal',
                    style: TextStyle(
                      color: Colors.white,
                      fontSize: 18,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                  MouseRegion(
                    cursor: SystemMouseCursors.click,
                    child: GestureDetector(
                      onTap: _closeNeuraPals,
                      child: Container(
                        padding: const EdgeInsets.all(4),
                        child: const Icon(
                          Icons.close,
                          color: Colors.grey,
                          size: 20,
                        ),
                      ),
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 20),
              
              // Persona grid
              Expanded(
                child: GridView.builder(
                  gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
                    crossAxisCount: 5,
                    childAspectRatio: 1.0,
                    crossAxisSpacing: 10,
                    mainAxisSpacing: 10,
                  ),
                  itemCount: _availablePersonas.length,
                  itemBuilder: (context, index) {
                    final persona = _availablePersonas[index];
                    final isActive = persona['name'] == _currentPersona?.name;
                    
                    return MouseRegion(
                      cursor: SystemMouseCursors.click,
                      child: GestureDetector(
                        onTap: () => _selectPersona(persona['name']),
                        child: Container(
                          padding: const EdgeInsets.all(6),
                          decoration: BoxDecoration(
                            color: const Color(0xFF3a3a3a),
                            borderRadius: BorderRadius.circular(8),
                            border: Border.all(
                              color: isActive ? Colors.blue : const Color(0xFF555555),
                              width: isActive ? 2 : 1,
                            ),
                            boxShadow: isActive ? [
                              BoxShadow(
                                color: Colors.blue.withOpacity(0.3),
                                blurRadius: 8,
                                spreadRadius: 2,
                              ),
                            ] : null,
                          ),
                          child: Column(
                            mainAxisAlignment: MainAxisAlignment.center,
                            children: [
                              // Avatar
                              Stack(
                                children: [
                                  Container(
                                    width: 36,
                                    height: 36,
                                    decoration: BoxDecoration(
                                      color: Colors.blue,
                                      borderRadius: BorderRadius.circular(18),
                                      border: isActive ? Border.all(
                                        color: Colors.blue,
                                        width: 3,
                                      ) : null,
                                    ),
                                    child: Center(
                                      child: Text(
                                        persona['name'][0].toUpperCase(),
                                        style: const TextStyle(
                                          color: Colors.white,
                                          fontSize: 16,
                                          fontWeight: FontWeight.bold,
                                        ),
                                      ),
                                    ),
                                  ),
                                  // Active indicator
                                  if (isActive)
                                    Positioned(
                                      bottom: 0,
                                      right: 0,
                                      child: Container(
                                        width: 14,
                                        height: 14,
                                        decoration: BoxDecoration(
                                          color: Colors.blue,
                                          borderRadius: BorderRadius.circular(7),
                                          border: Border.all(color: const Color(0xFF3a3a3a), width: 1),
                                        ),
                                        child: const Icon(
                                          Icons.check,
                                          color: Colors.white,
                                          size: 8,
                                        ),
                                      ),
                                    ),
                                ],
                              ),
                              const SizedBox(height: 4),
                              
                              // Name
                              Text(
                                persona['name'],
                                style: TextStyle(
                                  color: isActive ? Colors.blue : Colors.white,
                                  fontSize: 11,
                                  fontWeight: isActive ? FontWeight.bold : FontWeight.normal,
                                ),
                                textAlign: TextAlign.center,
                              ),
                            ],
                          ),
                        ),
                      ),
                    );
                  },
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  // Build fullscreen login screen
  Widget _buildLoginScreen() {
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
                        // Update auth state and load initial persona
                        setState(() {
                          _isSignedIn = true;
                        });
                        await _loadInitialPersona();
                      } else {
                        _showErrorDialog('Sign-in failed. Please try again.');
                      }
                    } catch (e) {
                      _showErrorDialog('Sign-in error: $e');
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
