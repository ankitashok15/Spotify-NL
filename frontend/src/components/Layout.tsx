import { NavLink, Outlet } from "react-router-dom";

const links = [
  { to: "/", label: "Dashboard" },
  { to: "/search", label: "Semantic Search" },
  { to: "/ask", label: "Ask (RAG)" },
  { to: "/agent", label: "Agent" },
  { to: "/themes", label: "Themes" },
  { to: "/insights", label: "Insights" },
  { to: "/reviews", label: "Reviews" },
];

export function Layout() {
  return (
    <div className="layout">
      <aside className="sidebar">
        <div className="logo">Spotify NL</div>
        {links.map((l) => (
          <NavLink
            key={l.to}
            to={l.to}
            end={l.to === "/"}
            className={({ isActive }) => `nav-link${isActive ? " active" : ""}`}
          >
            {l.label}
          </NavLink>
        ))}
      </aside>
      <main className="main">
        <Outlet />
      </main>
    </div>
  );
}
