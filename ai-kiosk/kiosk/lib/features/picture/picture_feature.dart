import 'package:flutter/material.dart';

import '../../widgets/no_dead_end_actions.dart';

/// Camera capture (S1). Framing guidance; do-not-repeat memory is enforced in
/// the UI (the same image view is never requested twice within a media set).
///
/// TODO: capture via the `camera` package → `POST /v1/inputs/picture` (via
/// core-api S4 → S6 image-service: quality gate → VLM observations → ViT
/// classifier). Observations are capped at confidence 0.6 at the API boundary.
class PictureScreen extends StatelessWidget {
  const PictureScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('ఫోటో పంపండి / Picture')),
      body: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            const Icon(Icons.photo_camera, size: 96),
            const SizedBox(height: 24),
            // TODO: camera preview + framing guidance; on capture, POST /v1/inputs/picture.
            FilledButton.icon(
              onPressed: () {},
              icon: const Icon(Icons.camera),
              label: const Text('ఫోటో తీయండి / Take photo'),
            ),
            const SizedBox(height: 24),
            const NoDeadEndActions(),
          ],
        ),
      ),
    );
  }
}
