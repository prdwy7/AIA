import 'package:flutter/material.dart';

import '../../widgets/no_dead_end_actions.dart';

/// Voice capture (S1). Mic array → 16 kHz WAV; TTS playback of confirmations.
///
/// TODO: capture via the `record` package → `POST /v1/inputs/voice` (via core-api
/// S4 → S5 speech-service). Primary ASR: `whisper-large-v3-vaani-telugu`;
/// fast fallback: `SraVaani-1.0`. Below the ASR confidence threshold, a
/// confirmation gate re-asks the farmer.
///
/// No dead ends (§S1) — "talk to an expert", "print", "start over".
class VoiceScreen extends StatelessWidget {
  const VoiceScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('మాట్లాడండి / Voice')),
      body: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            const Icon(Icons.mic, size: 96),
            const SizedBox(height: 24),
            // TODO: record → stop → POST /v1/inputs/voice.
            FilledButton.icon(
              onPressed: () {},
              icon: const Icon(Icons.mic),
              label: const Text('రికార్డ్ చేయండి / Record'),
            ),
            const SizedBox(height: 24),
            const NoDeadEndActions(),
          ],
        ),
      ),
    );
  }
}
