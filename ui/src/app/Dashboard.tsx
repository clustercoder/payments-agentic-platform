import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import {
  LineChart,
  Line,
  AreaChart,
  Area,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  CartesianGrid,
} from "recharts";
import {
  Activity,
  ShieldAlert,
  Brain,
  Wallet,
  TrendingUp,
  AlertCircle,
  CheckCircle2,
  Clock,
  Zap,
  Database,
  RefreshCw,
} from "lucide-react";
import React, { useState, useEffect } from "react";

const metrics = [
  { time: "10:00", success: 92, latency: 420, volume: 1240 },
  { time: "10:05", success: 89, latency: 510, volume: 1380 },
  { time: "10:10", success: 95, latency: 390, volume: 1520 },
  { time: "10:15", success: 90, latency: 480, volume: 1410 },
  { time: "10:20", success: 94, latency: 410, volume: 1650 },
  { time: "10:25", success: 93, latency: 430, volume: 1590 },
];

const recentTransactions = [
  {
    id: "txn_1a2b3c",
    merchant: "E-Commerce Store",
    amount: "₹2,450.00",
    status: "success",
    time: "2m ago",
  },
  {
    id: "txn_4d5e6f",
    merchant: "Food Delivery",
    amount: "₹890.00",
    status: "success",
    time: "3m ago",
  },
  {
    id: "txn_7g8h9i",
    merchant: "Subscription SaaS",
    amount: "₹12,999.00",
    status: "pending",
    time: "5m ago",
  },
  {
    id: "txn_0j1k2l",
    merchant: "Travel Booking",
    amount: "₹45,000.00",
    status: "failed",
    time: "7m ago",
  },
];

const agentActions = [
  {
    time: "10:24",
    action: "Retry optimization triggered",
    confidence: 0.94,
    impact: "+2.3% success rate",
  },
  {
    time: "10:18",
    action: "Issuer routing adjusted",
    confidence: 0.89,
    impact: "-45ms latency",
  },
  {
    time: "10:12",
    action: "Anomaly detected & mitigated",
    confidence: 0.97,
    impact: "Prevented ₹12K loss",
  },
];

