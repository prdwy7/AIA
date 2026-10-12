import 'package:flutter/material.dart';

import '../../widgets/no_dead_end_actions.dart';

/// Text input (S1). Telugu script + Latin keyboard.
///
/// TODO: on send, POST `{ modality: 'text', confidence: 1.0, content: {text} }`
/// to `POST /v1/inputs/text` (via core-api S4 → text normalizer).
class TextScreen extends StatefulWidget {
  const TextScreen({super.key});

  @override
  State<TextScreen> createState() => _TextScreenState();
}

class _TextScreenState extends State<TextScreen> {
  final _controller = TextEditingController();

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('టైప్ చేయండి / Text')),
      body: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          children: [
            TextField(
              controller: _controller,
              maxLines: 4,
              decoration: const InputDecoration(
                border: OutlineInputBorder(),
                hintText: 'మీ సమస్యను వివరించండి / Describe your problem',
              ),
            ),
            const SizedBox(height: 16),
            // TODO: on send, POST /v1/inputs/text (modality=text, confidence 1.0).
            FilledButton(onPressed: () {}, child: const Text('పంపండి / Send')),
            const Spacer(),
            const NoDeadEndActions(),
          ],
        ),
      ),
    );
  }
}
