import 'package:flutter/material.dart';

class VRMPhonemeControls extends StatelessWidget {
  final void Function(String phoneme)? onSetPhoneme;
  final VoidCallback? onClearPhonemes;

  const VRMPhonemeControls({
    Key? key,
    this.onSetPhoneme,
    this.onClearPhonemes,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Positioned(
      bottom: 10,
      left: 10,
      child: Container(
        padding: const EdgeInsets.all(8),
        decoration: BoxDecoration(
          color: Colors.black.withOpacity(0.7),
          borderRadius: BorderRadius.circular(8),
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              'Phonemes (Lip Sync)',
              style: TextStyle(
                color: Colors.white,
                fontSize: 12,
                fontWeight: FontWeight.bold,
              ),
            ),
            const SizedBox(height: 8),
            Wrap(
              spacing: 4,
              runSpacing: 4,
              children: [
                // Phoneme buttons based on your setLipSync mapping
                _buildPhonemeButton('aa', '🅰️', 'A sound'),
                _buildPhonemeButton('ih', 'Ⓘ', 'I sound'),
                _buildPhonemeButton('ou', '🅾️', 'U sound'),
                _buildPhonemeButton('ee', 'Ⓔ', 'E sound'),
                _buildPhonemeButton('oh', '🔴', 'O sound'),
                // Clear button
                _buildClearButton(),
              ],
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildPhonemeButton(String phoneme, String emoji, String tooltip) {
    return Tooltip(
      message: tooltip,
      child: SizedBox(
        width: 32,
        height: 32,
        child: ElevatedButton(
          onPressed: () => onSetPhoneme?.call(phoneme),
          style: ElevatedButton.styleFrom(
            padding: EdgeInsets.zero,
            minimumSize: const Size(32, 32),
            backgroundColor: Colors.grey[800],
            foregroundColor: Colors.white,
          ),
          child: Text(
            emoji,
            style: const TextStyle(fontSize: 14),
          ),
        ),
      ),
    );
  }

  Widget _buildClearButton() {
    return Tooltip(
      message: 'Clear all phonemes',
      child: SizedBox(
        width: 32,
        height: 32,
        child: ElevatedButton(
          onPressed: onClearPhonemes,
          style: ElevatedButton.styleFrom(
            padding: EdgeInsets.zero,
            minimumSize: const Size(32, 32),
            backgroundColor: Colors.red[800],
            foregroundColor: Colors.white,
          ),
          child: const Text(
            '🚫',
            style: TextStyle(fontSize: 14),
          ),
        ),
      ),
    );
  }
}
