import 'package:flutter/material.dart';

import '../../widgets/no_dead_end_actions.dart';

/// Print UI (S1). ESC/POS thermal printer via `esc_pos_printer` / `usb_serial`.
///
/// TODO: request `POST /v1/prescriptions/{id}/print` (S12 prescription-service).
/// Print jobs are idempotent (`print_id`) — a printer failure never duplicates
/// a prescription.
class PrintScreen extends StatelessWidget {
  const PrintScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('ప్రింట్ చేయండి / Print')),
      body: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            const Icon(Icons.print, size: 96),
            const SizedBox(height: 24),
            // TODO: list printable locked prescriptions; print via esc_pos_printer.
            FilledButton.icon(
              onPressed: () {},
              icon: const Icon(Icons.print),
              label: const Text('ప్రింట్ చేయండి / Print'),
            ),
            const SizedBox(height: 24),
            const NoDeadEndActions(),
          ],
        ),
      ),
    );
  }
}
