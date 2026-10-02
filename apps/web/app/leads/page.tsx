"use client";

import { useEffect, useState } from "react";
import { Navbar } from "@/components/Navbar";
import { Footer } from "@/components/Footer";
import { fetchLeads } from "@/lib/api";
import { CustomerContext } from "@/types";
import { Users, Shield, ArrowUpRight, BarChart3, Clock, DollarSign, Loader2 } from "lucide-react";

export default function LeadsPage() {
  const [leads, setLeads] = useState<CustomerContext[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    fetchLeads()
      .then((data) => setLeads(data))
      .catch((err) => console.error("Error loading leads:", err))
      .finally(() => setIsLoading(false));
  }, []);

  const getStatusBadge = (status?: string) => {
    switch (status) {
      case "MEETING_BOOKED":
        return "bg-emerald-950/80 border-emerald-700 text-emerald-300";
      case "QUALIFIED":
        return "bg-cyan-950/80 border-cyan-700 text-cyan-300";
      case "QUALIFYING":
        return "bg-amber-950/80 border-amber-700 text-amber-300";
      case "HANDOFF":
        return "bg-purple-950/80 border-purple-700 text-purple-300";
      default:
        return "bg-zinc-800 border-zinc-700 text-zinc-300";
    }
  };

  return (
    <div className="min-h-screen bg-zinc-950 text-zinc-100 flex flex-col font-sans">
      <Navbar />

      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-6">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between pb-6 border-b border-zinc-900 gap-4">
          <div>
            <div className="flex items-center space-x-2 text-xs font-mono text-zinc-400 mb-1">
              <Users className="w-4 h-4 text-emerald-400" />
              <span>SYSTEM OF RECORD</span>
            </div>
            <h1 className="text-2xl font-bold tracking-tight text-white">Demo CRM Pipeline</h1>
            <p className="text-xs sm:text-sm text-zinc-400 mt-1">
              Real database records populated autonomously by the AI Voice Employee during caller conversations.
            </p>
          </div>

          <div className="flex items-center space-x-2 bg-zinc-900/90 border border-zinc-800 px-3 py-1.5 rounded-lg text-xs font-mono text-zinc-400">
            <Shield className="w-3.5 h-3.5 text-zinc-500" />
            <span>Fictional Demonstration Data</span>
          </div>
        </div>

        {/* Table Card */}
        <div className="bg-zinc-900/40 border border-zinc-800 rounded-2xl overflow-hidden shadow-xl">
          {isLoading ? (
            <div className="py-20 flex flex-col items-center justify-center space-y-2 text-zinc-500">
              <Loader2 className="w-6 h-6 animate-spin text-emerald-400" />
              <span className="text-xs font-mono">Loading CRM pipeline records...</span>
            </div>
          ) : leads.length === 0 ? (
            <div className="py-16 text-center text-zinc-500 text-sm">
              No leads currently in database. Have a conversation on the home page to create one!
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs">
                <thead className="bg-zinc-900/80 border-b border-zinc-800 text-zinc-400 font-mono uppercase text-[10px] tracking-wider">
                  <tr>
                    <th className="px-5 py-3.5">Lead Name / Company</th>
                    <th className="px-5 py-3.5">Inquiry Scope / Use Case</th>
                    <th className="px-5 py-3.5">Timeline & Budget</th>
                    <th className="px-5 py-3.5 text-center">Score</th>
                    <th className="px-5 py-3.5">Pipeline Status</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-zinc-800/60">
                  {leads.map((lead) => (
                    <tr key={lead.id} className="hover:bg-zinc-800/20 transition-colors">
                      <td className="px-5 py-4">
                        <div className="font-semibold text-zinc-200">
                          {lead.name || "Anonymous Caller"}
                        </div>
                        <div className="text-zinc-400 font-mono text-[11px]">
                          {lead.company || "Company not provided"} {lead.role ? `· ${lead.role}` : ""}
                        </div>
                        {lead.email && (
                          <div className="text-zinc-500 text-[11px]">{lead.email}</div>
                        )}
                      </td>

                      <td className="px-5 py-4 max-w-xs">
                        <div className="font-medium text-zinc-300 truncate" title={lead.intent || ""}>
                          {lead.intent || "General inquiry"}
                        </div>
                        <div className="text-zinc-500 text-[11px] truncate" title={lead.use_case || ""}>
                          {lead.use_case || "Evaluating solutions"}
                        </div>
                      </td>

                      <td className="px-5 py-4">
                        <div className="text-zinc-300 font-mono text-[11px]">
                          {lead.timeline || "Not provided"}
                        </div>
                        <div className="text-zinc-500 font-mono text-[11px]">
                          {lead.budget_range || "Not specified"}
                        </div>
                      </td>

                      <td className="px-5 py-4 text-center">
                        <span
                          className={`font-mono font-bold px-2 py-0.5 rounded-full border text-[11px] ${
                            lead.qualification_score >= 65
                              ? "bg-emerald-950/60 text-emerald-400 border-emerald-800"
                              : lead.qualification_score >= 30
                              ? "bg-amber-950/60 text-amber-400 border-amber-800"
                              : "bg-zinc-900 text-zinc-400 border-zinc-800"
                          }`}
                        >
                          {lead.qualification_score}/100
                        </span>
                      </td>

                      <td className="px-5 py-4">
                        <span
                          className={`font-mono text-[10px] px-2.5 py-1 rounded-full border ${getStatusBadge(
                            lead.lead_status
                          )}`}
                        >
                          {lead.lead_status}
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </main>

      <Footer />
    </div>
  );
}
