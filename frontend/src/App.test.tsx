import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { MemoryRouter } from "react-router-dom";
import { beforeEach, describe, expect, it, vi } from "vitest";

import App from "./App";
import { installMockFetch } from "./test/mockApi";

function renderApp(route = "/") {
  const queryClient = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  return render(
    <QueryClientProvider client={queryClient}>
      <MemoryRouter initialEntries={[route]}>
        <App />
      </MemoryRouter>
    </QueryClientProvider>
  );
}

describe("ClaimGuard frontend", () => {
  beforeEach(() => {
    installMockFetch();
    sessionStorage.clear();
  });

  it("renders API-backed dashboard summary and priority queue", async () => {
    renderApp("/");
    expect(await screen.findByText("49,199")).toBeInTheDocument();
    expect(await screen.findByRole("heading", { name: "Priority Review Queue", level: 2 })).toBeInTheDocument();
    expect(screen.getByText("CLM-1")).toBeInTheDocument();
  });

  it("renders claims table and updates filter query controls", async () => {
    renderApp("/claims");
    expect(await screen.findByRole("heading", { name: "Priority Review Queue", level: 1 })).toBeInTheDocument();
    expect(screen.getByText("CLM-1")).toBeInTheDocument();
    await userEvent.selectOptions(screen.getByLabelText("Unusual"), "true");
    await waitFor(() => expect(fetch).toHaveBeenCalledWith(expect.stringContaining("is_anomaly=true")));
  });

  it("renders claim detail with explanation, anomaly, and evidence", async () => {
    renderApp("/claims/CLM-1");
    expect(await screen.findByText("Claim Investigation")).toBeInTheDocument();
    expect(await screen.findByText("Missing required authorization")).toBeInTheDocument();
    expect(await screen.findByText("Unusual Claim Signal")).toBeInTheDocument();
    expect(await screen.findByText("Prior Authorization Policy")).toBeInTheDocument();
    const generateButton = screen.getByRole("button", { name: /generate brief/i });
    expect(generateButton).not.toBeDisabled();
    fireEvent.click(generateButton);
    await waitFor(() => expect(fetch).toHaveBeenCalledWith(expect.stringContaining("/claims/CLM-1/brief")));
    await waitFor(() => expect(screen.getByText(/Claim CLM-1 is prioritized as HIGH risk/i)).toBeInTheDocument());
    expect(screen.getByText(/Decision support only/i)).toBeInTheDocument();
  });

  it("handles 404 claim state professionally", async () => {
    renderApp("/claims/CLM-404");
    expect(await screen.findByText("Claim could not be loaded.")).toBeInTheDocument();
  });

  it("renders model insights and data provenance", async () => {
    renderApp("/model");
    expect(await screen.findByText("Model Insights")).toBeInTheDocument();
    expect(await screen.findByText("xgboost")).toBeInTheDocument();
    expect(await screen.findByText(/CMS DE-SynPUF Sample 1 outpatient claims/i)).toBeInTheDocument();
  });
});
