import 'dart:convert';
import 'package:http/http.dart' as http;
import 'auth_service.dart';

class PersonaService {
  static const String baseUrl = "http://127.0.0.1:8000/api/personas";
  static const String chatUrl = "http://127.0.0.1:8000/chat/";
  
  static String? _userId;
  static Map<String, dynamic>? _activePersona;
  static Function(String)? _onPersonaChanged;
  static Function(String)? _onVrmModelChanged;
  
  static void setUserId(String userId) {
    _userId = userId;
  }
  
  static String getUserId() {
    // Try to get from AuthService first
    final authUserId = AuthService.userId;
    if (authUserId != null) {
      return authUserId;
    }
    
    // Fallback to local storage
    if (_userId == null) {
      throw Exception("No authenticated user. Please sign in.");
    }
    return _userId!;
  }
  
  static void setPersonaChangedCallback(Function(String) callback) {
    _onPersonaChanged = callback;
  }
  
  static void setVrmModelChangedCallback(Function(String) callback) {
    _onVrmModelChanged = callback;
  }
  
  static Map<String, String> _getHeaders() {
    final sessionToken = AuthService.sessionToken;
    if (sessionToken == null) {
      return {"Content-Type": "application/json"};
    }
    return {
      "Content-Type": "application/json",
      "Authorization": "Bearer $sessionToken",
    };
  }
  
