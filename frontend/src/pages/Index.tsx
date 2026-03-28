import { useState } from "react";
import { useHealthCheck } from "@/hooks/use-api";
import { getApiBaseUrl, setApiBaseUrl } from "@/lib/api";
import { DashboardView } from "@/components/views/DashboardView";
import { UserMonitorView } from "@/components/views/UserMonitorView";
import { DecisionLogView } from "@/components/views/DecisionLogView";
import { SimulationView } from "@/components/views/SimulationView";

const tabs = [
  { id: "dashboard", label: "Dashboard" },
  { id: "users", label: "Users" },
  { id: "decisions", label: "Decision Log" },
  { id: "simulation", label: "Simulation" },
] as const;

type TabId = typeof tabs[number]["id"];

const Index = () => {
  const [activeTab, setActiveTab] = useState<TabId>("dashboard");
  const [apiUrl, setApiUrl] = useState(getApiBaseUrl());
  const [editingUrl, setEditingUrl] = useState(false);
  const { data: isHealthy } = useHealthCheck();

  const handleUrlSubmit = () => {
    setApiBaseUrl(apiUrl);
    setEditingUrl(false);
  };

  return (
    <div className="min-h-screen bg-background">
      {/* Top Bar */}
      <div className="h-10 border-b border-border flex items-center px-4 gap-4 bg-card">
        <span className="text-sm font-semibold tracking-tight text-foreground">CogniShift</span>
        <span className="text-xs text-muted-foreground">Operational Console</span>

        <div className="ml-auto flex items-center gap-3">
          {editingUrl ? (
            <form className="flex items-center gap-1" onSubmit={(e) => { e.preventDefault(); handleUrlSubmit(); }}>
              <input
                className="h-6 text-xs px-2 border border-border rounded-sm bg-background font-mono w-64"
                value={apiUrl}
                onChange={(e) => setApiUrl(e.target.value)}
                autoFocus
              />
              <button type="submit" className="text-xs text-primary hover:underline">Set</button>
              <button type="button" className="text-xs text-muted-foreground hover:underline" onClick={() => { setEditingUrl(false); setApiUrl(getApiBaseUrl()); }}>Cancel</button>
            </form>
          ) : (
            <button
              className="text-xs font-mono text-muted-foreground hover:text-foreground"
              onClick={() => setEditingUrl(true)}
            >
              {apiUrl}
            </button>
          )}
          <span className="flex items-center gap-1.5 text-xs text-muted-foreground">
            <span className={`text-[8px] leading-none ${isHealthy ? "text-status-send" : "text-status-block"}`}>●</span>
            {isHealthy ? "Connected" : "Disconnected"}
          </span>
        </div>
      </div>

      {/* Tab Navigation */}
      <div className="border-b border-border flex bg-card">
        {tabs.map((tab) => (
          <button
            key={tab.id}
            className={`px-4 py-2 text-xs font-medium border-b-2 transition-colors ${
              activeTab === tab.id
                ? "border-primary text-foreground"
                : "border-transparent text-muted-foreground hover:text-foreground"
            }`}
            onClick={() => setActiveTab(tab.id)}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {/* Content */}
      <div>
        {activeTab === "dashboard" && <DashboardView />}
        {activeTab === "users" && <UserMonitorView />}
        {activeTab === "decisions" && <DecisionLogView />}
        {activeTab === "simulation" && <SimulationView />}
      </div>
    </div>
  );
};

export default Index;
