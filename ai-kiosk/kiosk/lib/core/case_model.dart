/// Case-to-Solution tree mirrors (S7, case-service).
///
/// The kiosk renders a read-only view of the append-only case graph; inputs are
/// posted as typed [InputNode] instances and the resulting nodes come back from
/// core-api.
///
/// Invariants: every touch action is a typed Input node with `modality=touch`
/// and `confidence=1.0`; nodes are append-only (ULID, immutable once written);
/// farmer identity is a pseudonymous `farmer_ref`, never a name.
class InputNode {
  const InputNode({
    required this.modality,
    required this.confidence,
    required this.content,
  });

  /// `voice` | `touch` | `text` | `picture`.
  final String modality;
  final double confidence;
  final Map<String, dynamic> content;

  Map<String, dynamic> toJson() => {
        'modality': modality,
        'confidence': confidence,
        'content': content,
        // TODO: session_id / case_id attached by the repository layer at send time.
      };
}

class CaseNode {
  const CaseNode({required this.id, required this.kind, required this.createdAt});

  final String id; // ULID
  final String kind; // input | interpretation | decision | prescription | ...
  final String createdAt; // UTC ISO-8601

  factory CaseNode.fromJson(Map<String, dynamic> j) => CaseNode(
        id: j['id'] as String,
        kind: j['kind'] as String,
        createdAt: j['created_at'] as String,
      );
}

class CaseView {
  const CaseView({required this.caseId, required this.nodes});

  final String caseId;
  final List<CaseNode> nodes;

  factory CaseView.fromJson(Map<String, dynamic> j) => CaseView(
        caseId: j['case_id'] as String,
        nodes: (j['nodes'] as List)
            .map((n) => CaseNode.fromJson(n as Map<String, dynamic>))
            .toList(),
      );
}
