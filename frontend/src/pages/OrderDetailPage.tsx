import { FormEvent, useEffect, useMemo, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { api, Order } from "../api";

export default function OrderDetailPage() {
  const { id } = useParams();
  const [order, setOrder] = useState<Order | null>(null);
  const [values, setValues] = useState<Record<number, string>>({});
  const [error, setError] = useState("");
  const [message, setMessage] = useState("");
  const [busy, setBusy] = useState(false);

  const load = async () => {
    const o = await api.get<Order>(`/orders/${id}`);
    setOrder(o);
    const map: Record<number, string> = {};
    o.order_tests.forEach((ot) =>
      ot.results.forEach((r) => {
        map[r.test_parameter_id] = r.value_text || "";
      })
    );
    setValues(map);
  };

  useEffect(() => {
    load().catch((e) => setError(e.message));
  }, [id]);

  const rows = useMemo(() => {
    if (!order) return [];
    return order.order_tests.flatMap((ot) =>
      [...ot.results]
        .sort((a, b) => (a.parameter?.sort_order || 0) - (b.parameter?.sort_order || 0))
        .map((r) => ({
          orderTest: ot,
          result: r,
        }))
    );
  }, [order]);

  const save = async (markCompleted: boolean) => {
    if (!order) return;
    setBusy(true);
    setError("");
    setMessage("");
    try {
      const payload = {
        results: Object.entries(values).map(([test_parameter_id, value_text]) => ({
          test_parameter_id: Number(test_parameter_id),
          value_text,
        })),
        mark_completed: markCompleted,
      };
      const updated = await api.put<Order>(`/orders/${order.id}/results`, payload);
      setOrder(updated);
      setMessage(markCompleted ? "Order completed." : "Results saved.");
    } catch (e) {
      setError(e instanceof Error ? e.message : "Save failed");
    } finally {
      setBusy(false);
    }
  };

  const onSubmit = (e: FormEvent) => {
    e.preventDefault();
    save(false);
  };

  if (!order && !error) return <p>Loading…</p>;
  if (!order) return <p className="error">{error}</p>;

  return (
    <div>
      <div className="page-header">
        <div>
          <h1>{order.order_number}</h1>
          <div className="row">
            <span className={`badge ${order.status}`}>{order.status.replace("_", " ")}</span>
            <span>
              {order.patient?.full_name} ({order.patient?.patient_code})
            </span>
            <span>Dr: {order.doctor?.full_name || "—"}</span>
          </div>
        </div>
        <div className="row no-print">
          <Link to={`/orders/${order.id}/report`}>
            <button type="button" className="secondary">
              Preview report
            </button>
          </Link>
        </div>
      </div>

      <form className="card stack" onSubmit={onSubmit}>
        <table className="data">
          <thead>
            <tr>
              <th>Test</th>
              <th>Parameter</th>
              <th>Value</th>
              <th>Unit</th>
              <th>Reference</th>
              <th>Flag</th>
            </tr>
          </thead>
          <tbody>
            {rows.map(({ orderTest, result }) => (
              <tr key={result.id}>
                <td>{orderTest.test_definition?.name}</td>
                <td>{result.parameter?.name}</td>
                <td>
                  <input
                    value={values[result.test_parameter_id] || ""}
                    onChange={(e) =>
                      setValues({ ...values, [result.test_parameter_id]: e.target.value })
                    }
                  />
                </td>
                <td>{result.parameter?.unit}</td>
                <td>{result.parameter?.reference_text}</td>
                <td className={result.flag ? "error" : ""}>{result.flag || "—"}</td>
              </tr>
            ))}
          </tbody>
        </table>
        {error && <p className="error">{error}</p>}
        {message && <p className="ok">{message}</p>}
        <div className="row no-print">
          <button type="submit" disabled={busy}>
            Save results
          </button>
          <button
            type="button"
            className="secondary"
            disabled={busy || order.status === "completed"}
            onClick={() => save(true)}
          >
            Mark completed
          </button>
        </div>
      </form>
    </div>
  );
}