export default function Dashboard() {
  const [liveUpdate, setLiveUpdate] = useState(0);

  useEffect(() => {
    const interval = setInterval(() => {
      setLiveUpdate((prev) => prev + 1);
    }, 3000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-950 via-slate-900 to-slate-950 text-slate-100">
      {/* Background Pattern */}
      <div className="fixed inset-0 opacity-10">
        <div className="absolute inset-0 bg-[radial-gradient(circle_at_50%_50%,rgba(76,29,149,0.1),transparent_50%)]" />
        <div className="absolute inset-0 bg-[linear-gradient(to_right,#4f4f4f2e_1px,transparent_1px),linear-gradient(to_bottom,#4f4f4f2e_1px,transparent_1px)] bg-[size:64px_64px]" />
      </div>

      <div className="relative z-10 p-8 max-w-[1800px] mx-auto">
        {/* Header */}
        <header className="mb-12 flex items-center justify-between">
          <div>
            <div className="flex items-center gap-4 mb-2">
              <div className="h-10 w-10 rounded-lg bg-gradient-to-br from-violet-500 to-fuchsia-500 flex items-center justify-center">
                <Zap className="w-6 h-6 text-white" />
              </div>
              <h1 className="text-5xl font-black tracking-tight bg-gradient-to-r from-violet-400 via-fuchsia-400 to-pink-400 bg-clip-text text-transparent">
                Payments Agentic Platform
              </h1>
            </div>
            <p className="text-slate-400 text-lg ml-14 font-medium">
              Real-time intelligent payment orchestration
            </p>
          </div>

          <div className="flex items-center gap-3">
            <div className="px-4 py-2 rounded-lg bg-slate-800/50 backdrop-blur-sm border border-slate-700/50 flex items-center gap-2">
              <div className="h-2 w-2 rounded-full bg-emerald-400 animate-pulse" />
              <span className="text-sm font-semibold text-slate-300">
                System Operational
              </span>
            </div>
            <Button className="bg-gradient-to-r from-violet-600 to-fuchsia-600 hover:from-violet-700 hover:to-fuchsia-700 font-semibold shadow-lg shadow-violet-500/20">
              <RefreshCw className="w-4 h-4 mr-2" />
              Refresh Data
            </Button>
          </div>
        </header>

        {/* Stats Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <StatCard
            icon={<Wallet className="w-6 h-6" />}
            label="Transaction Success"
            value="93.4%"
            trend="+2.3%"
            trendUp={true}
            color="emerald"
          />
          <StatCard
            icon={<Activity className="w-6 h-6" />}
            label="Avg Latency"
            value="445ms"
            trend="-12ms"
            trendUp={true}
            color="blue"
          />
          <StatCard
            icon={<ShieldAlert className="w-6 h-6" />}
            label="Anomalies (24h)"
            value="7"
            trend="-3"
            trendUp={true}
            color="amber"
            highlight={true}
          />
          <StatCard
            icon={<Brain className="w-6 h-6" />}
            label="Agent Decisions"
            value="1,248"
            trend="+127"
            trendUp={true}
            color="violet"
          />
        </div>

        {/* Main Content Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-6">
          {/* System Health Chart - Spans 2 columns */}
          <Card className="lg:col-span-2 bg-slate-900/50 backdrop-blur-sm border-slate-800/50 shadow-2xl overflow-hidden">
            <CardContent className="p-6">
              <div className="flex items-center justify-between mb-6">
                <div>
                  <h2 className="text-2xl font-bold text-white mb-1">
                    System Health
                  </h2>
                  <p className="text-slate-400 text-sm">
                    Real-time performance metrics
                  </p>
                </div>
                <div className="flex gap-4">
                  <div className="flex items-center gap-2">
                    <div className="h-3 w-3 rounded-full bg-violet-500" />
                    <span className="text-xs text-slate-400 font-medium">
                      Success Rate
                    </span>
                  </div>
                  <div className="flex items-center gap-2">
                    <div className="h-3 w-3 rounded-full bg-fuchsia-500" />
                    <span className="text-xs text-slate-400 font-medium">
                      Latency
                    </span>
                  </div>
                </div>
              </div>
              <div className="h-80">
                <ResponsiveContainer width="100%" height="100%">
                  <AreaChart data={metrics}>
                    <defs>
                      <linearGradient
                        id="colorSuccess"
                        x1="0"
                        y1="0"
                        x2="0"
                        y2="1"
                      >
                        <stop
                          offset="5%"
                          stopColor="#8b5cf6"
                          stopOpacity={0.3}
                        />
                        <stop
                          offset="95%"
                          stopColor="#8b5cf6"
                          stopOpacity={0}
                        />
                      </linearGradient>
                      <linearGradient
                        id="colorLatency"
                        x1="0"
                        y1="0"
                        x2="0"
                        y2="1"
                      >
                        <stop
                          offset="5%"
                          stopColor="#d946ef"
                          stopOpacity={0.3}
                        />
                        <stop
                          offset="95%"
                          stopColor="#d946ef"
                          stopOpacity={0}
                        />
                      </linearGradient>
                    </defs>
                    <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                    <XAxis
                      dataKey="time"
                      stroke="#64748b"
                      style={{ fontSize: "12px" }}
                    />
                    <YAxis stroke="#64748b" style={{ fontSize: "12px" }} />
                    <Tooltip
                      contentStyle={{
                        backgroundColor: "#1e293b",
                        border: "1px solid #334155",
                        borderRadius: "8px",
                      }}
                    />
                    <Area
                      type="monotone"
                      dataKey="success"
                      stroke="#8b5cf6"
                      strokeWidth={3}
                      fill="url(#colorSuccess)"
                    />
                    <Area
                      type="monotone"
                      dataKey="latency"
                      stroke="#d946ef"
                      strokeWidth={3}
                      fill="url(#colorLatency)"
                    />
                  </AreaChart>
                </ResponsiveContainer>
              </div>
            </CardContent>
          </Card>

          {/* Agent Actions */}
          <Card className="bg-slate-900/50 backdrop-blur-sm border-slate-800/50 shadow-2xl">
            <CardContent className="p-6">
              <div className="flex items-center gap-3 mb-6">
                <div className="p-2 rounded-lg bg-gradient-to-br from-violet-500/20 to-fuchsia-500/20">
                  <Brain className="w-5 h-5 text-violet-400" />
                </div>
                <div>
                  <h2 className="text-xl font-bold text-white">
                    Recent Agent Actions
                  </h2>
                  <p className="text-xs text-slate-400">AI-driven optimizations</p>
                </div>
              </div>
              <div className="space-y-4">
                {agentActions.map((action, idx) => (
                  <div
                    key={idx}
                    className="p-4 rounded-lg bg-slate-800/40 border border-slate-700/50 hover:border-violet-500/50 transition-all cursor-pointer group"
                  >
                    <div className="flex items-start justify-between mb-2">
                      <span className="text-xs font-mono text-slate-500">
                        {action.time}
                      </span>
                      <span className="text-xs px-2 py-1 rounded bg-violet-500/20 text-violet-300 font-semibold">
                        {Math.round(action.confidence * 100)}% confidence
                      </span>
                    </div>
                    <p className="text-sm font-semibold text-white mb-1 group-hover:text-violet-300 transition-colors">
                      {action.action}
                    </p>
                    <p className="text-xs text-emerald-400 font-medium">
                      {action.impact}
                    </p>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Bottom Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Recent Transactions */}
          <Card className="bg-slate-900/50 backdrop-blur-sm border-slate-800/50 shadow-2xl">
            <CardContent className="p-6">
              <div className="flex items-center gap-3 mb-6">
                <div className="p-2 rounded-lg bg-gradient-to-br from-emerald-500/20 to-teal-500/20">
                  <Database className="w-5 h-5 text-emerald-400" />
                </div>
                <div>
                  <h2 className="text-xl font-bold text-white">
                    Live Transactions
                  </h2>
                  <p className="text-xs text-slate-400">Real-time payment stream</p>
                </div>
              </div>
              <div className="space-y-3">
                {recentTransactions.map((txn) => (
                  <div
                    key={txn.id}
                    className="p-4 rounded-lg bg-slate-800/40 border border-slate-700/50 hover:border-slate-600/50 transition-all"
                  >
                    <div className="flex items-center justify-between mb-2">
                      <span className="text-xs font-mono text-slate-500">
                        {txn.id}
                      </span>
                      <div className="flex items-center gap-2">
                        {txn.status === "success" && (
                          <>
                            <CheckCircle2 className="w-4 h-4 text-emerald-400" />
                            <span className="text-xs font-semibold text-emerald-400">
                              Success
                            </span>
                          </>
                        )}
                        {txn.status === "pending" && (
                          <>
                            <Clock className="w-4 h-4 text-amber-400" />
                            <span className="text-xs font-semibold text-amber-400">
                              Pending
                            </span>
                          </>
                        )}
                        {txn.status === "failed" && (
                          <>
                            <AlertCircle className="w-4 h-4 text-rose-400" />
                            <span className="text-xs font-semibold text-rose-400">
                              Failed
                            </span>
                          </>
                        )}
                      </div>
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="text-sm font-medium text-white">
                        {txn.merchant}
                      </span>
                      <span className="text-sm font-bold text-slate-200">
                        {txn.amount}
                      </span>
                    </div>
                    <span className="text-xs text-slate-500 mt-1 block">
                      {txn.time}
                    </span>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>

          {/* Quick Actions */}
          <Card className="bg-slate-900/50 backdrop-blur-sm border-slate-800/50 shadow-2xl">
            <CardContent className="p-6">
              <h2 className="text-xl font-bold text-white mb-6">
                Quick Actions
              </h2>
              <div className="grid grid-cols-2 gap-4">
                <ActionButton
                  icon={<Activity />}
                  label="Live Transactions"
                  description="Monitor in real-time"
                  variant="primary"
                />
                <ActionButton
                  icon={<ShieldAlert />}
                  label="Anomaly Feed"
                  description="Security alerts"
                  variant="warning"
                />
                <ActionButton
                  icon={<Brain />}
                  label="Agent Logs"
                  description="View reasoning"
                  variant="secondary"
                />
                <ActionButton
                  icon={<TrendingUp />}
                  label="Analytics"
                  description="Deep insights"
                  variant="secondary"
                />
              </div>

              {/* System Status */}
              <div className="mt-6 p-4 rounded-lg bg-slate-800/40 border border-slate-700/50">
                <h3 className="text-sm font-bold text-white mb-3">
                  Service Status
                </h3>
                <div className="space-y-2">
                  <ServiceStatus
                    name="Payment Gateway"
                    status="operational"
                  />
                  <ServiceStatus name="Agent Brain" status="operational" />
                  <ServiceStatus
                    name="Anomaly Detector"
                    status="operational"
                  />
                  <ServiceStatus name="Policy Executor" status="operational" />
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}

function StatCard({
  icon,
  label,
  value,
  trend,
  trendUp,
  color,
  highlight,
}: {
  icon: React.ReactNode;
  label: string;
  value: string;
  trend?: string;
  trendUp?: boolean;
  color: "emerald" | "blue" | "amber" | "violet";
  highlight?: boolean;
}) {
  const colorClasses = {
    emerald: "from-emerald-500/20 to-teal-500/20 text-emerald-400",
    blue: "from-blue-500/20 to-cyan-500/20 text-blue-400",
    amber: "from-amber-500/20 to-orange-500/20 text-amber-400",
    violet: "from-violet-500/20 to-fuchsia-500/20 text-violet-400",
  };

  const borderColorClasses = {
    emerald: "border-emerald-500/50",
    blue: "border-blue-500/50",
    amber: "border-amber-500/50",
    violet: "border-violet-500/50",
  };

  return (
    <Card
      className={`bg-slate-900/50 backdrop-blur-sm ${
        highlight ? borderColorClasses[color] : "border-slate-800/50"
      } shadow-xl hover:shadow-2xl transition-all hover:-translate-y-1 cursor-pointer group`}
    >
      <CardContent className="p-6">
        <div className="flex items-start justify-between mb-4">
          <div
            className={`p-3 rounded-xl bg-gradient-to-br ${colorClasses[color]}`}
          >
            {icon}
          </div>
          {trend && (
            <div
              className={`flex items-center gap-1 text-xs font-bold ${
                trendUp ? "text-emerald-400" : "text-rose-400"
              }`}
            >
              <TrendingUp
                className={`w-3 h-3 ${!trendUp && "rotate-180"}`}
              />
              {trend}
            </div>
          )}
        </div>
        <div>
          <p className="text-sm text-slate-400 mb-1 font-medium">{label}</p>
          <p className="text-3xl font-black text-white tracking-tight">
            {value}
          </p>
        </div>
      </CardContent>
    </Card>
  );
}

function ActionButton({
  icon,
  label,
  description,
  variant,
}: {
  icon: React.ReactNode;
  label: string;
  description: string;
  variant: "primary" | "secondary" | "warning";
}) {
  const variantClasses = {
    primary:
      "bg-gradient-to-br from-violet-600 to-fuchsia-600 hover:from-violet-700 hover:to-fuchsia-700 text-white shadow-lg shadow-violet-500/20",
    secondary:
      "bg-slate-800/50 hover:bg-slate-700/50 text-slate-200 border border-slate-700/50",
    warning:
      "bg-gradient-to-br from-amber-600 to-orange-600 hover:from-amber-700 hover:to-orange-700 text-white shadow-lg shadow-amber-500/20",
  };

  return (
    <button
      className={`p-4 rounded-xl transition-all hover:-translate-y-1 text-left group ${variantClasses[variant]}`}
    >
      <div className="flex items-center gap-2 mb-2">
        <div className="group-hover:scale-110 transition-transform">
          {React.cloneElement(icon as React.ReactElement, {
            className: "w-5 h-5",
          })}
        </div>
        <span className="font-bold text-sm">{label}</span>
      </div>
      <p className="text-xs opacity-80">{description}</p>
    </button>
  );
}

function ServiceStatus({
  name,
  status,
}: {
  name: string;
  status: "operational" | "degraded" | "down";
}) {
  const statusConfig = {
    operational: { color: "bg-emerald-400", text: "Operational" },
    degraded: { color: "bg-amber-400", text: "Degraded" },
    down: { color: "bg-rose-400", text: "Down" },
  };

  return (
    <div className="flex items-center justify-between">
      <span className="text-sm text-slate-300">{name}</span>
      <div className="flex items-center gap-2">
        <div
          className={`h-2 w-2 rounded-full ${
            statusConfig[status].color
          } ${status === "operational" && "animate-pulse"}`}
        />
        <span className="text-xs text-slate-400 font-medium">
          {statusConfig[status].text}
        </span>
      </div>
    </div>
  );
}