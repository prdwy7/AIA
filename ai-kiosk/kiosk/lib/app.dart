import 'package:flutter/material.dart';

import 'core/session.dart';
import 'features/picture/picture_feature.dart';
import 'features/print/print_feature.dart';
import 'features/text/text_feature.dart';
import 'features/touch/touch_feature.dart';
import 'features/voice/voice_feature.dart';

/// AI Kiosk — farmer-facing home screen (S1, channel-adapter-kiosk).
///
/// Five inputs are first-class: 🎤 voice, 👆 touch, ⌨️ text, 📷 picture, plus a
/// 🖨️ print action. Telugu-first labels with an English gloss. Serves KVK
/// Banavasi, Kurnool district, AP (crops: cotton, paddy, groundnut, maize,
/// arhar, castor, millets, chilli).
///
/// No dead ends: every journey ends in "talk to an expert", "print what I have",
/// or "start over". See docs/02-modules.md §S1.
class AiKioskApp extends StatelessWidget {
  const AiKioskApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'సాగు సహాయం / AI Kiosk',
      theme: ThemeData(colorSchemeSeed: Colors.green, useMaterial3: true),
      home: const HomeScreen(),
    );
  }
}

class HomeScreen extends StatefulWidget {
  const HomeScreen({super.key});

  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  Session? _session;

  /// Consent gate (DPDP) — a case may not begin until consent is recorded.
  Future<void> _startSession() async {
    final consented = await showDialog<bool>(
      context: context,
      builder: (ctx) => AlertDialog(
        title: const Text('అనుమతి / Consent'),
        content: const Text(
          'మీ వివరాలు సురక్షితంగా నిల్వ చేయబడతాయి. కొనసాగించడానికి అనుమతించండి.\n'
          'Your details are stored securely. (DPDP consent)',
        ),
        actions: [
          TextButton(onPressed: () => Navigator.pop(ctx, false), child: const Text('వద్దు / No')),
          TextButton(onPressed: () => Navigator.pop(ctx, true), child: const Text('అవును / Yes')),
        ],
      ),
    );
    if (consented != true) return;
    final s = await Session.start(consent: consented);
    if (!mounted) return;
    setState(() => _session = s);
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('సాగు సహాయం / AI Kiosk')),
      body: Padding(
        padding: const EdgeInsets.all(24),
        child: Column(
          children: [
            const Text(
              'KVK బనవాసి — కర్నూలు జిల్లా · KVK Banavasi, Kurnool',
              style: TextStyle(fontWeight: FontWeight.w600),
            ),
            const SizedBox(height: 16),
            Expanded(
              child: GridView.count(
                crossAxisCount: 2,
                mainAxisSpacing: 16,
                crossAxisSpacing: 16,
                children: [
                  _ModButton(
                    emoji: '🎤',
                    label: 'మాట్లాడండి\nVoice',
                    color: Colors.teal,
                    onTap: () => _open(const VoiceScreen()),
                  ),
                  _ModButton(
                    emoji: '👆',
                    label: 'ఎంచుకోండి\nTouch',
                    color: Colors.indigo,
                    onTap: () => _open(const TouchScreen()),
                  ),
                  _ModButton(
                    emoji: '⌨️',
                    label: 'టైప్ చేయండి\nText',
                    color: Colors.blue,
                    onTap: () => _open(const TextScreen()),
                  ),
                  _ModButton(
                    emoji: '📷',
                    label: 'ఫోటో పంపండి\nPicture',
                    color: Colors.orange,
                    onTap: () => _open(const PictureScreen()),
                  ),
                  _ModButton(
                    emoji: '🖨️',
                    label: 'ప్రింట్ చేయండి\nPrint',
                    color: Colors.brown,
                    onTap: () => _open(const PrintScreen()),
                  ),
                ],
              ),
            ),
            const SizedBox(height: 16),
            if (_session == null)
              FilledButton(onPressed: _startSession, child: const Text('ప్రారంభించండి / Start (consent)'))
            else
              TextButton(
                onPressed: () => setState(() => _session = null),
                child: const Text('మళ్ళీ ప్రారంభించండి / Start over'),
              ),
          ],
        ),
      ),
    );
  }

  void _open(Widget screen) {
    Navigator.of(context).push(MaterialPageRoute(builder: (_) => screen));
  }
}

class _ModButton extends StatelessWidget {
  const _ModButton({
    required this.emoji,
    required this.label,
    required this.color,
    required this.onTap,
  });

  final String emoji;
  final String label;
  final Color color;
  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) {
    return Material(
      color: color.withOpacity(0.15),
      borderRadius: BorderRadius.circular(16),
      child: InkWell(
        onTap: onTap,
        borderRadius: BorderRadius.circular(16),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Text(emoji, style: const TextStyle(fontSize: 40)),
            const SizedBox(height: 8),
            Text(
              label,
              textAlign: TextAlign.center,
              style: const TextStyle(fontSize: 16, fontWeight: FontWeight.w600),
            ),
          ],
        ),
      ),
    );
  }
}
