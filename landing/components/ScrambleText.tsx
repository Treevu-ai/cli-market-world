"use client"
import { useState, useRef, useEffect } from "react"

interface Props {
  text: string
  as?: "span" | "div"
  className?: string
  duration?: number
}

const CHARS = "!@#$%^&*()_+-=[]{}|;:,.<>?/~`abcdefghijklmnopqrstuvwxyz0123456789"

export default function ScrambleText({ text, as: Tag = "span", className = "", duration = 0.6 }: Props) {
  const [display, setDisplay] = useState(text)
  const timer = useRef<ReturnType<typeof setInterval>>(undefined)
  const animating = useRef(false)

  const scramble = () => {
    if (animating.current) return
    animating.current = true
    let frame = 0
    const totalFrames = Math.floor(duration * 20)
    timer.current = setInterval(() => {
      frame++
      if (frame >= totalFrames) {
        setDisplay(text)
        clearInterval(timer.current)
        animating.current = false
        return
      }
      const progress = frame / totalFrames
      setDisplay(
        text
          .split("")
          .map((ch, i) => {
            if (ch === " ") return " "
            if (i / text.length < progress) return ch
            return CHARS[Math.floor(Math.random() * CHARS.length)]
          })
          .join(""),
      )
    }, 50)
  }

  useEffect(() => {
    if (timer.current) clearInterval(timer.current)
    animating.current = false
    setDisplay(text)
  }, [text])

  return (
    <Tag className={className} onMouseEnter={scramble}>
      {display}
    </Tag>
  )
}
