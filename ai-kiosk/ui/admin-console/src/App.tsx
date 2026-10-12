/**
 * Admin Console (S22) — skeleton.
 *
 * Platform administration: device fleet (status, health, active version tuple,
 * sync state); release management (shadow → canary → production, rollback);
 * users/roles; audit views; KB/rules review workflows; weather staleness
 * alerts; candidate queues.
 *
 * Full module context: docs/02-modules.md §S22.
 * Invariants: admin may NOT approve agricultural content (role separation with
 * the scientist); two-person rule for production promotion; fleet shows the
 * active version tuple per device.
 */
import { useEffect, useState } from 'react'

const API_BASE = '/v1'

interface Device {
  id: string
  name: string
  status: string
  sync_state: string
  version_tuple: string
  last_seen: string
}

interface WeatherStaleAlert {
  id: string
  message: string
  created_at: string
}

export default function App() {
  const [devices, setDevices] = useState<Device[]>([])
  const [alerts, setAlerts] = useState<WeatherStaleAlert[]>([])
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    // TODO: Keycloak OIDC login (admin/auditor roles; MFA TOTP) before any data call.
    Promise.all([
      fetch(`${API_BASE}/admin/devices`).then((r) => (r.ok ? r.json() : Promise.reject(new Error(`HTTP ${r.status}`)))),
      fetch(`${API_BASE}/admin/weather-stale-alerts`).then((r) =>
        r.ok ? r.json() : Promise.reject(new Error(`HTTP ${r.status}`)),
      ),
    ])
      .then(([dev, alrt]) => {
        setDevices(dev.items as Device[])
        setAlerts(alrt.items as WeatherStaleAlert[])
      })
      .catch((e: Error) => setError(e.message))
  }, [])

  return (
    <main style={{ fontFamily: 'system-ui', margin: '2rem auto', maxWidth: 1100 }}>
      <h1>AI Kiosk — Admin Console</h1>
      <p>
        Skeleton (S22). Fleet management shows the <strong>active version tuple</strong>{' '}
        per device; releases promote <strong>shadow → canary → production</strong> under a
        two-person rule. Admins may not approve agricultural content (role separation).
      </p>
      {error && <p style={{ color: 'crimson' }}>admin APIs unreachable: {error}</p>}

      <section>
        <h2>Device fleet</h2>
        <table style={{ borderCollapse: 'collapse', width: '100%' }}>
          <thead>
            <tr>
              <th style={{ textAlign: 'left' }}>device</th>
              <th style={{ textAlign: 'left' }}>status</th>
              <th style={{ textAlign: 'left' }}>sync</th>
              <th style={{ textAlign: 'left' }}>active version tuple</th>
            </tr>
          </thead>
          <tbody>
            {devices.map((d) => (
              <tr key={d.id}>
                <td>{d.name}</td>
                <td>{d.status}</td>
                <td>{d.sync_state}</td>
                <td>
                  <code>{d.version_tuple}</code>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </section>

      <section>
        <h2>Weather staleness alerts</h2>
        <ul>
          {alerts.map((a) => (
            <li key={a.id}>{a.message}</li>
          ))}
        </ul>
      </section>
    </main>
  )
}
