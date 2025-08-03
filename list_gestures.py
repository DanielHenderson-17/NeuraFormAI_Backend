#!/usr/bin/env python3
"""
VRM Gesture/Expression Extractor

This script loads VRM files and extracts all available blend shapes/expressions
from the VRM extensions. VRM files are essentially GLB/GLTF files with VRM-specific extensions.

Usage:
    python list_gestures.py [vrm_file_path]
    
If no file path is provided, it will analyze all VRM files in chat_ui/assets/vrms/
"""

import json
import struct
import sys
import os
from pathlib import Path
from typing import Dict, List, Optional

def read_glb_header(file_path: str) -> Dict:
    """
    Read the GLB header and extract basic information.
    GLB format: 12-byte header + JSON chunk + binary chunk
    """
    with open(file_path, 'rb') as f:
        # Read GLB header (12 bytes)
        magic = f.read(4)
        version = struct.unpack('<I', f.read(4))[0]
        length = struct.unpack('<I', f.read(4))[0]
        
        if magic != b'glTF':
            raise ValueError(f"Invalid GLB file: {file_path}")
        
        print(f"GLB Version: {version}")
        print(f"Total length: {length} bytes")
        
        return {
            'version': version,
            'length': length
        }

def extract_json_from_glb(file_path: str) -> Dict:
    """
    Extract the JSON content from a GLB file.
    """
    with open(file_path, 'rb') as f:
        # Skip GLB header (12 bytes)
        f.seek(12)
        
        # Read JSON chunk header
        json_length = struct.unpack('<I', f.read(4))[0]
        json_type = f.read(4)
        
        if json_type != b'JSON':
            raise ValueError("Invalid JSON chunk type")
        
        # Read JSON content
        json_data = f.read(json_length).decode('utf-8')
        return json.loads(json_data)

def extract_vrm_expressions(gltf_data: Dict) -> List[Dict]:
    """
    Extract blend shape groups from VRM extensions.
    """
    expressions = []
    
    # Check if VRM extension exists
    if 'extensions' not in gltf_data:
        print("No extensions found in GLTF data")
        return expressions
    
    vrm_ext = gltf_data['extensions'].get('VRM')
    if not vrm_ext:
        print("No VRM extension found")
        return expressions
    
    # Check for blendShapeMaster
    blend_shape_master = vrm_ext.get('blendShapeMaster')
    if not blend_shape_master:
        print("No blendShapeMaster found in VRM extension")
        return expressions
    
    # Extract blendShapeGroups
    blend_shape_groups = blend_shape_master.get('blendShapeGroups', [])
    
    for group in blend_shape_groups:
        expression_info = {
            'name': group.get('name', 'Unknown'),
            'presetName': group.get('presetName', 'Unknown'),
            'binds': group.get('binds', []),
            'materialValues': group.get('materialValues', []),
            'isBinary': group.get('isBinary', False)
        }
        expressions.append(expression_info)
    
    return expressions

def analyze_vrm_file(file_path: str) -> None:
    """
    Analyze a single VRM file and print all available expressions.
    """
    print(f"\n{'='*60}")
    print(f"Analyzing: {file_path}")
    print(f"{'='*60}")
    
    try:
        # Read GLB header
        header_info = read_glb_header(file_path)
        
        # Extract JSON content
        gltf_data = extract_json_from_glb(file_path)
        
        # Extract VRM expressions
        expressions = extract_vrm_expressions(gltf_data)
        
        if not expressions:
            print("❌ No expressions found in this VRM file")
            return
        
        print(f"\n✅ Found {len(expressions)} expressions/gestures:")
        print("-" * 40)
        
        for i, expr in enumerate(expressions, 1):
            print(f"{i:2d}. Name: {expr['name']}")
            print(f"    Preset: {expr['presetName']}")
            print(f"    Binary: {expr['isBinary']}")
            
            # Show blend shape binds if any
            if expr['binds']:
                print(f"    Blend Shapes: {len(expr['binds'])}")
                for bind in expr['binds'][:3]:  # Show first 3
                    mesh_name = bind.get('mesh', 'Unknown')
                    index = bind.get('index', 'Unknown')
                    weight = bind.get('weight', 1.0)
                    print(f"      - {mesh_name}[{index}]: {weight}")
                if len(expr['binds']) > 3:
                    print(f"      ... and {len(expr['binds']) - 3} more")
            
            # Show material values if any
            if expr['materialValues']:
                print(f"    Materials: {len(expr['materialValues'])}")
                for mat in expr['materialValues'][:2]:  # Show first 2
                    mat_name = mat.get('materialName', 'Unknown')
                    prop_name = mat.get('propertyName', 'Unknown')
                    print(f"      - {mat_name}.{prop_name}")
                if len(expr['materialValues']) > 2:
                    print(f"      ... and {len(expr['materialValues']) - 2} more")
            
            print()
        
        # Summary of preset names
        preset_names = [expr['presetName'] for expr in expressions if expr['presetName'] != 'Unknown']
        if preset_names:
            print("📋 Available Preset Expressions:")
            for preset in sorted(set(preset_names)):
                print(f"   • {preset}")
        
    except Exception as e:
        print(f"❌ Error analyzing {file_path}: {e}")

def main():
    """
    Main function to handle command line arguments and process VRM files.
    """
    if len(sys.argv) > 1:
        # Analyze specific file
        file_path = sys.argv[1]
        if not os.path.exists(file_path):
            print(f"❌ File not found: {file_path}")
            sys.exit(1)
        analyze_vrm_file(file_path)
    else:
        # Analyze all VRM files in the default directory
        vrm_dir = Path("chat_ui/assets/vrms")
        if not vrm_dir.exists():
            print(f"❌ VRM directory not found: {vrm_dir}")
            print("Please provide a specific VRM file path as an argument.")
            sys.exit(1)
        
        vrm_files = list(vrm_dir.glob("*.vrm"))
        if not vrm_files:
            print(f"❌ No VRM files found in {vrm_dir}")
            sys.exit(1)
        
        print(f"🔍 Found {len(vrm_files)} VRM files to analyze:")
        for vrm_file in vrm_files:
            print(f"   • {vrm_file.name}")
        
        for vrm_file in vrm_files:
            analyze_vrm_file(str(vrm_file))

if __name__ == "__main__":
    main() 