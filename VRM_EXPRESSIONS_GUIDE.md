# VRM Expression System Guide

## Overview

We've successfully analyzed your VRM models and implemented a comprehensive expression system that goes far beyond just blinking. All your VRM models contain **14 different expressions** that can be used to create more dynamic and engaging character interactions.

## Available Expressions

### 🎭 Emotional Expressions

- **Joy** - Happy/smiling expression
- **Angry** - Angry/frowning expression
- **Fun** - Fun/amused expression
- **Sorrow** - Sad/sorrowful expression
- **Surprised** - Surprised/shocked expression

### 👄 Lip Sync Expressions (for speech)

- **A** - Mouth open for "ah" sound
- **I** - Mouth shape for "ee" sound
- **U** - Mouth shape for "oo" sound
- **E** - Mouth shape for "eh" sound
- **O** - Mouth shape for "oh" sound

### 👁️ Eye Expressions

- **Blink** - Both eyes blink
- **Blink_L** - Left eye blink only
- **Blink_R** - Right eye blink only

### 😐 Base Expression

- **Neutral** - Default/resting expression

## Files Created/Modified

### 1. `list_gestures.py`

A Python script that analyzes VRM files and extracts all available expressions:

```bash
python list_gestures.py                    # Analyze all VRM files
python list_gestures.py my_model.vrm       # Analyze specific file
```

### 2. Enhanced VRM Viewer (`chat_ui/assets/vrm_viewer/app.js`)

Added new JavaScript functions for expression control:

- `window.setExpression(expressionName, weight)` - Set any expression
- `window.setEmotion(emotion)` - Set emotional expressions
- `window.setLipSync(phoneme)` - Set lip sync for speech
- `window.clearLipSync()` - Clear lip sync expressions
- `window.resetExpressions()` - Reset to neutral
- `window.getAvailableExpressions()` - Get list of expressions

### 3. Enhanced VRMWebView (`chat_ui/center/vrm_webview.py`)

Added Python methods to control expressions:

- `set_expression(expression_name, weight)`
- `set_emotion(emotion)`
- `set_lip_sync(phoneme)`
- `clear_lip_sync()`
- `reset_expressions()`
- `get_available_expressions()`

### 4. Test Applications

- `test_expressions.py` - Basic expression testing interface
- `demo_expressions.py` - Advanced demo with chat simulation

## Usage Examples

### Basic Expression Control

```python
from chat_ui.center.vrm_webview import VRMWebView

vrm_viewer = VRMWebView()

# Set emotional expressions
vrm_viewer.set_emotion("joy")      # Happy
vrm_viewer.set_emotion("angry")    # Angry
vrm_viewer.set_emotion("fun")      # Amused
vrm_viewer.set_emotion("sorrow")   # Sad
vrm_viewer.set_emotion("surprised") # Shocked

# Set specific expressions with custom weights
vrm_viewer.set_expression("joy", 0.5)  # Half intensity joy
vrm_viewer.set_expression("angry", 1.0) # Full intensity angry

# Lip sync for speech
vrm_viewer.set_lip_sync("a")  # "Ah" sound
vrm_viewer.set_lip_sync("i")  # "Ee" sound
vrm_viewer.set_lip_sync("u")  # "Oo" sound
vrm_viewer.set_lip_sync("e")  # "Eh" sound
vrm_viewer.set_lip_sync("o")  # "Oh" sound

# Clear lip sync when done speaking
vrm_viewer.clear_lip_sync()

# Reset to neutral
vrm_viewer.reset_expressions()
```

### Chat Integration Example

