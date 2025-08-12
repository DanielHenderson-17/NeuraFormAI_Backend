import 'package:flutter/material.dart';
import '../models/chat_message.dart';

class ChatBubble extends StatelessWidget {
  final ChatMessage message;
  
  const ChatBubble({
    Key? key,
    required this.message,
  }) : super(key: key);
  
  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 8.0, horizontal: 8.0),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        mainAxisAlignment: message.isUser 
            ? MainAxisAlignment.end    // User messages on right
            : MainAxisAlignment.start, // AI messages on left
        children: [
          if (message.isUser) ...[
            // User: Message content (on right)
            Flexible(
              child: _buildMessageBubble(isUser: true),
            ),
          ] else ...[
            // AI: Message content (on left)
            Flexible(
              child: _buildMessageBubble(isUser: false),
            ),
          ],
        ],
      ),
    );
  }

  Widget _buildMessageBubble({required bool isUser}) {
    return Column(
      crossAxisAlignment: isUser ? CrossAxisAlignment.end : CrossAxisAlignment.start,
      children: [
        // Message bubble
        Container(
          constraints: const BoxConstraints(
            maxWidth: 250,
          ),
          padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
          decoration: BoxDecoration(
            color: isUser 
                ? Colors.blue.shade600 
                : Colors.grey.shade700,
            borderRadius: BorderRadius.circular(12),
          ),
          child: _buildMessageContent(),
        ),
        
        // Header with name and time (moved below bubble)
        Padding(
          padding: const EdgeInsets.only(top: 4.0),
          child: Row(
            mainAxisSize: MainAxisSize.min,
            children: [
              Text(
                isUser ? 'You' : (message.personaName ?? 'AI'),
                style: TextStyle(
                  fontWeight: FontWeight.bold,
                  fontSize: 12,
                  color: Colors.grey.shade300,
                ),
              ),
              const SizedBox(width: 6),
              Text(
                _formatTime(message.timestamp),
                style: TextStyle(
                  color: Colors.grey.shade400,
                  fontSize: 10,
                ),
              ),
            ],
          ),
        ),
        
        // Metadata if available
        if (message.metadata != null && message.metadata!.isNotEmpty)
          Padding(
            padding: const EdgeInsets.only(top: 4.0),
            child: _buildMetadata(),
          ),
      ],
    );
  }
  
  Widget _buildMessageContent() {
    // Check if message contains code blocks
    if (_containsCodeBlock(message.content)) {
      return _buildCodeBlockMessage();
    }
    
    // Regular text message
    return SelectableText(
      message.content,
      style: const TextStyle(
        fontSize: 14,
        color: Colors.white,
        height: 1.4,
      ),
    );
  }
  
  Widget _buildCodeBlockMessage() {
    final parts = _splitCodeBlocks(message.content);
    
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: parts.map((part) {
        if (part.startsWith('```') && part.endsWith('```')) {
          // Code block
          final code = part.substring(3, part.length - 3);
          final language = _extractLanguage(part);
          
          return Container(
            margin: const EdgeInsets.symmetric(vertical: 4),
            padding: const EdgeInsets.all(12),
            decoration: BoxDecoration(
              color: Colors.grey.shade900,
              borderRadius: BorderRadius.circular(8),
            ),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                if (language.isNotEmpty)
                  Padding(
                    padding: const EdgeInsets.only(bottom: 8),
                    child: Text(
                      language,
                      style: TextStyle(
                        color: Colors.grey.shade400,
                        fontSize: 12,
                        fontWeight: FontWeight.w500,
                      ),
                    ),
                  ),
                SelectableText(
                  code,
                  style: const TextStyle(
                    color: Colors.white,
                    fontSize: 14,
                    fontFamily: 'monospace',
                    height: 1.3,
                  ),
                ),
              ],
            ),
          );
        } else {
          // Regular text
          return Padding(
            padding: const EdgeInsets.symmetric(vertical: 4),
            child: SelectableText(
              part,
              style: TextStyle(
                fontSize: 16,
                color: message.isUser ? Colors.black87 : Colors.black87,
                height: 1.4,
              ),
            ),
          );
        }
      }).toList(),
    );
  }
  
  Widget _buildMetadata() {
    final metadata = message.metadata!;
    final List<Widget> metadataWidgets = [];
    
    // Emotion
    if (metadata['emotion'] != null) {
      metadataWidgets.add(
        Chip(
          label: Text('😊 ${metadata['emotion']}'),
          backgroundColor: Colors.blue.shade100,
          labelStyle: TextStyle(
            color: Colors.blue.shade800,
            fontSize: 12,
          ),
        ),
      );
    }
    
    // Gesture
    if (metadata['gesture'] != null) {
      metadataWidgets.add(
        Chip(
          label: Text('👋 ${metadata['gesture']}'),
          backgroundColor: Colors.green.shade100,
          labelStyle: TextStyle(
            color: Colors.green.shade800,
            fontSize: 12,
          ),
        ),
      );
    }
    
    // Confidence
    if (metadata['confidence'] != null) {
      final confidence = metadata['confidence'] as double;
      final color = confidence > 0.8 
          ? Colors.green 
          : confidence > 0.6 
              ? Colors.orange 
              : Colors.red;
      
      metadataWidgets.add(
        Chip(
          label: Text('${(confidence * 100).toStringAsFixed(1)}%'),
          backgroundColor: color.shade100,
          labelStyle: TextStyle(
            color: color.shade800,
            fontSize: 12,
          ),
        ),
      );
    }
    
    if (metadataWidgets.isEmpty) return const SizedBox.shrink();
    
    return Wrap(
      spacing: 8,
      runSpacing: 4,
      children: metadataWidgets,
    );
  }
  
  String _formatTime(DateTime timestamp) {
    // Format: hh:mm:ss AM/PM mm/dd/yyyy
    final hour = timestamp.hour;
    final minute = timestamp.minute.toString().padLeft(2, '0');
    final second = timestamp.second.toString().padLeft(2, '0');
    final month = timestamp.month.toString().padLeft(2, '0');
    final day = timestamp.day.toString().padLeft(2, '0');
    final year = timestamp.year;
    
    // Convert to 12-hour format
    final hour12 = hour == 0 ? 12 : (hour > 12 ? hour - 12 : hour);
    final ampm = hour >= 12 ? 'PM' : 'AM';
    final hourStr = hour12.toString().padLeft(2, '0');
    
    return '$hourStr:$minute:$second $ampm $month/$day/$year';
  }
  
  bool _containsCodeBlock(String text) {
    return text.contains('```');
  }
  
  List<String> _splitCodeBlocks(String text) {
    final regex = RegExp(r'```.*?```', dotAll: true);
    final matches = regex.allMatches(text);
    
    if (matches.isEmpty) {
      return [text];
    }
    
    final List<String> parts = [];
    int lastIndex = 0;
    
    for (final match in matches) {
      // Add text before code block
      if (match.start > lastIndex) {
        parts.add(text.substring(lastIndex, match.start));
      }
      
      // Add code block
      parts.add(text.substring(match.start, match.end));
      lastIndex = match.end;
    }
    
    // Add remaining text after last code block
    if (lastIndex < text.length) {
      parts.add(text.substring(lastIndex));
    }
    
    return parts;
  }
  
  String _extractLanguage(String codeBlock) {
    final lines = codeBlock.split('\n');
    if (lines.length > 1) {
      final firstLine = lines[0].trim();
      if (firstLine.startsWith('```')) {
        return firstLine.substring(3).trim();
      }
    }
    return '';
  }
}
