import { Search } from "lucide-react";
import { useNavigate } from "react-router-dom";

export function PageHeader({ title, kicker }: { title: string; kicker: string }) {
  const navigate = useNavigate();
  return (
    <header className="top-header">
      <div>
        <p>{kicker}</p>
        <h1>{title}</h1>
      </div>
      <label className="global-search">
        <Search size={16} />
        <input
          placeholder="Search claim"
          onKeyDown={(event) => {
            if (event.key === "Enter" && event.currentTarget.value.trim()) {
              navigate(`/claims/${encodeURIComponent(event.currentTarget.value.trim())}`);
            }
          }}
        />
      </label>
      <div className="system-status">
        <span>CMS DE-SynPUF</span>
        <strong>System Ready</strong>
      </div>
    </header>
  );
}

