import 'dart:convert';

import 'package:http/http.dart' as http;

/// Session lifecycle (S1).
///
/// The kiosk session is **consent-gated** (DPDP): no case may be created until
/// the farmer records consent. `POST /v1/session` returns a `session_id` and a
/// ULID `case_id` scoped to a pseudonymous `farmer_ref` (never a name).
///
/// Timeout/reset clears local state only — the server keeps the immutable,
/// append-only case graph.
class Session {
  Session({this.sessionId, this.caseId, this.farmerRef});

  final String? sessionId;
  final String? caseId;
  final String? farmerRef;

  bool get active => sessionId != null;

  /// Starts a session; requires [consent] to be true.
  static Future<Session> start({
    required bool consent,
    String apiBase = 'http://localhost:8000',
  }) async {
    if (!consent) {
      throw StateError('Consent is required to start a session (DPDP).');
    }
    final resp = await http.post(
      Uri.parse('$apiBase/v1/session'),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({'consent': true}),
    );
    if (resp.statusCode != 201) {
      throw StateError('Session start failed: HTTP ${resp.statusCode}');
    }
    final body = jsonDecode(resp.body) as Map<String, dynamic>;
    return Session(
      sessionId: body['session_id'] as String?,
      caseId: body['case_id'] as String?,
      farmerRef: body['farmer_ref'] as String?,
    );
  }

  /// Clears local session state (timeout/reset). Server state is untouched.
  void reset() {}
}
