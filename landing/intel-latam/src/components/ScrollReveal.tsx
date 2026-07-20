import React, { ReactNode } from "react";
import { motion } from "motion/react";

interface ScrollRevealProps {
  children: ReactNode;
  className?: string;
  delay?: number;
  duration?: number;
  direction?: "up" | "down" | "left" | "right" | "none";
  distance?: number;
  triggerOnce?: boolean;
  key?: React.Key;
}

export default function ScrollReveal({
  children,
  className = "",
  delay = 0,
  duration = 0.8,
  direction = "up",
  distance = 30,
  triggerOnce = true,
}: ScrollRevealProps) {
  // Determine coordinate offsets based on direction
  const offsets = {
    up: { y: distance, x: 0 },
    down: { y: -distance, x: 0 },
    left: { x: distance, y: 0 },
    right: { x: -distance, y: 0 },
    none: { x: 0, y: 0 },
  };

  const selectedOffset = offsets[direction];

  return (
    <motion.div
      initial={{
        opacity: 0,
        x: selectedOffset.x,
        y: selectedOffset.y,
      }}
      whileInView={{
        opacity: 1,
        x: 0,
        y: 0,
      }}
      viewport={{ once: triggerOnce, margin: "-80px" }}
      transition={{
        duration: duration,
        delay: delay,
        ease: [0.16, 1, 0.3, 1], // Custom premium ease-out
      }}
      className={className}
    >
      {children}
    </motion.div>
  );
}
