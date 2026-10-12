import 'package:flutter/material.dart';

import '../../widgets/no_dead_end_actions.dart';

/// Touch guided flow (S1): pickers, quick replies, confirmation gates.
///
/// Every touch action is a typed Input node (`modality=touch`, `confidence=1.0`):
/// TODO: POST to `POST /v1/inputs/touch` (via core-api S4 → S7 case-service).
///
/// KVK Banavasi (Kurnool, AP) crops: cotton, paddy, groundnut, maize, arhar,
/// castor, millets, chilli.
class TouchScreen extends StatelessWidget {
  const TouchScreen({super.key});

  static const crops = [
    'పత్తి / Cotton',
    'వరి / Paddy',
    'వేరుశనగ / Groundnut',
    'మొక్కజొన్న / Maize',
    'కందులు / Arhar',
    'ఆముదం / Castor',
    'చిరుధాన్యాలు / Millets',
    'మిరప / Chilli',
  ];

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('ఎంచుకోండి / Touch')),
      body: ListView(
        padding: const EdgeInsets.all(16),
        children: [
          for (final crop in crops)
            Card(
              child: ListTile(
                title: Text(crop),
                // TODO: onTap → POST /v1/inputs/touch (modality=touch, confidence 1.0).
                onTap: () {},
              ),
            ),
          const SizedBox(height: 16),
          const NoDeadEndActions(),
        ],
      ),
    );
  }
}
