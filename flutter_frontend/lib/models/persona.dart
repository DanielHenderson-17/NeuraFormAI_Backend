class Persona {
  final String id;
  final String name;
  final String description;
  final String vrmModel;
  final String greeting;
  final Map<String, dynamic> personality;
  final Map<String, dynamic> expressions;
  final Map<String, dynamic> gestures;
  final Map<String, dynamic> metadata;
  
  Persona({
    required this.id,
    required this.name,
    required this.description,
    required this.vrmModel,
    required this.greeting,
    required this.personality,
    required this.expressions,
    required this.gestures,
    required this.metadata,
  });
  
  factory Persona.fromJson(Map<String, dynamic> json) {
    return Persona(
      id: json['id']?.toString() ?? '',
      name: json['name']?.toString() ?? 'Unknown',
      description: json['description']?.toString() ?? '',
      vrmModel: json['vrm_model']?.toString() ?? '',
      greeting: json['greeting']?.toString() ?? '',
      personality: Map<String, dynamic>.from(json['personality'] ?? {}),
      expressions: Map<String, dynamic>.from(json['expressions'] ?? {}),
      gestures: Map<String, dynamic>.from(json['gestures'] ?? {}),
      metadata: Map<String, dynamic>.from(json['metadata'] ?? {}),
    );
  }
  
  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'name': name,
      'description': description,
      'vrm_model': vrmModel,
      'greeting': greeting,
      'personality': personality,
      'expressions': expressions,
      'gestures': gestures,
      'metadata': metadata,
    };
  }
  
  Persona copyWith({
    String? id,
    String? name,
    String? description,
    String? vrmModel,
    String? greeting,
    Map<String, dynamic>? personality,
    Map<String, dynamic>? expressions,
    Map<String, dynamic>? gestures,
    Map<String, dynamic>? metadata,
  }) {
    return Persona(
      id: id ?? this.id,
      name: name ?? this.name,
      description: description ?? this.description,
      vrmModel: vrmModel ?? this.vrmModel,
      greeting: greeting ?? this.greeting,
      personality: personality ?? this.personality,
      expressions: expressions ?? this.expressions,
      gestures: gestures ?? this.gestures,
      metadata: metadata ?? this.metadata,
    );
  }
}
