import '../models/chat_message.dart';
import '../services/auth_service.dart';
import '../services/persona_service.dart';

class ConversationManager {
  // Helper method to get conversation history as ChatMessage objects
  static Future<List<ChatMessage>> getConversationHistoryMessages(String? currentPersonaName) async {
    try {
      final historyData = await PersonaService.getConversationHistory();
      final historyMessages = <ChatMessage>[];
      
      for (final msgData in historyData) {
        final message = ChatMessage(
          id: msgData['id'] ?? DateTime.now().millisecondsSinceEpoch.toString(),
          content: msgData['content'] ?? '',
          isUser: msgData['sender_type'] == 'user',
          timestamp: DateTime.tryParse(msgData['created_at'] ?? '') ?? DateTime.now(),
          personaName: currentPersonaName ?? 'AI',
        );
        historyMessages.add(message);
      }
      
      print("📚 [ConversationManager] Loaded ${historyMessages.length} messages from conversation history");
      return historyMessages;
      
    } catch (e) {
      print("❌ [ConversationManager] Error loading conversation history: $e");
      return [];
    }
  }
  
  // Helper method to get conversations list
  static Future<List<Map<String, dynamic>>> getConversationsList() async {
    try {
      final userId = AuthService.userId;
      if (userId == null) {
        print("⚠️ [ConversationManager] No user ID available");
        return [];
      }
      
      final response = await PersonaService.getConversations(userId);
      print("📂 [ConversationManager] Loaded ${response.length} conversations");
      return response;
      
    } catch (e) {
      print("❌ [ConversationManager] Error loading conversations: $e");
      return [];
    }
  }
  
  // Helper method to rename a conversation
  static Future<bool> renameConversation(String conversationId, String newTitle) async {
    try {
      final success = await PersonaService.updateConversationTitle(conversationId, newTitle);
      
      if (success) {
        print("✏️ [ConversationManager] Conversation renamed to: $newTitle");
      }
      
      return success;
      
    } catch (e) {
      print("❌ [ConversationManager] Error renaming conversation: $e");
      return false;
    }
  }
  
  // Helper method to delete a conversation
  static Future<bool> deleteConversation(String conversationId) async {
    try {
      final success = await PersonaService.deleteConversation(conversationId);
      
      if (success) {
        print("🗑️ [ConversationManager] Conversation deleted");
      }
      
      return success;
      
    } catch (e) {
      print("❌ [ConversationManager] Error deleting conversation: $e");
      return false;
    }
  }
}