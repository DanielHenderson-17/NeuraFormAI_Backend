import 'package:flutter/material.dart';

/// A reusable loading overlay that covers the VRM container during VRM loading
/// Used when loading initial VRM, swapping VRMs, or waiting for animations to start
class VRMLoadingOverlay extends StatelessWidget {
  final bool isVisible;
  final String? loadingText;
  final Color? backgroundColor;
  final Color? textColor;
  
  const VRMLoadingOverlay({
    Key? key,
    required this.isVisible,
    this.loadingText,
    this.backgroundColor,
    this.textColor,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    if (!isVisible) {
      return const SizedBox.shrink();
    }

    return Container(
      width: double.infinity,
      height: double.infinity,
      color: backgroundColor ?? const Color(0xFF1e1e1e),
      child: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            // Loading spinner
            SizedBox(
              width: 60,
              height: 60,
              child: CircularProgressIndicator(
                strokeWidth: 4,
                valueColor: AlwaysStoppedAnimation<Color>(
                  textColor ?? Colors.white,
                ),
              ),
            ),
            const SizedBox(height: 24),
            // Loading text
            Text(
              loadingText ?? 'Loading...',
              style: TextStyle(
                fontSize: 18,
                fontWeight: FontWeight.w500,
                color: textColor ?? Colors.white,
              ),
            ),
            const SizedBox(height: 8),
            // Subtitle
            Text(
              'Preparing VRM model',
              style: TextStyle(
                fontSize: 14,
                color: (textColor ?? Colors.white).withOpacity(0.7),
              ),
            ),
          ],
        ),
      ),
    );
  }
}

/// A loading overlay specifically designed for VRM operations with animation
class VRMLoadingOverlayAnimated extends StatefulWidget {
  final bool isVisible;
  final String? loadingText;
  final Color? backgroundColor;
  final Color? textColor;
  final Duration fadeDuration;
  
  const VRMLoadingOverlayAnimated({
    Key? key,
    required this.isVisible,
    this.loadingText,
    this.backgroundColor,
    this.textColor,
    this.fadeDuration = const Duration(milliseconds: 500),
  }) : super(key: key);

  @override
  State<VRMLoadingOverlayAnimated> createState() => _VRMLoadingOverlayAnimatedState();
}

class _VRMLoadingOverlayAnimatedState extends State<VRMLoadingOverlayAnimated>
    with SingleTickerProviderStateMixin {
  late AnimationController _controller;
  late Animation<double> _fadeAnimation;

  @override
  void initState() {
    super.initState();
    _controller = AnimationController(
      duration: widget.fadeDuration,
      vsync: this,
    );
    _fadeAnimation = Tween<double>(
      begin: 0.0,
      end: 1.0,
    ).animate(CurvedAnimation(
      parent: _controller,
      curve: Curves.easeInOut,
    ));

    if (widget.isVisible) {
      _controller.forward();
    }
  }

  @override
  void didUpdateWidget(VRMLoadingOverlayAnimated oldWidget) {
    super.didUpdateWidget(oldWidget);
    if (widget.isVisible != oldWidget.isVisible) {
      if (widget.isVisible) {
        _controller.forward();
      } else {
        _controller.reverse();
      }
    }
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return AnimatedBuilder(
      animation: _fadeAnimation,
      builder: (context, child) {
        if (_fadeAnimation.value == 0.0 && !widget.isVisible) {
          return const SizedBox.shrink();
        }

        return Opacity(
          opacity: _fadeAnimation.value,
          child: VRMLoadingOverlay(
            isVisible: true,
            loadingText: widget.loadingText,
            backgroundColor: widget.backgroundColor,
            textColor: widget.textColor,
          ),
        );
      },
    );
  }
}
