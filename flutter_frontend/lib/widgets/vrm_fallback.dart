import 'package:flutter/material.dart';

class VRMFallback extends StatelessWidget {
  final String? currentVrmModel;
  final List<Map<String, String>> availableAnimations;
  final bool animationsDiscovered;
  final void Function(String animationName) onPlayAnimation;
  final VoidCallback onStopAnimation;
  final void Function(String emotion) onSetEmotion;
  final VoidCallback onBlink;

  const VRMFallback({
    Key? key,
    required this.currentVrmModel,
    required this.availableAnimations,
    required this.animationsDiscovered,
    required this.onPlayAnimation,
    required this.onStopAnimation,
    required this.onSetEmotion,
    required this.onBlink,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Container(
      color: const Color(0xFF1e1e1e),
      child: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Container(
              width: 200,
              height: 200,
              decoration: BoxDecoration(
                color: Colors.purple.withOpacity(0.3),
                borderRadius: BorderRadius.circular(100),
                border: Border.all(color: Colors.purple, width: 2),
              ),
              child: const Icon(
                Icons.person,
                size: 120,
                color: Colors.purple,
              ),
            ),
            const SizedBox(height: 24),
            Text(
              currentVrmModel != null ? currentVrmModel! : 'No Persona Selected',
              style: const TextStyle(
                fontSize: 24,
                fontWeight: FontWeight.bold,
                color: Colors.white,
              ),
            ),
            const SizedBox(height: 8),
            Text(
              currentVrmModel ?? 'Select a persona to see their VRM model',
              style: const TextStyle(
                fontSize: 14,
                color: Colors.grey,
              ),
            ),
            const SizedBox(height: 32),
            const Text(
              'VRM Animation Controls',
              style: TextStyle(
                fontSize: 18,
                fontWeight: FontWeight.bold,
                color: Colors.white,
              ),
            ),
            const SizedBox(height: 16),
            Wrap(
              spacing: 8,
              runSpacing: 8,
              children: [
                if (!animationsDiscovered)
                  _buildAnimationButton('⏳', 'Loading Animations...', () {})
                else ...[
                  ...availableAnimations.map((anim) =>
                    _buildAnimationButton(
                      anim['emoji'] ?? '🎭',
                      anim['displayName'] ?? anim['name'] ?? '',
                      () => onPlayAnimation(anim['name']!)
                    )
                  ).toList(),
                  if (availableAnimations.isEmpty)
                    _buildAnimationButton('❌', 'No Animations Found', () {}),
                ],
                _buildAnimationButton('⏹️', 'Stop', onStopAnimation),
              ],
            ),
            const SizedBox(height: 24),
            const Text(
              'VRM Expression Simulator',
              style: TextStyle(
                fontSize: 18,
                fontWeight: FontWeight.bold,
                color: Colors.white,
              ),
            ),
            const SizedBox(height: 16),
            Wrap(
              spacing: 8,
              runSpacing: 8,
              children: [
                _buildExpressionButton('😊', 'Happy', () => onSetEmotion('happy')),
                _buildExpressionButton('😠', 'Angry', () => onSetEmotion('angry')),
                _buildExpressionButton('😢', 'Sad', () => onSetEmotion('sad')),
                _buildExpressionButton('😮', 'Surprised', () => onSetEmotion('surprised')),
                _buildExpressionButton('😌', 'Relaxed', () => onSetEmotion('relaxed')),
                _buildExpressionButton('😉', 'Blink', onBlink),
              ],
            ),
            const SizedBox(height: 16),
            const Text(
              'VRM 3D viewer not available on this platform.\nUsing fallback persona display.',
              textAlign: TextAlign.center,
              style: TextStyle(
                fontSize: 12,
                color: Colors.grey,
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildAnimationButton(String emoji, String label, VoidCallback onPressed) {
    return ElevatedButton(
      onPressed: onPressed,
      style: ElevatedButton.styleFrom(
        backgroundColor: Colors.blue.withOpacity(0.3),
        foregroundColor: Colors.white,
        padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Text(emoji, style: const TextStyle(fontSize: 18)),
          const SizedBox(width: 6),
          Text(label, style: const TextStyle(fontSize: 12)),
        ],
      ),
    );
  }

  Widget _buildExpressionButton(String emoji, String label, VoidCallback onPressed) {
    return ElevatedButton(
      onPressed: onPressed,
      style: ElevatedButton.styleFrom(
        backgroundColor: Colors.purple.withOpacity(0.3),
        foregroundColor: Colors.white,
        padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Text(emoji, style: const TextStyle(fontSize: 18)),
          const SizedBox(width: 6),
          Text(label, style: const TextStyle(fontSize: 12)),
        ],
      ),
    );
  }
}
