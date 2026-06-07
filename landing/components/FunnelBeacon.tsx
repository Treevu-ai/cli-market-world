"use client";

import { useEffect } from "react";
import { getFunnelSessionId } from "@/lib/funnel";

/** Ensures a funnel session id exists for landing → API event correlation. */
export default function FunnelBeacon() {
  useEffect(() => {
    getFunnelSessionId();
  }, []);
  return null;
}