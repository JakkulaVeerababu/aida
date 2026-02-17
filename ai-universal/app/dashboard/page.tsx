"use client";

import { useState } from "react";

export default function Dashboard() {
  const [data, setData] = useState<any[]>([]);

  const handleFile = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    const text = await file.text();
    const rows = text.split("\n").map(r => r.split(","));
    setData(rows);
  };

  return (
    <main style={{ padding: 40 }}>
      <h1>Data Analysis Dashboard</h1>

      <input type="file" accept=".csv" onChange={handleFile} />

      {data.length > 0 && (
        <table border={1} cellPadding={5}>
          <tbody>
            {data.slice(0, 10).map((row, i) => (
              <tr key={i}>
                {row.map((cell, j) => (
                  <td key={j}>{cell}</td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </main>
  );
}
