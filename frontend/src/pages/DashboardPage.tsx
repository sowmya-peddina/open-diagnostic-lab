import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { api, Order } from "../api";

export default function DashboardPage() {
  const [orders, setOrders] = useState<Order[]>([]);
  const [error, setError] = useState("");

  useEffect(() => {
    api
      .get<Order[]>("/orders?limit=50")
      .then(setOrders)
      .catch((e) => setError(e.message));
  }, []);

  return (
    <div>
      <div className="page-header">
        <h1>Recent orders</h1>
        <Link to="/orders/new">
          <button type="button">New order</button>
        </Link>
      </div>
      {error && <p className="error">{error}</p>}
      <table className="data">
        <thead>
          <tr>
            <th>Order</th>
            <th>Patient</th>
            <th>Doctor</th>
            <th>Status</th>
            <th>Ordered</th>
          </tr>
        </thead>
        <tbody>
          {orders.map((o) => (
            <tr key={o.id}>
              <td>
                <Link to={`/orders/${o.id}`}>{o.order_number}</Link>
              </td>
              <td>{o.patient?.full_name || o.patient_id}</td>
              <td>{o.doctor?.full_name || "—"}</td>
              <td>
                <span className={`badge ${o.status}`}>{o.status.replace("_", " ")}</span>
              </td>
              <td>{new Date(o.ordered_at).toLocaleString()}</td>
            </tr>
          ))}
          {!orders.length && (
            <tr>
              <td colSpan={5}>No orders yet. Create the first one.</td>
            </tr>
          )}
        </tbody>
      </table>
    </div>
  );
}
