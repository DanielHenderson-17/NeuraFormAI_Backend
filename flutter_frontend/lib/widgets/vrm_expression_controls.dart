import 'package:flutter/material.dart';

class VRMExpressionControls extends StatelessWidget {
  final void Function(String emotion)? onSetEmotion;
  final VoidCallback? onBlink;

  const VRMExpressionControls({
    Key? key,
    this.onSetEmotion,
    this.onBlink,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Row(
      mainAxisAlignment: MainAxisAlignment.center,
      children: [
        // Example emotion buttons
        _buildExpressionButton('Happy', '😊'),
        _buildExpressionButton('Sad', '😢'),
        _buildExpressionButton('Angry', '😠'),
        _buildExpressionButton('Surprised', '😮'),
        // Blink button
        IconButton(
          icon: const Icon(Icons.remove_red_eye),
          tooltip: 'Blink',
          onPressed: onBlink,
        ),
      ],
    );
  }

  Widget _buildExpressionButton(String emotion, String emoji) {
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 4.0),
      child: ElevatedButton(
        onPressed: () => onSetEmotion?.call(emotion),
        child: Text(emoji, style: const TextStyle(fontSize: 20)),
      ),
    );
  }
}
