"use client";

import { useEffect, useId, useRef } from "react";
import { PAYPAL_CLIENT_ID, PAYPAL_HOSTED_BUTTON_ID } from "@/lib/api";

declare global {
  interface Window {
    paypal?: {
      HostedButtons: (opts: { hostedButtonId: string }) => {
        render: (selector: string) => Promise<void>;
      };
    };
  }
}

type Props = {
  className?: string;
};

export default function PayPalHostedButton({ className = "" }: Props) {
  const containerId = useId().replace(/:/g, "");
  const rendered = useRef(false);

  useEffect(() => {
    rendered.current = false;
    const selector = `#${containerId}`;
    const host = document.getElementById(containerId);
    if (host) host.innerHTML = "";

    const renderButton = () => {
      if (rendered.current || !window.paypal || !document.getElementById(containerId)) return;
      rendered.current = true;
      window.paypal
        .HostedButtons({ hostedButtonId: PAYPAL_HOSTED_BUTTON_ID })
        .render(selector)
        .catch(() => {
          rendered.current = false;
        });
    };

    const existing = document.getElementById("paypal-hosted-buttons-sdk");
    if (existing) {
      renderButton();
      return;
    }

    const script = document.createElement("script");
    script.id = "paypal-hosted-buttons-sdk";
    script.src = `https://www.paypal.com/sdk/js?client-id=${encodeURIComponent(
      PAYPAL_CLIENT_ID
    )}&components=hosted-buttons&disable-funding=venmo&currency=USD`;
    script.async = true;
    script.onload = renderButton;
    document.body.appendChild(script);
  }, [containerId]);

  return (
    <div className={`paypal-hosted-button-wrap w-full min-w-0 ${className}`}>
      <div
        id={containerId}
        className="paypal-hosted-button w-full min-w-[280px] min-h-[48px]"
      />
    </div>
  );
}
