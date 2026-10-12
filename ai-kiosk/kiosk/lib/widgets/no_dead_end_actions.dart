import 'package:flutter/material.dart';

/// S1 invariant: **no dead ends** — every screen offers "talk to an expert",
/// "print what I have", and "start over", so a farmer is never stuck.
class NoDeadEndActions extends StatelessWidget {
  const NoDeadEndActions({super.key});

  @override
  Widget build(BuildContext context) {
    return Row(
      mainAxisAlignment: MainAxisAlignment.spaceEvenly,
      children: [
        TextButton(onPressed: () {}, child: const Text('నిపుణుడితో మాట్లాడండి\nTalk to expert')),
        TextButton(onPressed: () {}, child: const Text('ప్రింట్ చేయండి\nPrint')),
        TextButton(onPressed: () {}, child: const Text('మళ్ళీ ప్రారంభం\nStart over')),
      ],
    );
  }
}
