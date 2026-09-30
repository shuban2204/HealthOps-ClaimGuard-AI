import { BarChart3, FileSearch, Gauge, Info, ShieldCheck } from "lucide-react";
import { NavLink, Outlet } from "react-router-dom";

export function AppShell() {
  return (
    <div className="app-shell">
      <aside className="nav-rail" aria-label="Primary navigation">
        <div className="rail-logo" title="HealthOps ClaimGuard">
          <ShieldCheck size={26} />
        </div>
        <nav>
          <NavLink to="/" title="Overview" end>
            <Gauge size={21} />
            <span>Overview</span>
          </NavLink>
          <NavLink to="/claims" title="Claims">
            <FileSearch size={21} />
            <span>Claims</span>
          </NavLink>
          <NavLink to="/model" title="Model Insights">
            <BarChart3 size={21} />
            <span>Model</span>
          </NavLink>
        </nav>
        <div className="rail-info" title="Analyst decision support">
          <Info size={18} />
        </div>
      </aside>
      <Outlet />
    </div>
  );
}

