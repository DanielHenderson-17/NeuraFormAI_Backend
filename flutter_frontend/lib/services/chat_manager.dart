import 'package:flutter/material.dart';
import '../models/persona.dart';
import '../models/chat_message.dart';
import '../services/auth_service.dart';
import '../services/persona_service.dart';
import '../services/voice_player.dart';

class ChatResult {
  final List<ChatMessage> newMessages;
  final String? conversationId;
  final bool shouldReloadConversations;

  ChatResult({
    required this.newMessages,
    this.conversationId,
    this.shouldReloadConversations = false,
  });
}

class ChatManager {
  static Future<ChatResult> processMessage({
    required String message,
    required Persona? currentPersona,
    required bool voiceEnabled,
    String? activeConversationId,
    Function(String response, double? audioDuration, {double? durationPerWord})? onVrmLipSync,
  }) async {
    final newMessages = <ChatMessage>[];
    String? updatedConversationId = activeConversationId;
    bool shouldReloadConversations = false;

    try {
      // Check for persona switching commands (switch to / swap to)
      final switchMatch = RegExp(r'^(?:switch|swap)\s+to\s+(.+)$', caseSensitive: false).firstMatch(message);
      if (switchMatch != null) {
        final personaName = switchMatch.group(1)?.trim();
        if (personaName != null && personaName.isNotEmpty) {
          print("🔄 [ChatManager] Typed command detected — switching to persona: $personaName");
          
          // Don't add the command to chat history - it's a system command
          
          try {
            // Switch to the persona and load their conversation immediately
            final hadExistingConversation = activeConversationId != null;
            
            // This will be handled by the calling code since it involves state management
            // We'll return a special result indicating persona switch is needed
            
            // For now, we'll just process this as a message indicating persona switch
            // The actual persona switching will be handled in main.dart
            
            // Since this involves complex state management, we'll handle this differently
            // Return empty result for now - the calling code will handle persona switching
            return ChatResult(newMessages: []);
            
          } catch (e) {
            print("❌ [ChatManager] Error during persona switch: $e");
            final errorMessage = ChatMessage(
              id: DateTime.now().millisecondsSinceEpoch.toString(),
              content: "Sorry, I couldn't switch to that persona. Please try again.",
              isUser: false,
              timestamp: DateTime.now(),
            );
            newMessages.add(errorMessage);
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
        
        newMessages.add(userMessage);
        
        try {
          final response = await PersonaService.fetchReply(message, voiceEnabled: voiceEnabled);
          
          final aiMessage = ChatMessage(
            id: DateTime.now().millisecondsSinceEpoch.toString(),
            content: response,
            isUser: false,
            timestamp: DateTime.now(),
            personaName: currentPersona?.name ?? 'AI',
          );
          
          newMessages.add(aiMessage);
          shouldReloadConversations = true;
          
          // Update active conversation ID if it wasn't set (new conversation)
          if (activeConversationId == null && currentPersona != null) {
            final userId = AuthService.userId;
            if (userId != null) {
              final conversationId = await PersonaService.getConversationForPersona(userId, currentPersona.name);
              updatedConversationId = conversationId;
            }
          }
          
          // Handle voice/lip sync if callback provided
          if (onVrmLipSync != null) {
            if (voiceEnabled) {
              print("🎤 Voice enabled - starting TTS playback");
              VoicePlayer.playReplyFromBackend(response, voiceEnabled: true, onStart: (audioDuration) {
                // Start voice-synchronized lip sync
                if (audioDuration != null) {
                  onVrmLipSync(response, audioDuration);
                }
              });
            } else {
              // Voice disabled - just do text-based lip sync with EXACT Python timing
              onVrmLipSync(response, null, durationPerWord: 0.08);
            }
          }
          
        } catch (e) {
          print("❌ [ChatManager] Error sending message: $e");
          final errorMessage = ChatMessage(
            id: DateTime.now().millisecondsSinceEpoch.toString(),
            content: "Sorry, I couldn't process your message. Please try again.",
            isUser: false,
            timestamp: DateTime.now(),
          );
          newMessages.add(errorMessage);
        }
      }
    } catch (e) {
      print("❌ [ChatManager] Unexpected error: $e");
      final errorMessage = ChatMessage(
        id: DateTime.now().millisecondsSinceEpoch.toString(),
        content: "An unexpected error occurred. Please try again.",
        isUser: false,
        timestamp: DateTime.now(),
      );
      newMessages.add(errorMessage);
    }

    return ChatResult(
      newMessages: newMessages,
      conversationId: updatedConversationId,
      shouldReloadConversations: shouldReloadConversations,
    );
  }

  // Handle persona switching with welcome/intro messages
  static Future<ChatResult> handlePersonaSwitch({
    required String personaName,
    required Persona? currentPersona,
    required bool voiceEnabled,
    String? activeConversationId,
    required List<ChatMessage> currentMessages,
    Function(String response, double? audioDuration, {double? durationPerWord})? onVrmLipSync,
  }) async {
    final newMessages = <ChatMessage>[];
    
    try {
      // The actual persona switching logic would be handled by the caller
      // This method handles the welcome/intro messages after switch
      
      final hadExistingConversation = activeConversationId != null;
      
      if (activeConversationId != null && !hadExistingConversation && currentMessages.isNotEmpty) {
        // Existing conversation - send welcome back message (hidden from history)
        print("🔄 [ChatManager] Found existing conversation with ${currentMessages.length} messages - sending welcome back");
        final response = await PersonaService.fetchReply(
          "The user just returned to continue our conversation. Give them a brief, personalized welcome back message that fits your personality.", 
          voiceEnabled: voiceEnabled,
          saveToHistory: false
        );
        
        final aiMessage = ChatMessage(
          id: DateTime.now().millisecondsSinceEpoch.toString(),
          content: response,
          isUser: false,
          timestamp: DateTime.now(),
          personaName: currentPersona?.name ?? 'AI',
        );
        
        newMessages.add(aiMessage);
        
        // Handle voice/lip sync if callback provided
        if (onVrmLipSync != null) {
          if (voiceEnabled) {
            print("🎤 Voice enabled - starting TTS playback for welcome back");
            VoicePlayer.playReplyFromBackend(response, voiceEnabled: true, onStart: (audioDuration) {
              if (audioDuration != null) {
                onVrmLipSync(response, audioDuration);
              }
            });
          } else {
            onVrmLipSync(response, null, durationPerWord: 0.08);
          }
        }
        
      } else if (activeConversationId == null && currentMessages.isEmpty) {
        // New conversation - send introduction (hidden from history)
        print("🔄 [ChatManager] No existing conversation - sending introduction");
        final response = await PersonaService.fetchReply(
          "Introduce yourself briefly as the new persona.", 
          voiceEnabled: voiceEnabled,
          saveToHistory: false
        );
        
        final aiMessage = ChatMessage(
          id: DateTime.now().millisecondsSinceEpoch.toString(),
          content: response,
          isUser: false,
          timestamp: DateTime.now(),
          personaName: currentPersona?.name ?? 'AI',
        );
        
        newMessages.add(aiMessage);
        
        // Handle voice/lip sync if callback provided
        if (onVrmLipSync != null) {
          if (voiceEnabled) {
            print("🎤 Voice enabled - starting TTS playback for persona introduction");
            VoicePlayer.playReplyFromBackend(response, voiceEnabled: true, onStart: (audioDuration) {
              if (audioDuration != null) {
                onVrmLipSync(response, audioDuration);
              }
            });
          } else {
            onVrmLipSync(response, null, durationPerWord: 0.08);
          }
        }
      } else {
        print("🔄 [ChatManager] Switched to persona $personaName - no welcome message needed (${currentMessages.length} messages loaded)");
      }
      
    } catch (e) {
      print("❌ [ChatManager] Error during persona switch: $e");
      final errorMessage = ChatMessage(
        id: DateTime.now().millisecondsSinceEpoch.toString(),
        content: "Sorry, I couldn't switch to that persona. Please try again.",
        isUser: false,
        timestamp: DateTime.now(),
      );
      newMessages.add(errorMessage);
    }
    
    return ChatResult(
      newMessages: newMessages,
      conversationId: activeConversationId,
      shouldReloadConversations: false,
    );
  }
}
