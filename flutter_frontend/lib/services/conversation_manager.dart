import 'package:flutter/material.dart';
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
  
  static void showConversationMenu(
    BuildContext context, 
    Map<String, dynamic> conversation,
    Function(String, String) onRename,
    Function(String) onDelete,
  ) {
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
                  showRenameDialog(context, conversation, onRename);
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
                  showDeleteDialog(context, conversation, onDelete);
                },
              ),
            ],
          ),
        );
      },
    );
  }
  
  static void showRenameDialog(
    BuildContext context,
    Map<String, dynamic> conversation,
    Function(String, String) onRename,
  ) {
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
                onRename(conversation['id'], controller.text.trim());
              },
              child: const Text('Rename'),
            ),
          ],
        );
      },
    );
  }

  // Helper method to build conversation list UI
  static Widget buildConversationList({
    required List<Map<String, dynamic>> conversations,
    required String? activeConversationId,
    required bool isLoadingConversations,
    required Function(String) onConversationSelected,
    required Function(String, String) onRename,
    required Function(String) onDelete,
    required BuildContext context,
  }) {
    if (isLoadingConversations) {
      return const Center(
        child: CircularProgressIndicator(
          color: Colors.grey,
          strokeWidth: 2,
        ),
      );
    }
    
    if (conversations.isEmpty) {
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
      itemCount: conversations.length,
      itemBuilder: (context, index) {
        final conversation = conversations[index];
        final isActive = conversation['id'] == activeConversationId;
        
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
                  onConversationSelected(personaName);
                  print("📂 [ConversationManager] Switched to conversation: ${conversation['title']} (Persona: $personaName)");
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
                        onTap: () => showConversationMenu(
                          context, 
                          conversation,
                          onRename,
                          onDelete,
                        ),
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

  static void showDeleteDialog(
    BuildContext context,
    Map<String, dynamic> conversation,
    Function(String) onDelete,
  ) {
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
                onDelete(conversation['id']);
              },
              style: TextButton.styleFrom(foregroundColor: Colors.red),
              child: const Text('Delete'),
            ),
          ],
        );
      },
    );
  }
}