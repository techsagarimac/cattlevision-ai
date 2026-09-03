import {
  Area,
  AreaChart,
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  Legend,
  Pie,
  PieChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

const COLORS = ["#3c7a5a", "#d7b07a", "#b5741a", "#9b3b2e"];

function formatTick(value) {
  if (!value) return "";
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return String(value);
  return date.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
}

export function ActivityChart({ data }) {
  const rows = data?.length ? data : [{ time: "—", activity: 0 }];
  return (
    <div className="card">
      <h3>Animal activity over time</h3>
      <ResponsiveContainer width="100%" height={240}>
        <AreaChart data={rows}>
          <CartesianGrid strokeDasharray="3 3" stroke="#e0e7e2" />
          <XAxis dataKey="time" tickFormatter={formatTick} />
          <YAxis />
          <Tooltip labelFormatter={formatTick} />
          <Area type="monotone" dataKey="activity" stroke="#1f4d3a" fill="#b7d4c3" />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  );
}

export function BehaviorChart({ counts }) {
  const data = Object.entries(counts || {}).map(([name, value]) => ({ name, value }));
  const rows = data.length ? data : [{ name: "No data", value: 1 }];
  return (
    <div className="card">
      <h3>Animals by behavior</h3>
      <ResponsiveContainer width="100%" height={240}>
        <BarChart data={rows}>
          <CartesianGrid strokeDasharray="3 3" stroke="#e0e7e2" />
          <XAxis dataKey="name" />
          <YAxis allowDecimals={false} />
          <Tooltip />
          <Bar dataKey="value" fill="#3c7a5a" radius={[6, 6, 0, 0]} />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}

export function RiskChart({ distribution }) {
  const data = Object.entries(distribution || {}).map(([name, value]) => ({ name, value }));
  return (
    <div className="card">
      <h3>Risk-score distribution</h3>
      <ResponsiveContainer width="100%" height={240}>
        <PieChart>
          <Pie data={data} dataKey="value" nameKey="name" innerRadius={50} outerRadius={80} paddingAngle={3}>
            {data.map((entry, index) => (
              <Cell key={entry.name} fill={COLORS[index % COLORS.length]} />
            ))}
          </Pie>
          <Legend />
          <Tooltip />
        </PieChart>
      </ResponsiveContainer>
    </div>
  );
}

export function AlertsChart({ data }) {
  const rows = data?.length ? data : [{ time: "—", count: 0 }];
  return (
    <div className="card">
      <h3>Alerts over time</h3>
      <ResponsiveContainer width="100%" height={240}>
        <BarChart data={rows}>
          <CartesianGrid strokeDasharray="3 3" stroke="#e0e7e2" />
          <XAxis dataKey="time" tickFormatter={formatTick} />
          <YAxis allowDecimals={false} />
          <Tooltip labelFormatter={formatTick} />
          <Bar dataKey="count" fill="#b5741a" radius={[6, 6, 0, 0]} />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
