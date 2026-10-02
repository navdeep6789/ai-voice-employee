"use client";

import { BookingDetails } from "@/types";
import { CalendarCheck, Clock, CheckCircle2 } from "lucide-react";

interface BookingConfirmationCardProps {
  booking: BookingDetails;
}

export function BookingConfirmationCard({ booking }: BookingConfirmationCardProps) {
  const startDate = new Date(booking.confirmed_start);
  const formattedDate = startDate.toLocaleDateString("en-US", {
    weekday: "long",
    month: "short",
    day: "numeric",
  });
  const formattedTime = startDate.toLocaleTimeString("en-US", {
    hour: "2-digit",
    minute: "2-digit",
  });

  return (
    <div className="bg-gradient-to-br from-emerald-950/40 via-zinc-900 to-zinc-950 border border-emerald-500/40 rounded-xl p-4 shadow-md animate-in fade-in slide-in-from-top-2 duration-300">
      <div className="flex items-center space-x-2 pb-2 border-b border-emerald-800/40 mb-3">
        <div className="w-5 h-5 rounded-full bg-emerald-500/20 flex items-center justify-center">
          <CalendarCheck className="w-3.5 h-3.5 text-emerald-400" />
        </div>
        <h4 className="text-xs font-semibold text-emerald-300 font-mono uppercase tracking-wider">
          Meeting Booked in Calendar
        </h4>
      </div>

      <div className="space-y-2 text-xs">
        <div className="text-sm font-semibold text-white">
          {booking.meeting_type || "AI Solutions Consultation"}
        </div>

        <div className="flex items-center space-x-2 text-zinc-300">
          <Clock className="w-3.5 h-3.5 text-emerald-400 shrink-0" />
          <span className="font-mono">{formattedDate} at {formattedTime}</span>
        </div>

        <div className="text-[11px] text-zinc-400 pt-1 border-t border-zinc-800/60 flex items-center justify-between">
          <span>Attendee: <strong className="text-zinc-200">{booking.name}</strong> ({booking.email})</span>
          <span className="flex items-center text-emerald-400 font-mono text-[10px]">
            <CheckCircle2 className="w-3 h-3 mr-1" /> CRM Synced
          </span>
        </div>
      </div>
    </div>
  );
}
