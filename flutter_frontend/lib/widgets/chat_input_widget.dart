import 'package:flutter/material.dart';
import '../widgets/voice_toggle_switch.dart';

class ChatInputWidget extends StatelessWidget {
  final TextEditingController controller;
  final FocusNode focusNode;
  final bool isLoading;
  final bool isVoiceEnabled;
  final bool isChatWindowVisible;
  final VoidCallback onSendMessage;
  final Function(bool) onVoiceToggle;
  final VoidCallback onChatToggle;
  final VoidCallback onMicrophonePressed;

  const ChatInputWidget({
    super.key,
    required this.controller,
    required this.focusNode,
    required this.isLoading,
    required this.isVoiceEnabled,
    required this.isChatWindowVisible,
    required this.onSendMessage,
    required this.onVoiceToggle,
    required this.onChatToggle,
    required this.onMicrophonePressed,
  });

  @override
  Widget build(BuildContext context) {
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
                  initialValue: isVoiceEnabled,
                  onChanged: onVoiceToggle,
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
                        controller: controller,
                        focusNode: focusNode,
                        style: const TextStyle(
                          color: Colors.white,
                          fontSize: 14,
                        ),
                        decoration: InputDecoration(
                          hintText: isLoading ? 'AI is typing...' : 'Start typing...',
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
                          if (!isLoading) onSendMessage();
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
                                  onTap: onChatToggle,
                                  child: Container(
                                    decoration: BoxDecoration(
                                      color: isChatWindowVisible ? Colors.grey.withOpacity(0.3) : Colors.transparent,
                                      borderRadius: BorderRadius.circular(6),
                                    ),
                                    child: Icon(
                                      isChatWindowVisible ? Icons.chat_bubble : Icons.chat_bubble_outline,
                                      color: isChatWindowVisible ? Colors.blue : Colors.white,
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
                                  onTap: onMicrophonePressed,
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
                                  onTap: isLoading ? null : onSendMessage,
                                  child: Container(
                                    decoration: BoxDecoration(
                                      color: Colors.transparent,
                                      borderRadius: BorderRadius.circular(6),
                                    ),
                                    child: Icon(
                                      Icons.arrow_upward_rounded,
                                      color: isLoading ? Colors.grey : Colors.white,
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
}
