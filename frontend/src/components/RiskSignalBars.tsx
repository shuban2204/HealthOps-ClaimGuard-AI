import type { Driver } from "../types/api";
import { humanizeFeature } from "../utils/format";

export function RiskSignalBars({ drivers }: { drivers: Driver[] }) {
  const max = Math.max(...drivers.map((driver) => driver.importance), 0.001);
  return (
    <div className="signal-bars">
      {drivers.map((driver, index) => (
        <div className="signal-row" key={driver.feature}>
          <span className="rank">{String(index + 1).padStart(2, "0")}</span>
          <span className="signal-label">{humanizeFeature(driver.feature)}</span>
          <div className="signal-track">
            <i style={{ width: `${(driver.importance / max) * 100}%` }} />
          </div>
          <strong>{Math.round((driver.importance / max) * 100)}%</strong>
        </div>
      ))}
    </div>
  );
}

