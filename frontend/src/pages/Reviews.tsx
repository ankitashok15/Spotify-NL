import { useEffect, useState } from "react";
import { api } from "../api/client";

interface Review {
  id: string;
  rating?: number;
  device_type?: string;
  text_cleaned?: string;
  text_original?: string;
  processing_state: string;
}

export function ReviewsPage() {
  const [items, setItems] = useState<Review[]>([]);
  const [total, setTotal] = useState(0);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    api
      .reviews(30)
      .then((r) => {
        setItems(r.items as Review[]);
        setTotal(r.total);
      })
      .catch((e) => setError(e.message));
  }, []);

  return (
    <>
      <h1 className="page-title">Reviews</h1>
      <p className="page-sub">{total} reviews in corpus</p>
      {error && <div className="error">{error}</div>}
      {items.map((r) => (
        <div className="hit-card" key={r.id}>
          <div className="hit-meta">
            <span className="badge">★ {r.rating ?? "?"}</span>
            {r.device_type && <span className="badge">{r.device_type}</span>}
            <span className="badge">{r.processing_state}</span>
          </div>
          <p>{r.text_cleaned || r.text_original || "—"}</p>
        </div>
      ))}
    </>
  );
}
