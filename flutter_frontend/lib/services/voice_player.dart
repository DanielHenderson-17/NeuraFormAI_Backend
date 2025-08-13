import 'dart:typed_data';
import 'dart:io';
import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:audioplayers/audioplayers.dart';
import 'package:path_provider/path_provider.dart';
import 'auth_service.dart';

class VoicePlayer {
  static bool _isInitialized = false;
  static AudioPlayer? _audioPlayer;

  static Future<void> initialize() async {
    if (!_isInitialized) {
      _audioPlayer = AudioPlayer();
      _isInitialized = true;
      print("🔊 VoicePlayer initialized");
    }
  }

  /// Request ElevenLabs stream from backend and play it - matches Python implementation
  static Future<double?> playReplyFromBackend(String text, {bool voiceEnabled = true, Function(double?)? onStart}) async {
    if (!voiceEnabled) {
      print("🔇 [VoicePlayer] Voice disabled — skipping playback");
      return null;
    }

    if (!_isInitialized) {
      await initialize();
    }

    try {
      print("🎤 [VoicePlayer] Sending TTS for reply...");

      final userId = AuthService.userId;
      if (userId == null) {
        print("❌ [VoicePlayer] No user ID available");
        return null;
      }

      final url = "http://localhost:8000/chat/speak-from-text";
      final payload = {
        "user_id": userId,
        "reply": text
      };
      print("📨 [VoicePlayer] Payload: $payload");

      final response = await http.post(
        Uri.parse(url),
        headers: {
          'Content-Type': 'application/json',
          'Authorization': 'Bearer ${AuthService.sessionToken}',
        },
        body: json.encode(payload),
      );

      if (response.statusCode == 200) {
        print("✅ [VoicePlayer] Received TTS stream...");
        print("📦 [VoicePlayer] Buffer size: ${response.bodyBytes.length}");

        // Save audio to temporary file (required for audioplayers on desktop)
        final tempDir = await getTemporaryDirectory();
        final tempFile = File('${tempDir.path}/tts_audio_${DateTime.now().millisecondsSinceEpoch}.mp3');
        await tempFile.writeAsBytes(response.bodyBytes);

        // Get EXACT audio duration from MP3 metadata - EXACT match to Python implementation
        // In Python: audio_duration_seconds = len(audio) / 1000.0  # Convert ms to seconds
        double audioDurationSeconds;
        try {
          await _audioPlayer!.setSource(DeviceFileSource(tempFile.path));
          final duration = await _audioPlayer!.getDuration();
          if (duration != null) {
            audioDurationSeconds = duration.inMilliseconds / 1000.0; // EXACT Python conversion
            print("🎧 [VoicePlayer] EXACT MP3 Duration: ${audioDurationSeconds.toStringAsFixed(2)}s | Bytes: ${response.bodyBytes.length}");
          } else {
            // Fallback to estimation if duration reading fails
            audioDurationSeconds = response.bodyBytes.length / 16000.0;
            print("🎧 [VoicePlayer] Fallback Duration Estimate: ${audioDurationSeconds.toStringAsFixed(2)}s | Bytes: ${response.bodyBytes.length}");
          }
        } catch (e) {
          // Fallback to estimation if metadata reading fails
          audioDurationSeconds = response.bodyBytes.length / 16000.0;
          print("⚠️ [VoicePlayer] Failed to read MP3 duration, using estimate: ${audioDurationSeconds.toStringAsFixed(2)}s | Error: $e");
        }

        if (onStart != null) {
          onStart(audioDurationSeconds); // Pass duration to callback
        }

        print("🔊 [VoicePlayer] Playing audio now...");
        await _audioPlayer!.play(DeviceFileSource(tempFile.path));

        // Wait for playback to complete
        await _audioPlayer!.onPlayerComplete.first;
        print("✅ [VoicePlayer] Playback finished");

        // Clean up temp file
        try {
          await tempFile.delete();
        } catch (e) {
          print("⚠️ [VoicePlayer] Could not delete temp file: $e");
        }

        return audioDurationSeconds;
      } else {
        print("❌ [VoicePlayer] HTTP ${response.statusCode}: ${response.body}");
        return null;
      }
    } catch (e) {
      print("❌ Voice playback error: $e");
      return null;
    }
  }

  static void dispose() {
    _audioPlayer?.dispose();
    _audioPlayer = null;
    _isInitialized = false;
    print("🔊 VoicePlayer disposed");
  }
}
