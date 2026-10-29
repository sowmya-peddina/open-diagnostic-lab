import { FormEvent, useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { api, Doctor, Patient, TestDefinition } from "../api";

export default function NewOrderPage() {
  const navigate = useNavigate();
  const [patients, setPatients] = useState<Patient[]>([]);
  const [doctors, setDoctors] = useState<Doctor[]>([]);
  const [tests, setTests] = useState<TestDefinition[]>([]);
  const [q, setQ] = useState("");
  const [patientId, setPatientId] = useState<number | "">("");
  const [doctorId, setDoctorId] = useState<number | "">("");
  const [selectedTests, setSelectedTests] = useState<number[]>([]);
  const [notes, setNotes] = useState("");
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  const [newPatient, setNewPatient] = useState({
    full_name: "",
    age_years: "",
    sex: "unknown",
    phone: "",
  });

  useEffect(() => {
    Promise.all([
      api.get<Doctor[]>("/doctors"),
      api.get<TestDefinition[]>("/tests"),
    ])
      .then(([d, t]) => {
        setDoctors(d);
        setTests(t);
      })
      .catch((e) => setError(e.message));
  }, []);

  useEffect(() => {
    const t = setTimeout(() => {
      api
        .get<Patient[]>(`/patients?q=${encodeURIComponent(q)}`)
        .then(setPatients)
        .catch(() => undefined);
    }, 200);
    return () => clearTimeout(t);
  }, [q]);

  const toggleTest = (id: number) => {
    setSelectedTests((prev) =>
      prev.includes(id) ? prev.filter((x) => x !== id) : [...prev, id]
    );
  };

  const createPatient = async () => {
    if (!newPatient.full_name.trim()) {
      setError("Patient name is required");
      return;
    }
    const p = await api.post<Patient>("/patients", {
      full_name: newPatient.full_name,
      age_years: newPatient.age_years ? Number(newPatient.age_years) : null,
      sex: newPatient.sex,
      phone: newPatient.phone,
    });
    setPatients((prev) => [p, ...prev]);
    setPatientId(p.id);
    setNewPatient({ full_name: "", age_years: "", sex: "unknown", phone: "" });
  };

  const onSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setError("");
    if (!patientId) {
      setError("Select or create a patient");
      return;
    }
    if (!selectedTests.length) {
      setError("Select at least one test");
      return;
    }
    setBusy(true);
    try {
      const order = await api.post<{ id: number }>("/orders", {
        patient_id: patientId,
        doctor_id: doctorId || null,
        test_definition_ids: selectedTests,
        notes,
      });
      navigate(`/orders/${order.id}`);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to create order");
    } finally {
      setBusy(false);
    }
  };

  return (
    <div>
      <div className="page-header">
        <h1>New order</h1>
      </div>
      <form className="stack" onSubmit={onSubmit}>
        <div className="card two-col">
          <div className="stack">
            <h3>Patient</h3>
            <label>
              Search existing
              <input
                value={q}
                onChange={(e) => setQ(e.target.value)}
                placeholder="Name, code, phone…"
              />
            </label>
            <label>
              Select patient
              <select
                value={patientId}
                onChange={(e) => setPatientId(e.target.value ? Number(e.target.value) : "")}
              >
                <option value="">— Select —</option>
                {patients.map((p) => (
                  <option key={p.id} value={p.id}>
                    {p.patient_code} — {p.full_name}
                  </option>
                ))}
              </select>
            </label>
            <hr />
            <h4>Or register new</h4>
            <label>
              Full name
              <input
                value={newPatient.full_name}
                onChange={(e) => setNewPatient({ ...newPatient, full_name: e.target.value })}
              />
            </label>
            <div className="row">
              <label style={{ flex: 1 }}>
                Age (years)
                <input
                  value={newPatient.age_years}
                  onChange={(e) => setNewPatient({ ...newPatient, age_years: e.target.value })}
                />
              </label>
              <label style={{ flex: 1 }}>
                Sex
                <select
                  value={newPatient.sex}
                  onChange={(e) => setNewPatient({ ...newPatient, sex: e.target.value })}
                >
                  <option value="unknown">Unknown</option>
                  <option value="male">Male</option>
                  <option value="female">Female</option>
                  <option value="other">Other</option>
                </select>
              </label>
            </div>
            <label>
              Phone
              <input
                value={newPatient.phone}
                onChange={(e) => setNewPatient({ ...newPatient, phone: e.target.value })}
              />
            </label>
            <button type="button" className="secondary" onClick={createPatient}>
              Save patient
            </button>
          </div>

          <div className="stack">
            <h3>Referring doctor & tests</h3>
            <label>
              Referring doctor
              <select
                value={doctorId}
                onChange={(e) => setDoctorId(e.target.value ? Number(e.target.value) : "")}
              >
                <option value="">— Optional —</option>
                {doctors.map((d) => (
                  <option key={d.id} value={d.id}>
                    {d.full_name}
                    {d.specialty ? ` (${d.specialty})` : ""}
                  </option>
                ))}
              </select>
            </label>
            <div>
              <div style={{ marginBottom: 6, color: "var(--muted)" }}>Tests</div>
              <div className="checks">
                {tests.map((t) => (
                  <label key={t.id}>
                    <input
                      type="checkbox"
                      checked={selectedTests.includes(t.id)}
                      onChange={() => toggleTest(t.id)}
                    />
                    {t.code} — {t.name}
                  </label>
                ))}
              </div>
            </div>
            <label>
              Notes
              <textarea value={notes} onChange={(e) => setNotes(e.target.value)} rows={3} />
            </label>
          </div>
        </div>
        {error && <p className="error">{error}</p>}
        <div className="row">
          <button type="submit" disabled={busy}>
            {busy ? "Creating…" : "Create order"}
          </button>
        </div>
      </form>
    </div>
  );
}