```python
def handle_chat_message(message):
    """Handle chat messages and set appropriate expressions"""
    message_lower = message.lower()

    # Detect emotion from message content
    if any(word in message_lower for word in ['happy', 'joy', 'great', 'love']):
        vrm_viewer.set_emotion("joy")
    elif any(word in message_lower for word in ['angry', 'mad', 'hate']):
        vrm_viewer.set_emotion("angry")
    elif any(word in message_lower for word in ['fun', 'funny', 'lol']):
        vrm_viewer.set_emotion("fun")
    elif any(word in message_lower for word in ['sad', 'sorry', 'unfortunate']):
        vrm_viewer.set_emotion("sorrow")
    elif any(word in message_lower for word in ['wow', 'omg', 'surprised']):
        vrm_viewer.set_emotion("surprised")
    else:
        vrm_viewer.set_emotion("neutral")

    # Simulate speaking with lip sync
    simulate_speaking()

def simulate_speaking():
    """Simulate speaking with lip sync sequence"""
    phonemes = ['a', 'i', 'u', 'e', 'o']

    def speak_sequence(index=0):
        if index < len(phonemes):
            vrm_viewer.set_lip_sync(phonemes[index])
            QTimer.singleShot(200, lambda: speak_sequence(index + 1))
        else:
            QTimer.singleShot(500, vrm_viewer.clear_lip_sync)

    speak_sequence()
```

## Integration with Your Chat System

To integrate these expressions into your existing chat system:

1. **Import the enhanced VRMWebView**:

   ```python
   from chat_ui.center.vrm_webview import VRMWebView
   ```

2. **Use the expression methods** in your chat handlers:

   ```python
   # In your chat response handler
   def on_chat_response(response_text, emotion=None):
       if emotion:
           self.vrm_viewer.set_emotion(emotion)

       # Add lip sync during speech
       self.simulate_speech_lip_sync()
   ```

3. **Add emotion detection** to your chat processing:
   ```python
   def detect_emotion_from_text(text):
       # Add your emotion detection logic here
       # Return: 'joy', 'angry', 'fun', 'sorrow', 'surprised', or 'neutral'
       pass
   ```

## Testing the System

### Run the Basic Test

```bash
python test_expressions.py
```

### Run the Advanced Demo

```bash
python demo_expressions.py
```

The demo includes:

- Model selection
- Manual expression controls
- Chat simulation with emotion detection
- Lip sync demonstrations
- Utility functions

## Technical Details

### VRM File Structure

VRM files are GLB/GLTF files with VRM extensions. The expressions are stored in:

```
extensions.VRM.blendShapeMaster.blendShapeGroups[]
```

Each blend shape group contains:

- `name`: Expression name
- `presetName`: Standard VRM preset name
- `binds`: Blend shape bindings
- `materialValues`: Material property changes
- `isBinary`: Whether it's a binary expression

### Expression Weights

All expressions use weights from 0.0 to 1.0:

- `0.0` = Expression completely off
- `1.0` = Expression fully applied
- Values in between = Partial expression

### Performance Considerations

- Expressions are GPU-accelerated and very efficient
- Multiple expressions can be active simultaneously
- Lip sync expressions should be cleared after speech
- Emotional expressions can be left active for longer periods

## Next Steps

1. **Integrate with your chat system** - Add emotion detection and expression triggering
2. **Add more sophisticated lip sync** - Map phonemes to actual speech audio
3. **Create expression sequences** - Combine multiple expressions for complex animations
4. **Add expression blending** - Smooth transitions between expressions
5. **Implement personality-based expressions** - Different characters react differently

## Troubleshooting

### Common Issues

1. **Expressions not working**: Make sure the VRM model is fully loaded
2. **Lip sync not visible**: Check that lip sync expressions are being cleared properly
3. **Performance issues**: Limit the number of simultaneous expressions
4. **Expression conflicts**: Use `reset_expressions()` before setting new ones

### Debug Commands

```python
# Check available expressions
vrm_viewer.get_available_expressions()

# Reset to neutral state
vrm_viewer.reset_expressions()

# Check if VRM is loaded
# (Look for "Available expressions:" in console output)
```

This expression system provides a solid foundation for creating dynamic, expressive VRM characters that can react to chat content and provide more engaging user interactions!
