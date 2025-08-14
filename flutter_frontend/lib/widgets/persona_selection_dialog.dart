import 'package:flutter/material.dart';
import '../models/persona.dart';

class PersonaSelectionDialog extends StatelessWidget {
  final List<Map<String, dynamic>> availablePersonas;
  final Persona? currentPersona;
  final Function(String) onPersonaSelected;
  final VoidCallback onClose;

  const PersonaSelectionDialog({
    super.key,
    required this.availablePersonas,
    required this.currentPersona,
    required this.onPersonaSelected,
    required this.onClose,
  });

  @override
  Widget build(BuildContext context) {
    return Center(
      child: GestureDetector(
        onTap: () {}, // Prevent click propagation to background
        child: Container(
          width: 700,
          height: 500,
          padding: const EdgeInsets.all(20),
          decoration: BoxDecoration(
            color: const Color(0xFF2c2c2c),
            borderRadius: BorderRadius.circular(12),
            border: Border.all(color: const Color(0xFF555555)),
            boxShadow: [
              BoxShadow(
                color: Colors.black.withOpacity(0.3),
                blurRadius: 10,
                offset: const Offset(0, 5),
              ),
            ],
          ),
          child: Column(
            children: [
              // Header
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  const Text(
                    'Select NeuraPal',
                    style: TextStyle(
                      color: Colors.white,
                      fontSize: 18,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                  MouseRegion(
                    cursor: SystemMouseCursors.click,
                    child: GestureDetector(
                      onTap: onClose,
                      child: Container(
                        padding: const EdgeInsets.all(4),
                        child: const Icon(
                          Icons.close,
                          color: Colors.grey,
                          size: 20,
                        ),
                      ),
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 20),
              
              // Persona grid
              Expanded(
                child: GridView.builder(
                  gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
                    crossAxisCount: 5,
                    childAspectRatio: 1.0,
                    crossAxisSpacing: 10,
                    mainAxisSpacing: 10,
                  ),
                  itemCount: availablePersonas.length,
                  itemBuilder: (context, index) {
                    final persona = availablePersonas[index];
                    final isActive = persona['name'] == currentPersona?.name;
                    
                    return MouseRegion(
                      cursor: SystemMouseCursors.click,
                      child: GestureDetector(
                        onTap: () => onPersonaSelected(persona['name']),
                        child: Container(
                          padding: const EdgeInsets.all(6),
                          decoration: BoxDecoration(
                            color: const Color(0xFF3a3a3a),
                            borderRadius: BorderRadius.circular(8),
                            border: Border.all(
                              color: isActive ? Colors.blue : const Color(0xFF555555),
                              width: isActive ? 2 : 1,
                            ),
                            boxShadow: isActive ? [
                              BoxShadow(
                                color: Colors.blue.withOpacity(0.3),
                                blurRadius: 8,
                                spreadRadius: 2,
                              ),
                            ] : null,
                          ),
                          child: Column(
                            mainAxisAlignment: MainAxisAlignment.center,
                            children: [
                              // Avatar
                              Stack(
                                children: [
                                  Container(
                                    width: 36,
                                    height: 36,
                                    decoration: BoxDecoration(
                                      color: Colors.blue,
                                      borderRadius: BorderRadius.circular(18),
                                      border: isActive ? Border.all(
                                        color: Colors.blue,
                                        width: 3,
                                      ) : null,
                                    ),
                                    child: Center(
                                      child: Text(
                                        persona['name'][0].toUpperCase(),
                                        style: const TextStyle(
                                          color: Colors.white,
                                          fontSize: 16,
                                          fontWeight: FontWeight.bold,
                                        ),
                                      ),
                                    ),
                                  ),
                                  // Active indicator
                                  if (isActive)
                                    Positioned(
                                      bottom: 0,
                                      right: 0,
                                      child: Container(
                                        width: 14,
                                        height: 14,
                                        decoration: BoxDecoration(
                                          color: Colors.blue,
                                          borderRadius: BorderRadius.circular(7),
                                          border: Border.all(color: const Color(0xFF3a3a3a), width: 1),
                                        ),
                                        child: const Icon(
                                          Icons.check,
                                          color: Colors.white,
                                          size: 8,
                                        ),
                                      ),
                                    ),
                                ],
                              ),
                              const SizedBox(height: 4),
                              
                              // Name
                              Text(
                                persona['name'],
                                style: TextStyle(
                                  color: isActive ? Colors.blue : Colors.white,
                                  fontSize: 11,
                                  fontWeight: isActive ? FontWeight.bold : FontWeight.normal,
                                ),
                                textAlign: TextAlign.center,
                              ),
                            ],
                          ),
                        ),
                      ),
                    );
                  },
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
