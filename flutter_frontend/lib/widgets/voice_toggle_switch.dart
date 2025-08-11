import 'package:flutter/material.dart';

class VoiceToggleSwitch extends StatefulWidget {
  final bool initialValue;
  final ValueChanged<bool>? onChanged;

  const VoiceToggleSwitch({
    Key? key,
    this.initialValue = false,
    this.onChanged,
  }) : super(key: key);

  @override
  State<VoiceToggleSwitch> createState() => _VoiceToggleSwitchState();
}

class _VoiceToggleSwitchState extends State<VoiceToggleSwitch> {
  late bool _isEnabled;

  @override
  void initState() {
    super.initState();
    _isEnabled = widget.initialValue;
  }

  void _toggle() {
    setState(() {
      _isEnabled = !_isEnabled;
    });
    widget.onChanged?.call(_isEnabled);
  }

  @override
  Widget build(BuildContext context) {
    return MouseRegion(
      cursor: SystemMouseCursors.click,
      child: GestureDetector(
        onTap: _toggle,
        child: Container(
          width: 50,
          height: 24,
          decoration: BoxDecoration(
            color: _isEnabled ? const Color(0xFF6610F2) : const Color(0xFF444444),
            borderRadius: BorderRadius.circular(12),
          ),
          child: AnimatedAlign(
            duration: const Duration(milliseconds: 200),
            curve: Curves.easeInOut,
            alignment: _isEnabled ? Alignment.centerRight : Alignment.centerLeft,
            child: Container(
              width: 20,
              height: 20,
              margin: const EdgeInsets.all(2),
              decoration: const BoxDecoration(
                color: Colors.white,
                shape: BoxShape.circle,
              ),
            ),
          ),
        ),
      ),
    );
  }

  bool get isEnabled => _isEnabled;
  
  void setEnabled(bool value) {
    if (_isEnabled != value) {
      setState(() {
        _isEnabled = value;
      });
    }
  }
}
