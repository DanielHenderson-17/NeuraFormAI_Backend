// Helper functions for VRM-related logic
import 'package:flutter/material.dart';

String getPersonaNameFromModel(String modelFilename) {
  if (modelFilename.contains('fuka')) return 'Fuka';
  if (modelFilename.contains('gwen')) return 'Gwen';
  if (modelFilename.contains('kenji')) return 'Kenji';
  if (modelFilename.contains('koan')) return 'Koan';
  if (modelFilename.contains('nika')) return 'Nika';
  return modelFilename.replaceAll('.vrm', '').replaceAll('_model', '');
}

// Add more VRM-related helper functions here as needed
