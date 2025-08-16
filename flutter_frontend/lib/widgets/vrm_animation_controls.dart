import 'package:flutter/material.dart';

class VRMAnimationControls extends StatelessWidget {
  final bool animationsDiscovered;
  final List<Map<String, String>> availableAnimations;
  final void Function(String animationName) onPlayAnimation;
  final VoidCallback onStopAnimation;

  const VRMAnimationControls({
    Key? key,
    required this.animationsDiscovered,
    required this.availableAnimations,
    required this.onPlayAnimation,
    required this.onStopAnimation,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Positioned(
      top: 10,
      right: 10,
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
              'Animations',
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
                if (!animationsDiscovered)
                  _buildSmallAnimationButton('⏳', 'Loading...', () {})
                else ...[
                  ...availableAnimations.map((anim) =>
                    _buildSmallAnimationButton(
                      anim['emoji']!,
                      anim['displayName']!,
                      () => onPlayAnimation(anim['name']!)
                    )
                  ).toList(),
                  if (availableAnimations.isEmpty)
                    _buildSmallAnimationButton('❌', 'No Anims', () {}),
                ],
                _buildSmallAnimationButton('⏹️', 'Stop', onStopAnimation),
              ],
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildSmallAnimationButton(String emoji, String label, VoidCallback onPressed) {
    return InkWell(
      onTap: onPressed,
      child: Container(
        padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 4),
        decoration: BoxDecoration(
          color: Colors.blue.withOpacity(0.3),
          borderRadius: BorderRadius.circular(4),
          border: Border.all(color: Colors.blue.withOpacity(0.5)),
        ),
        child: Row(
          mainAxisSize: MainAxisSize.min,
          children: [
            Text(emoji, style: const TextStyle(fontSize: 12)),
            const SizedBox(width: 4),
            Text(
              label,
              style: const TextStyle(
                fontSize: 10,
                color: Colors.white,
              ),
            ),
          ],
        ),
      ),
    );
  }
}
