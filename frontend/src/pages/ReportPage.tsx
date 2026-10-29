import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";

const API_BASE = import.meta.env.VITE_API_BASE || "/api";

export default function ReportPage() {
  const { id } = useParams();
  const [html, setHtml] = useState("");
  const [error, setError] = useState("");

  useEffect(() => {
    fetch(`${API_BASE}/reports/${id}/html`, { credentials: "include" })
      .then(async (res) => {
        if (!res.ok) throw new Error(await res.text());
        return res.text();
      })
      .then(setHtml)
      .catch((e) => setError(e.message));
  }, [id]);

  return (
    <div>
      <div className="page-header no-print">
        <h1>Report preview</h1>
        <div className="row">
          <Link to={`/orders/${id}`}>
            <button type="button" className="secondary">
              Back to order
            </button>
          </Link>
          <button
            type="button"
            className="secondary"
            onClick={async () => {
              const res = await fetch(`${API_BASE}/reports/${id}/pdf`, {
                credentials: "include",
              });
              if (!res.ok) {
                setError("PDF download failed");
                return;
              }
              const blob = await res.blob();
              const url = URL.createObjectURL(blob);
              const a = document.createElement("a");
              a.href = url;
              a.download = `report-${id}.pdf`;
              a.click();
              URL.revokeObjectURL(url);
            }}
          >
            Download PDF
          </button>
          <button type="button" onClick={() => window.print()}>
            Print
          </button>
        </div>
      </div>
      {error && <p className="error">{error}</p>}
      <div className="card" dangerouslySetInnerHTML={{ __html: html }} />
    </div>
  );
}