  static Future<List<Map<String, dynamic>>> listPersonas() async {
    try {
      print("🔎 [PersonaService] Fetching persona list...");
      final response = await http.get(
        Uri.parse("$baseUrl/list"),
        headers: _getHeaders(),
      );
      
      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        return List<Map<String, dynamic>>.from(data["personas"] ?? []);
      } else {
        print("❌ [PersonaService] Failed to fetch persona list: ${response.statusCode}");
        return [];
      }
    } catch (e) {
      print("❌ [PersonaService] Failed to fetch persona list: $e");
      return [];
    }
  }
  
  static Future<Map<String, dynamic>> getActivePersona() async {
    try {
      final userId = getUserId();
      final response = await http.post(
        Uri.parse("$baseUrl/active"),
        headers: _getHeaders(),
        body: json.encode({"user_id": userId}),
      );
      
      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        _activePersona = data["active_persona"] ?? {};
        return _activePersona!;
      } else {
        print("❌ [PersonaService] Failed to fetch active persona: ${response.statusCode}");
        return {};
      }
    } catch (e) {
      print("❌ [PersonaService] Failed to fetch active persona: $e");
      return {};
    }
  }
  
  static Future<Map<String, dynamic>> selectPersona(String personaName) async {
    try {
      final userId = getUserId();
      print("🛠️ [PersonaService] Selecting persona '$personaName' for user_id=$userId");
      
      final response = await http.post(
        Uri.parse("$baseUrl/select"),
        headers: _getHeaders(),
        body: json.encode({
          "user_id": userId,
          "persona_name": personaName
        }),
      );
      
      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        _activePersona = data["active_persona"] ?? {};
        
        // Handle VRM model loading
        final vrmModel = _activePersona!["vrm_model"] ?? "";
        final locked = _activePersona!["locked"] ?? false;
        
        if (locked) {
          print("🔒 Persona '$personaName' is locked. VRM will not load.");
        } else if (vrmModel.isNotEmpty) {
          print("✅ Loading VRM model for $personaName: $vrmModel");
          _onVrmModelChanged?.call(vrmModel);
        } else {
          print("⚠️ No VRM model specified for persona $personaName");
        }
        
        // Notify persona change
        _onPersonaChanged?.call(personaName);
        
        return _activePersona!;
      } else {
        print("❌ [PersonaService] Failed to select persona: ${response.statusCode}");
        return {};
      }
    } catch (e) {
      print("❌ [PersonaService] Failed to select persona: $e");
      return {};
    }
  }
  
  static Future<String> fetchReply(String message, {bool voiceEnabled = false, bool saveToHistory = true}) async {
    try {
      final userId = getUserId();
      final activePersona = await getActivePersona();
      final personaName = activePersona["name"] ?? "Assistant";
      
      print("🟢 [PersonaService] Sending message for user_id=$userId, Persona: $personaName, saveToHistory: $saveToHistory");
      
      final response = await http.post(
        Uri.parse(chatUrl),
        headers: _getHeaders(),
        body: json.encode({
          "user_id": userId,
          "message": message,
          "mode": "safe",
          "voice_enabled": voiceEnabled,
          "save_to_history": saveToHistory,
        }),
      );
      
      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        final replyText = data["reply"] ?? "";
        print("🟢 [PersonaService] Reply received: $replyText");
        return replyText;
      } else {
        final errorText = "(Error ${response.statusCode})";
        print("❌ [PersonaService] Error response: $errorText");
        return errorText;
      }
    } catch (e) {
      final errorText = "(Request failed: $e)";
      print("❌ [PersonaService] Exception: $errorText");
      return errorText;
    }
  }
  
  static String getCurrentPersonaName() {
    return _activePersona?["name"] ?? "Assistant";
  }
  
  static bool isPersonaLocked() {
    return _activePersona?["locked"] ?? false;
  }
  
  static String getCurrentVrmModel() {
    return _activePersona?["vrm_model"] ?? "";
  }
  
  static Future<List<Map<String, dynamic>>> getAllPersonas() async {
    try {
      final response = await http.get(
        Uri.parse("$baseUrl/list"),
        headers: _getHeaders(),
      );
      
      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        return List<Map<String, dynamic>>.from(data["personas"] ?? []);
      } else {
        print("❌ [PersonaService] Failed to fetch personas: ${response.statusCode}");
        return [];
      }
    } catch (e) {
      print("❌ [PersonaService] Failed to fetch personas: $e");
      return [];
    }
  }
  
  static Future<List<Map<String, dynamic>>> getConversationHistory() async {
    try {
      final userId = getUserId();
      final activePersona = await getActivePersona();
      final personaName = activePersona["name"] ?? "Assistant";
      
      print("📚 [PersonaService] Loading conversation history for user_id=$userId, persona=$personaName");
      
      final response = await http.get(
        Uri.parse("${chatUrl}history?user_id=$userId&persona_name=$personaName"),
        headers: _getHeaders(),
      );
      
      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        final messages = List<Map<String, dynamic>>.from(data["messages"] ?? []);
        print("📚 [PersonaService] Loaded ${messages.length} messages from history");
        return messages;
      } else {
        print("❌ [PersonaService] Failed to fetch conversation history: ${response.statusCode}");
        return [];
      }
    } catch (e) {
      print("❌ [PersonaService] Failed to fetch conversation history: $e");
      return [];
    }
  }

  // === Conversation Management Methods ===
  
  static Future<String?> getConversationForPersona(String userId, String personaName) async {
    try {
      print("🔍 [PersonaService] Getting conversation for user_id=$userId, persona=$personaName");
      
      final response = await http.get(
        Uri.parse("${chatUrl}conversation-for-persona?user_id=$userId&persona_name=$personaName"),
        headers: _getHeaders(),
      );
      
      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        final conversationId = data["conversation_id"];
        print("🔍 [PersonaService] Found conversation: $conversationId");
        return conversationId;
      } else if (response.statusCode == 404) {
        print("🔍 [PersonaService] No conversation found for persona $personaName");
        return null;
      } else {
        print("❌ [PersonaService] Failed to get conversation for persona: ${response.statusCode}");
        return null;
      }
    } catch (e) {
      print("❌ [PersonaService] Error getting conversation for persona: $e");
      return null;
    }
  }
  
  static Future<List<Map<String, dynamic>>> getConversations(String userId) async {
    try {
      print("📂 [PersonaService] Getting conversations for user_id=$userId");
      
      final response = await http.get(
        Uri.parse("${chatUrl}conversations?user_id=$userId"),
        headers: _getHeaders(),
      );
      
      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        final conversations = List<Map<String, dynamic>>.from(data["conversations"] ?? []);
        print("📂 [PersonaService] Loaded ${conversations.length} conversations");
        return conversations;
      } else {
        print("❌ [PersonaService] Failed to fetch conversations: ${response.statusCode}");
        return [];
      }
    } catch (e) {
      print("❌ [PersonaService] Error fetching conversations: $e");
      return [];
    }
  }
  
  static Future<bool> updateConversationTitle(String conversationId, String title) async {
    try {
      print("✏️ [PersonaService] Updating conversation $conversationId title to: $title");
      
      final response = await http.put(
        Uri.parse("${chatUrl}conversations/$conversationId"),
        headers: _getHeaders(),
        body: json.encode({"title": title}),
      );
      
      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        return data["success"] == true;
      } else {
        print("❌ [PersonaService] Failed to update conversation title: ${response.statusCode}");
        return false;
      }
    } catch (e) {
      print("❌ [PersonaService] Error updating conversation title: $e");
      return false;
    }
  }
  
  static Future<bool> deleteConversation(String conversationId) async {
    try {
      print("🗑️ [PersonaService] Deleting conversation $conversationId");
      
      final response = await http.delete(
        Uri.parse("${chatUrl}conversations/$conversationId"),
        headers: _getHeaders(),
      );
      
      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        return data["success"] == true;
      } else {
        print("❌ [PersonaService] Failed to delete conversation: ${response.statusCode}");
        return false;
      }
    } catch (e) {
      print("❌ [PersonaService] Error deleting conversation: $e");
      return false;
    }
  }
}
