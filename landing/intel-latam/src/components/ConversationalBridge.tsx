import React, { useState, useEffect, useRef } from "react";
import {
  MessageSquare, Send, CheckCheck, Sparkles,
  PhoneCall, Bot, HelpCircle
} from "lucide-react";
import { ChatMessage } from "../types";
import ScrollReveal from "./ScrollReveal";

export default function ConversationalBridge() {
  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      id: "msg-welcome",
      sender: "bot",
      text: "👋 ¡Hola! Soy tu Analista de Inteligencia de Mercados de CLI Market. Estoy listo para entregarte análisis de góndola en tiempo real en LATAM. Puedes hacerme preguntas sobre precios, tendencias o SKUs en lenguaje natural, o seleccionar una de las preguntas de ejemplo abajo.",
      timestamp: "19:52",
    }
  ]);
  
  const [inputValue, setInputValue] = useState("");
  const [isTyping, setIsTyping] = useState(false);
  const chatEndRef = useRef<HTMLDivElement>(null);

  // Auto scroll to bottom of chat
  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, isTyping]);

  // Preset queries requested by the user
  const PRESET_QUERIES = [
    {
      label: "☕ café en Perú",
      query: "¿Cuál es la tendencia de precio del café en Perú?",
    },
    {
      label: "🥛 leche en Lima",
      query: "Busca la mejor opción de leche evaporada en Lima",
    },
    {
      label: "🍺 cervezas en México",
      query: "Dame un comparativo de cervezas pack de 6 en México CDMX",
    }
  ];

  const handleSendMessage = async (textToSend: string) => {
    if (!textToSend.trim()) return;

    const timeString = new Date().toLocaleTimeString("es-ES", {
      hour: "2-digit",
      minute: "2-digit",
    });

    // Add user message
    const userMsgId = `msg-user-${Date.now()}`;
    setMessages((prev) => [
      ...prev,
      {
        id: userMsgId,
        sender: "user",
        text: textToSend,
        timestamp: timeString,
      },
    ]);

    setInputValue("");
    setIsTyping(true);

    try {
      // Fetch from our server endpoint
      const response = await fetch(`${import.meta.env.BASE_URL}api/chat`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ message: textToSend }),
      });

      const data = await response.json();
      
      setIsTyping(false);
      
      const botMsgId = `msg-bot-${Date.now()}`;
      setMessages((prev) => [
        ...prev,
        {
          id: botMsgId,
          sender: "bot",
          text: data.text || "Disculpa, no pude procesar la consulta en este momento.",
          timestamp: new Date().toLocaleTimeString("es-ES", { hour: "2-digit", minute: "2-digit" }),
        },
      ]);
    } catch (error) {
      console.error("Error connecting to retail engine:", error);
      setIsTyping(false);
      
      // Fallback in case of server offline/error during editing transitions
      const botMsgId = `msg-bot-err-${Date.now()}`;
      setMessages((prev) => [
        ...prev,
        {
          id: botMsgId,
          sender: "bot",
          text: "⚠️ *Error de conexión:* El motor CLI se encuentra reconfigurando servidores de góndola. Por favor intenta de nuevo en unos segundos.",
          timestamp: timeString,
        },
      ]);
    }
  };

  const handleFormSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (inputValue.trim()) {
      handleSendMessage(inputValue);
    }
  };

  return (
    <section className="bg-[#0a0a0a] text-[#f5f5f5] py-20 lg:py-28 border-b border-white/10" id="chat-section">
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-12 items-center">
          
          {/* Left Column: Descriptive text */}
          <ScrollReveal duration={0.8} className="lg:col-span-5 flex flex-col justify-center">
            <div className="text-left">
              <span className="font-mono text-[10px] font-bold text-[#bef264] uppercase tracking-widest bg-[#bef264]/5 border border-[#bef264]/20 px-3 py-1.5 rounded-sm">
                Canal Conversacional
              </span>
              
              <h2 className="mt-6 text-3xl font-extrabold tracking-tight text-white sm:text-4xl">
                Tu analista de mercado, ahora en WhatsApp.
              </h2>
              
              <p className="mt-4 text-xs sm:text-sm text-white/60 leading-relaxed">
                No necesitas un dashboard complejo para obtener respuestas urgentes de góndola.
                Pregúntanos en lenguaje natural y recibe inteligencia de precios procesada en segundos.
              </p>

              <div className="mt-8 space-y-4">
                <div className="flex items-start space-x-3.5">
                  <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-sm bg-white/5 text-[#bef264] border border-white/10 mt-1">
                    <Sparkles className="h-4.5 w-4.5" />
                  </div>
                  <div>
                    <h4 className="text-sm font-bold text-white uppercase tracking-wider font-mono">Formato Estructurado de Retail</h4>
                    <p className="text-xs text-white/50 mt-0.5">Recibe tablas comparativas de precios, brechas de góndola, alertas de desabastecimiento y sugerencias de tácticas.</p>
                  </div>
                </div>
              </div>

              <p className="mt-8 text-[10px] font-bold font-mono text-[#bef264] uppercase tracking-widest">
                — Desde una API robusta para tu equipo de Data Science hasta un chat para tu Gerente de Campo.
              </p>
            </div>
          </ScrollReveal>

          {/* Right Column: Live Interactive Sandbox Phone */}
          <ScrollReveal delay={0.15} duration={0.8} className="lg:col-span-7 flex flex-col items-center w-full">
            <div className="w-full flex flex-col items-center">
              
              <div className="w-full max-w-[480px] bg-[#121212] rounded-sm border border-white/10 shadow-2xl overflow-hidden flex flex-col aspect-[4/5] min-h-[500px]">
                
                {/* Terminal Chat Header */}
                <div className="bg-black text-white p-4 flex items-center justify-between shrink-0 border-b border-white/10 text-left">
                  <div className="flex items-center space-x-3">
                    <div className="relative h-10 w-10 rounded-sm bg-[#bef264]/10 flex items-center justify-center font-mono font-bold text-xs text-[#bef264] border border-[#bef264]/20">
                      CLI
                      <span className="absolute bottom-0 right-0 h-2 w-2 rounded-full bg-[#bef264] border-2 border-black"></span>
                    </div>
                    <div>
                      <div className="font-bold text-xs flex items-center space-x-1.5 font-mono uppercase tracking-wider">
                        <span>Analista CLI Market</span>
                        <span className="bg-[#bef264]/10 text-[#bef264] text-[8px] font-mono px-1 rounded-sm uppercase tracking-widest border border-[#bef264]/20">AI Live</span>
                      </div>
                      <div className="text-[10px] text-white/40 font-mono uppercase tracking-wide">
                        Autómata de góndolas • Online
                      </div>
                    </div>
                  </div>

                  <div className="flex items-center space-x-2 text-white/60">
                    <PhoneCall className="h-4 w-4 hover:text-white transition-colors cursor-pointer" />
                  </div>
                </div>

                {/* Chat Message Scroll Area */}
                <div className="flex-1 bg-[#0c0c0c] p-4 overflow-y-auto space-y-4 text-left">
                  
                  {messages.map((msg) => (
                    <div 
                      key={msg.id}
                      className={`flex flex-col ${msg.sender === "user" ? "items-end" : "items-start"}`}
                    >
                      <div 
                        className={`max-w-[85%] p-3 rounded-sm text-xs relative ${
                          msg.sender === "user" 
                            ? "bg-[#bef264] text-black rounded-tr-none font-medium shadow-sm" 
                            : "bg-white/5 text-white rounded-tl-none border border-white/10 shadow-sm"
                        }`}
                      >
                        {/* Message Content with simple Markdown rendering for tables/lines */}
                        <div className="whitespace-pre-line leading-relaxed font-sans text-xs">
                          {msg.text.split("\n").map((line, idx) => {
                            // Very basic markdown table formatting helper
                            if (line.trim().startsWith("|")) {
                              const cells = line.split("|").filter(cell => cell.trim() !== "");
                              const isHeader = idx === 0 || line.includes("---");
                              if (isHeader) return null; // let's simplify or skip dividers
                              return (
                                <div key={idx} className={`grid grid-cols-4 gap-1 py-1 font-mono text-[9px] border-b ${
                                  msg.sender === "user" ? "border-black/10" : "border-white/10"
                                }`}>
                                  {cells.map((c, cIdx) => (
                                    <span key={cIdx} className={cIdx === 0 
                                      ? (msg.sender === "user" ? "font-bold text-black/80 truncate text-left" : "font-bold text-white/80 truncate text-left") 
                                      : (msg.sender === "user" ? "text-right font-bold text-black" : "text-right font-bold text-[#bef264]")}>
                                      {c.trim().replace(/\*\*/g, "")}
                                    </span>
                                  ))}
                                </div>
                              );
                            }
                            
                            // Handle standard bold words **word**
                            const boldRegex = /\*\*(.*?)\*\*/g;
                            if (boldRegex.test(line)) {
                              const parts = line.split(boldRegex);
                              return (
                                <p key={idx} className="mb-1">
                                  {parts.map((part, pIdx) => pIdx % 2 === 1 
                                    ? <strong key={pIdx} className={msg.sender === "user" ? "font-extrabold text-black" : "font-extrabold text-[#bef264]"}>{part}</strong> 
                                    : part)}
                                </p>
                              );
                            }

                            return <p key={idx} className="mb-1">{line}</p>;
                          })}
                        </div>

                        <div className="flex items-center justify-end space-x-1 mt-2">
                          <span className={`text-[8px] font-mono ${msg.sender === "user" ? "text-black/60" : "text-white/40"}`}>{msg.timestamp}</span>
                          {msg.sender === "user" && <CheckCheck className="h-3 w-3 text-black/80" />}
                        </div>
                      </div>
                    </div>
                  ))}

                  {/* Loading state indicator */}
                  {isTyping && (
                    <div className="flex flex-col items-start">
                      <div className="bg-white/5 p-3 rounded-sm rounded-tl-none shadow-sm flex items-center space-x-2 text-xs border border-white/10">
                        <span className="text-white/40 font-mono italic text-[10px] animate-pulse">Estructurando reporte...</span>
                        <span className="flex space-x-1">
                          <span className="h-1.5 w-1.5 rounded-full bg-[#bef264] animate-bounce" style={{ animationDelay: '0ms' }}></span>
                          <span className="h-1.5 w-1.5 rounded-full bg-[#bef264] animate-bounce" style={{ animationDelay: '150ms' }}></span>
                          <span className="h-1.5 w-1.5 rounded-full bg-[#bef264] animate-bounce" style={{ animationDelay: '300ms' }}></span>
                        </span>
                      </div>
                    </div>
                  )}

                  <div ref={chatEndRef} />
                </div>

                {/* Preset pill questions selector */}
                <div className="bg-black/80 p-2.5 border-t border-white/10 overflow-x-auto whitespace-nowrap flex gap-2 shrink-0">
                  {PRESET_QUERIES.map((preset, index) => (
                    <button
                      key={index}
                      onClick={() => handleSendMessage(preset.query)}
                      disabled={isTyping}
                      className="bg-white/5 border border-white/10 hover:border-[#bef264] hover:text-[#bef264] text-[9px] font-mono text-white/80 px-3 py-1.5 rounded-sm cursor-pointer transition-all shrink-0 active:scale-95 disabled:opacity-50 uppercase tracking-wider"
                    >
                      {preset.label}
                    </button>
                  ))}
                </div>

                {/* Chat Form Entry Input */}
                <form onSubmit={handleFormSubmit} className="p-2.5 bg-black border-t border-white/10 flex items-center space-x-2 shrink-0">
                  <input
                    type="text"
                    value={inputValue}
                    onChange={(e) => setInputValue(e.target.value)}
                    disabled={isTyping}
                    placeholder={isTyping ? "Espere la respuesta..." : "Escribe tu consulta..."}
                    className="flex-1 bg-white/5 border border-white/10 rounded-sm py-2.5 px-4 text-xs font-mono text-white placeholder-white/30 focus:outline-none focus:border-[#bef264] focus:ring-1 focus:ring-[#bef264]/20 disabled:opacity-50"
                  />
                  
                  <button
                    type="submit"
                    disabled={!inputValue.trim() || isTyping}
                    className="h-10 w-10 rounded-sm bg-[#bef264] text-black flex items-center justify-center shadow hover:bg-[#d9f99d] transition-all shrink-0 cursor-pointer disabled:opacity-40"
                    id="chat-send-btn"
                  >
                    <Send className="h-4 w-4" />
                  </button>
                </form>

              </div>

              {/* Hint Box */}
              <div className="mt-4 flex items-center space-x-2 text-[10px] text-white/40 font-mono uppercase tracking-wider">
                <HelpCircle className="h-4 w-4 text-[#bef264]" />
                <span>Prueba ingresando cualquier producto o marca en el chat real de arriba.</span>
              </div>

            </div>
          </ScrollReveal>

        </div>
      </div>
    </section>
  );
}
