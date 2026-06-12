"use client";

import { useEffect, useState } from "react";
import { SIDE_NAV } from "@/lib/siteNav";

export type StoryActEvent = CustomEvent<{ actIndex: number }>;

export function useActiveSection() {
  const [active, setActive] = useState("hero");
  const [progress, setProgress] = useState(0);
  const [storyAct, setStoryAct] = useState(0);

  useEffect(() => {
    const obs = new IntersectionObserver(
      (entries) => {
        entries.forEach((e) => {
          if (e.isIntersecting) setActive(e.target.id);
        });
      },
      { threshold: 0.15, rootMargin: "-10% 0px -45% 0px" },
    );

    SIDE_NAV.forEach(({ id }) => {
      const el = document.getElementById(id);
      if (el) obs.observe(el);
    });

    const onScroll = () => {
      const scrollTop = window.scrollY;
      const docHeight = document.documentElement.scrollHeight - window.innerHeight;
      if (docHeight > 0) setProgress(Math.min(scrollTop / docHeight, 1));
    };

    const onStoryAct = (e: Event) => {
      const detail = (e as StoryActEvent).detail;
      if (detail && typeof detail.actIndex === "number") {
        setStoryAct(detail.actIndex);
        setActive("story");
      }
    };

    window.addEventListener("scroll", onScroll, { passive: true });
    window.addEventListener("scroll-story-act", onStoryAct);
    onScroll();

    return () => {
      obs.disconnect();
      window.removeEventListener("scroll", onScroll);
      window.removeEventListener("scroll-story-act", onStoryAct);
    };
  }, []);

  const activeIndex = SIDE_NAV.findIndex((i) => i.id === active);

  return { active, activeIndex, progress, storyAct };
}
