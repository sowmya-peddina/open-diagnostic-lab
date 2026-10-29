import { FormEvent, useEffect, useState } from "react";
import { Navigate } from "react-router-dom";
import { api, ClinicSettings, Doctor, TestDefinition, User } from "../api";
import { useAuth } from "../auth";

export default function AdminPage() {
  const { user } = useAuth();
  const [doctors, setDoctors] = useState<Doctor[]>([]);
  const [tests, setTests] = useState<TestDefinition[]>([]);
  const [users, setUsers] = useState<User[]>([]);
  const [clinic, setClinic] = useState<ClinicSettings | null>(null);
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");

  const [doctorForm, setDoctorForm] = useState({ full_name: "", specialty: "", phone: "" });
  const [userForm, setUserForm] = useState({
    username: "",
    password: "",
    full_name: "",
    role: "staff",
  });
  const [testForm, setTestForm] = useState({
    code: "",
    name: "",
    sample_type: "Blood",
    param_code: "",
    param_name: "",
    unit: "",
    reference_text: "",
    reference_min: "",
    reference_max: "",
  });

  const reload = async () => {
    const [d, t, u, c] = await Promise.all([
      api.get<Doctor[]>("/doctors?active_only=false"),
      api.get<TestDefinition[]>("/tests?active_only=false"),
      api.get<User[]>("/users"),
      api.get<ClinicSettings>("/settings/clinic"),
    ]);
    setDoctors(d);
    setTests(t);
    setUsers(u);
    setClinic(c);
  };

  useEffect(() => {
    if (user?.role !== "admin") return;
    reload().catch((e) => setError(e.message));
  }, [user]);

  if (user?.role !== "admin") return <Navigate to="/" replace />;

  const addDoctor = async (e: FormEvent) => {
    e.preventDefault();
    try {
      await api.post("/doctors", { ...doctorForm, is_active: true });
      setDoctorForm({ full_name: "", specialty: "", phone: "" });
      setMessage("Doctor added.");
      await reload();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed");
    }
  };

  const addUser = async (e: FormEvent) => {
    e.preventDefault();
    try {
      await api.post("/users", userForm);
      setUserForm({ username: "", password: "", full_name: "", role: "staff" });
      setMessage("Staff user created.");
      await reload();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed");
    }
  };

  const saveClinic = async (e: FormEvent) => {
    e.preventDefault();
    if (!clinic) return;
    try {
      const updated = await api.put<ClinicSettings>("/settings/clinic", clinic);
      setClinic(updated);
      setMessage("Clinic settings saved.");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed");
    }
  };

  const addTest = async (e: FormEvent) => {
    e.preventDefault();
    try {
      await api.post("/tests", {
        code: testForm.code,
        name: testForm.name,
        sample_type: testForm.sample_type,
        parameters: [
          {
            code: testForm.param_code || testForm.code,
            name: testForm.param_name || testForm.name,
            unit: testForm.unit,
            reference_text: testForm.reference_text,
            reference_min: testForm.reference_min ? Number(testForm.reference_min) : null,
            reference_max: testForm.reference_max ? Number(testForm.reference_max) : null,
            sort_order: 1,
          },
        ],
      });
      setTestForm({
        code: "",
        name: "",
        sample_type: "Blood",
        param_code: "",
        param_name: "",
        unit: "",
        reference_text: "",
        reference_min: "",
        reference_max: "",
      });
      setMessage("Test added to catalog.");
      await reload();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed");
    }
  };

  return (
    <div className="stack">
      <div className="page-header">
        <h1>Admin</h1>
      </div>
      {error && <p className="error">{error}</p>}
      {message && <p className="ok">{message}</p>}

      <form className="card form-grid" onSubmit={saveClinic}>
        <h3>Clinic branding (reports)</h3>
        {clinic && (
          <>
            <label>
              Clinic name
              <input
                value={clinic.clinic_name}
                onChange={(e) => setClinic({ ...clinic, clinic_name: e.target.value })}
              />
            </label>
            <label>
              Address
              <textarea
                value={clinic.address}
                onChange={(e) => setClinic({ ...clinic, address: e.target.value })}
                rows={2}
              />
            </label>
            <label>
              Phone
              <input
                value={clinic.phone}
                onChange={(e) => setClinic({ ...clinic, phone: e.target.value })}
              />
            </label>
            <label>
              Report footer
              <textarea
                value={clinic.footer}
                onChange={(e) => setClinic({ ...clinic, footer: e.target.value })}
                rows={2}
              />
            </label>
            <button type="submit">Save clinic settings</button>
          </>
        )}
      </form>

      <div className="two-col">
        <form className="card form-grid" onSubmit={addDoctor}>
          <h3>Add referring doctor</h3>
          <label>
            Full name
            <input
              value={doctorForm.full_name}
              onChange={(e) => setDoctorForm({ ...doctorForm, full_name: e.target.value })}
              required
            />
          </label>
          <label>
            Specialty
            <input
              value={doctorForm.specialty}
              onChange={(e) => setDoctorForm({ ...doctorForm, specialty: e.target.value })}
            />
          </label>
          <label>
            Phone
            <input
              value={doctorForm.phone}
              onChange={(e) => setDoctorForm({ ...doctorForm, phone: e.target.value })}
            />
          </label>
          <button type="submit">Add doctor</button>
          <ul>
            {doctors.map((d) => (
              <li key={d.id}>
                {d.full_name} {d.specialty ? `— ${d.specialty}` : ""} {!d.is_active && "(inactive)"}
              </li>
            ))}
          </ul>
        </form>

        <form className="card form-grid" onSubmit={addUser}>
          <h3>Add staff user</h3>
          <label>
            Username
            <input
              value={userForm.username}
              onChange={(e) => setUserForm({ ...userForm, username: e.target.value })}
              required
            />
          </label>
          <label>
            Full name
            <input
              value={userForm.full_name}
              onChange={(e) => setUserForm({ ...userForm, full_name: e.target.value })}
            />
          </label>
          <label>
            Password
            <input
              type="password"
              value={userForm.password}
              onChange={(e) => setUserForm({ ...userForm, password: e.target.value })}
              required
            />
          </label>
          <label>
            Role
            <select
              value={userForm.role}
              onChange={(e) => setUserForm({ ...userForm, role: e.target.value })}
            >
              <option value="staff">staff</option>
              <option value="admin">admin</option>
            </select>
          </label>
          <button type="submit">Create user</button>
          <ul>
            {users.map((u) => (
              <li key={u.id}>
                {u.username} — {u.role}
              </li>
            ))}
          </ul>
        </form>
      </div>

      <form className="card form-grid" onSubmit={addTest}>
        <h3>Add test (single parameter)</h3>
        <div className="two-col">
          <label>
            Test code
            <input
              value={testForm.code}
              onChange={(e) => setTestForm({ ...testForm, code: e.target.value })}
              required
            />
          </label>
          <label>
            Test name
            <input
              value={testForm.name}
              onChange={(e) => setTestForm({ ...testForm, name: e.target.value })}
              required
            />
          </label>
          <label>
            Sample type
            <input
              value={testForm.sample_type}
              onChange={(e) => setTestForm({ ...testForm, sample_type: e.target.value })}
            />
          </label>
          <label>
            Unit
            <input
              value={testForm.unit}
              onChange={(e) => setTestForm({ ...testForm, unit: e.target.value })}
            />
          </label>
          <label>
            Parameter name
            <input
              value={testForm.param_name}
              onChange={(e) => setTestForm({ ...testForm, param_name: e.target.value })}
              placeholder="Defaults to test name"
            />
          </label>
          <label>
            Reference text
            <input
              value={testForm.reference_text}
              onChange={(e) => setTestForm({ ...testForm, reference_text: e.target.value })}
              placeholder="e.g. 70 - 100"
            />
          </label>
          <label>
            Reference min
            <input
              value={testForm.reference_min}
              onChange={(e) => setTestForm({ ...testForm, reference_min: e.target.value })}
            />
          </label>
          <label>
            Reference max
            <input
              value={testForm.reference_max}
              onChange={(e) => setTestForm({ ...testForm, reference_max: e.target.value })}
            />
          </label>
        </div>
        <button type="submit">Add test</button>
      </form>

      <div className="card">
        <h3>Test catalog</h3>
        <table className="data">
          <thead>
            <tr>
              <th>Code</th>
              <th>Name</th>
              <th>Sample</th>
              <th>Parameters</th>
              <th>Active</th>
            </tr>
          </thead>
          <tbody>
            {tests.map((t) => (
              <tr key={t.id}>
                <td>{t.code}</td>
                <td>{t.name}</td>
                <td>{t.sample_type}</td>
                <td>{t.parameters?.length || 0}</td>
                <td>{t.is_active ? "yes" : "no"}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
