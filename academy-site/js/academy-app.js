/**
 * CLI Market Academy landing — app logic
 * Journey cliente + Optimus interactions + content-data
 */
(function () {
  "use strict";

  var reduced =
    (window.OptimusGraphics && window.OptimusGraphics.prefersReducedMotion) ||
    (window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches);
  var Content = window.AcademyContent || {};

  /* ——— Hero grid ——— */
  var grid = document.getElementById("hero-grid");
  if (grid) {
    for (var i = 1; i <= 8; i++) {
      var h = document.createElement("div");
      h.className = "h-line";
      h.style.top = 12.5 * i + "%";
      grid.appendChild(h);
    }
    for (var j = 1; j <= 12; j++) {
      var v = document.createElement("div");
      v.className = "v-line";
      v.style.left = 8.33 * j + "%";
      grid.appendChild(v);
    }
  }

  /* ——— Hero fade-in ——— */
  document.querySelectorAll(".hero-fade").forEach(function (el) {
    var d = parseInt(el.getAttribute("data-delay") || "0", 10);
    if (reduced) {
      el.classList.add("in");
      return;
    }
    setTimeout(function () {
      el.classList.add("in");
    }, d + 80);
  });

  /* ——— Rotating word with char-in ——— */
  var words = ["decidir", "comprar", "leer", "cotizar", "certificar"];
  var wordEl = document.getElementById("rotating-word");
  var wi = 0;
  function renderWord(word) {
    if (!wordEl) return;
    wordEl.innerHTML = "";
    if (reduced) {
      wordEl.textContent = word;
      return;
    }
    word.split("").forEach(function (ch, idx) {
      var s = document.createElement("span");
      s.className = "char";
      s.textContent = ch;
      s.style.animationDelay = idx * 45 + "ms";
      wordEl.appendChild(s);
    });
  }
  if (wordEl) {
    renderWord(words[0]);
    if (!reduced) {
      setInterval(function () {
        wi = (wi + 1) % words.length;
        renderWord(words[wi]);
      }, 2600);
    }
  }

  /* ——— Optimus canvases ——— */
  var G = window.OptimusGraphics;
  if (G) {
    var sphere = document.getElementById("canvas-sphere");
    var tetra = document.getElementById("canvas-tetra");
    var lattice = document.getElementById("canvas-lattice");
    var wave = document.getElementById("canvas-wave");
    if (sphere) G.AnimatedSphere(sphere);
    if (lattice && G.AnimatedLattice) G.AnimatedLattice(lattice);
    if (tetra) G.AnimatedTetrahedron(tetra);
    if (wave) G.AnimatedWave(wave, false);
  }

  /* Mid-section subtle grid (same as hero language) */
  var midGrid = document.getElementById("mid-signal-grid");
  if (midGrid) {
    for (var mi = 1; mi <= 6; mi++) {
      var mh = document.createElement("div");
      mh.className = "h-line";
      mh.style.top = (100 / 7) * mi + "%";
      midGrid.appendChild(mh);
    }
    for (var mj = 1; mj <= 10; mj++) {
      var mv = document.createElement("div");
      mv.className = "v-line";
      mv.style.left = 10 * mj + "%";
      midGrid.appendChild(mv);
    }
  }

  /* ——— Orbit nodes for AI SVG (feature 02) ——— */
  var orbit = document.getElementById("orbit-nodes");
  if (orbit) {
    for (var k = 0; k < 6; k++) {
      var angle = k * 60 * (Math.PI / 180);
      var radius = 50;
      var cx = 100 + Math.cos(angle) * radius;
      var cy = 80 + Math.sin(angle) * radius;
      var line = document.createElementNS("http://www.w3.org/2000/svg", "line");
      line.setAttribute("x1", "100");
      line.setAttribute("y1", "80");
      line.setAttribute("x2", String(cx));
      line.setAttribute("y2", String(cy));
      line.setAttribute("stroke", "currentColor");
      line.setAttribute("stroke-width", "1");
      line.setAttribute("opacity", "0.3");
      if (!reduced) {
        var a1 = document.createElementNS("http://www.w3.org/2000/svg", "animate");
        a1.setAttribute("attributeName", "opacity");
        a1.setAttribute("values", "0.3;0.8;0.3");
        a1.setAttribute("dur", "2s");
        a1.setAttribute("begin", k * 0.3 + "s");
        a1.setAttribute("repeatCount", "indefinite");
        line.appendChild(a1);
      }
      orbit.appendChild(line);
      var circle = document.createElementNS("http://www.w3.org/2000/svg", "circle");
      circle.setAttribute("cx", String(cx));
      circle.setAttribute("cy", String(cy));
      circle.setAttribute("r", "6");
      circle.setAttribute("fill", "none");
      circle.setAttribute("stroke", "currentColor");
      circle.setAttribute("stroke-width", "2");
      if (!reduced) {
        var a2 = document.createElementNS("http://www.w3.org/2000/svg", "animate");
        a2.setAttribute("attributeName", "r");
        a2.setAttribute("values", "6;8;6");
        a2.setAttribute("dur", "2s");
        a2.setAttribute("begin", k * 0.3 + "s");
        a2.setAttribute("repeatCount", "indefinite");
        circle.appendChild(a2);
      }
      orbit.appendChild(circle);
    }
  }

  /* ——— Stack dual marquee ——— */
  var stackItems = [
    { name: "CLI Market", cat: "Motor de datos" },
    { name: "market CLI", cat: "Terminal" },
    { name: "REST API", cat: "Integración" },
    { name: "MCP tools", cat: "Agentes" },
    { name: "SIRI", cat: "Método Intelligence" },
    { name: "DDM", cat: "Método Procure" },
    { name: "Workbook", cat: "Práctica" },
    { name: "Capstone", cat: "Rúbrica" },
    { name: "Nowcast 7d/30d", cat: "Señal" },
    { name: "Semáforo", cat: "Calidad de claim" },
    { name: "Góndola formal", cat: "Alcance" },
    { name: "No-IPC", cat: "Honestidad" },
  ];
  function fillStack(el, items) {
    if (!el) return;
    function track() {
      var t = document.createElement("div");
      t.className = "stack-track";
      items.forEach(function (it) {
        var card = document.createElement("div");
        card.className = "stack-card";
        card.innerHTML =
          '<div class="stack-name">' + it.name + "</div>" +
          '<div class="stack-cat">' + it.cat + "</div>";
        t.appendChild(card);
      });
      return t;
    }
    el.appendChild(track());
    el.appendChild(track());
  }
  fillStack(document.getElementById("stack-forward"), stackItems);
  fillStack(document.getElementById("stack-reverse"), stackItems.slice().reverse());

  /* ——— Syllabus expandable + keyConcept ——— */
  function fillSyllabus(el, modules) {
    if (!el || !modules || !modules.length) return;
    el.innerHTML = "";
    modules.forEach(function (m) {
      var li = document.createElement("li");
      li.setAttribute("role", "button");
      li.setAttribute("tabindex", "0");
      li.setAttribute("aria-expanded", "false");
      var keyHtml = m.key
        ? '<div class="mod-extra"><strong>Concepto clave</strong>' + m.key + "</div>"
        : m.desc
          ? '<div class="mod-extra"><strong>Detalle</strong>' + m.desc + "</div>"
          : "";
      li.innerHTML =
        '<span class="n">' +
        m.n +
        "</span>" +
        "<span>" +
        '<span class="mod-title">' +
        m.title +
        "</span>" +
        (m.desc ? '<span class="mod-desc">' + m.desc + "</span>" : "") +
        keyHtml +
        "</span>" +
        '<span class="mod-chev" aria-hidden="true">▾</span>';
      function toggle() {
        var open = li.classList.contains("open");
        el.querySelectorAll("li.open").forEach(function (other) {
          if (other !== li) {
            other.classList.remove("open");
            other.setAttribute("aria-expanded", "false");
          }
        });
        li.classList.toggle("open", !open);
        li.setAttribute("aria-expanded", open ? "false" : "true");
      }
      li.addEventListener("click", toggle);
      li.addEventListener("keydown", function (e) {
        if (e.key === "Enter" || e.key === " ") {
          e.preventDefault();
          toggle();
        }
      });
      el.appendChild(li);
    });
  }
  fillSyllabus(document.getElementById("syllabus-intel"), Content.intelModules);
  fillSyllabus(document.getElementById("syllabus-procure"), Content.procureModules);

  /* ——— Methodology steps SIRI / DDM ——— */
  function fillMethodSteps(el, steps) {
    if (!el || !steps || !steps.length) return;
    el.innerHTML = "";
    steps.forEach(function (s) {
      var div = document.createElement("div");
      div.className = "method-step";
      div.innerHTML =
        '<span class="ms-step">' +
        s.step +
        '</span><div class="ms-title">' +
        (s.title || s.step) +
        '</div><p class="ms-desc">' +
        s.desc +
        "</p>";
      el.appendChild(div);
    });
  }
  var ms = Content.methodologySteps || {};
  fillMethodSteps(document.getElementById("method-steps-intel"), ms.SIRI);
  fillMethodSteps(document.getElementById("method-steps-procure"), ms.DDM);

  /* ——— Moat pillars ——— */
  var pillars = Content.moatPillars;
  if (pillars) {
    var moatTitle = document.getElementById("moat-title");
    var moatSub = document.getElementById("moat-sub");
    var pillarsGrid = document.getElementById("pillars-grid");
    if (moatTitle && pillars.title) moatTitle.textContent = pillars.title;
    if (moatSub) moatSub.textContent = pillars.subtitle || "";
    if (pillarsGrid && pillars.pillars) {
      pillarsGrid.innerHTML = "";
      pillars.pillars.forEach(function (p) {
        var card = document.createElement("article");
        card.className = "pillar-card";
        card.innerHTML =
          '<div class="pillar-top"><span class="pn">Pilar ' +
          p.n +
          '</span><span class="pillar-accent">' +
          p.accent +
          "</span></div>" +
          '<span class="pillar-label">' +
          p.label +
          "</span>" +
          "<h3>" +
          p.title +
          "</h3>" +
          "<p>" +
          p.desc +
          "</p>";
        pillarsGrid.appendChild(card);
      });
    }
  }

  /* ——— Pipeline + demo log (SIMULACIÓN) ——— */
  var pipe = Content.pipeline;
  var pipeLogTimer = null;
  var pipeLogLines = [];
  var pipeLogIdx = 0;

  function pipeLogClass(line) {
    if (line.indexOf("⚡") !== -1) return "work";
    if (line.indexOf("✓") !== -1) return "ok";
    return "dim";
  }

  function renderPipeLog() {
    var body = document.getElementById("pipe-log-body");
    if (!body) return;
    body.innerHTML = "";
    pipeLogLines.forEach(function (line, i) {
      var span = document.createElement("span");
      span.className = "log-line " + pipeLogClass(line);
      span.style.animationDelay = Math.min(i * 30, 200) + "ms";
      span.textContent = line;
      body.appendChild(span);
    });
    body.scrollTop = body.scrollHeight;
  }

  function startPipeLog() {
    if (!pipe || !pipe.logRotate || !pipe.logRotate.length) return;
    if (pipeLogTimer) return;
    if (reduced) return;
    pipeLogTimer = setInterval(function () {
      var msg =
        "[" +
        new Date().toLocaleTimeString("es", { hour: "2-digit", minute: "2-digit", second: "2-digit" }) +
        "] " +
        pipe.logRotate[pipeLogIdx % pipe.logRotate.length];
      pipeLogIdx++;
      pipeLogLines.push(msg);
      if (pipeLogLines.length > 8) pipeLogLines.shift();
      renderPipeLog();
    }, 3800);
  }

  function stopPipeLog() {
    if (pipeLogTimer) {
      clearInterval(pipeLogTimer);
      pipeLogTimer = null;
    }
  }

  if (pipe) {
    var pt = document.getElementById("pipeline-title");
    var ps = document.getElementById("pipeline-sub");
    var pf = document.getElementById("pipeline-flow");
    if (pt && pipe.title) pt.textContent = pipe.title;
    if (ps && pipe.subtitle) ps.textContent = pipe.subtitle;
    if (pf && pipe.stages) {
      pf.innerHTML = "";
      pipe.stages.forEach(function (st, idx) {
        if (idx > 0) {
          var arr = document.createElement("div");
          arr.className = "pipeline-arrow";
          arr.setAttribute("aria-hidden", "true");
          arr.textContent = "→";
          pf.appendChild(arr);
        }
        var stage = document.createElement("div");
        stage.className = "pipeline-stage";
        stage.innerHTML =
          '<span class="pk">' +
          st.k +
          "</span><h3>" +
          st.title +
          "</h3><p>" +
          st.desc +
          "</p>";
        pf.appendChild(stage);
      });
    }

    var note = document.getElementById("pipe-log-note");
    if (note) note.textContent = pipe.logDisclaimer || "SIMULACIÓN DIDÁCTICA";
    pipeLogLines = (pipe.logSeed || []).slice();
    renderPipeLog();

    var pipeSection = document.getElementById("pipeline");
    if (pipeSection && "IntersectionObserver" in window) {
      var pio = new IntersectionObserver(
        function (entries) {
          entries.forEach(function (en) {
            if (en.isIntersecting) startPipeLog();
            else stopPipeLog();
          });
        },
        { threshold: 0.15 }
      );
      pio.observe(pipeSection);
    } else if (!reduced) {
      startPipeLog();
    }
  }

  /* ——— MCP cards + schema tabs ——— */
  var mcp = Content.mcp;
  if (mcp) {
    var mt = document.getElementById("mcp-title");
    var msub = document.getElementById("mcp-sub");
    var mg = document.getElementById("mcp-grid");
    var mcta = document.getElementById("mcp-cta-primary");
    if (mt && mcp.title) mt.textContent = mcp.title;
    if (msub && mcp.subtitle) msub.textContent = mcp.subtitle;
    if (mg && mcp.features) {
      mg.innerHTML = "";
      mcp.features.forEach(function (f) {
        var card = document.createElement("article");
        card.className = "mcp-card";
        card.innerHTML = "<h3>" + f.title + "</h3><p>" + f.desc + "</p>";
        mg.appendChild(card);
      });
    }
    if (mcta && mcp.ctaPrimary) {
      mcta.textContent = mcp.ctaPrimary.label;
      mcta.href = mcp.ctaPrimary.href;
    }

    var schemaNote = document.getElementById("mcp-schema-note");
    var schemaBody = document.getElementById("mcp-schema-body");
    var schemaTabs = document.querySelectorAll("[data-mcp-tab]");
    if (schemaNote && mcp.schemaNote) schemaNote.textContent = mcp.schemaNote;

    function showMcpSchema(tab) {
      if (!schemaBody || !mcp.schema) return;
      var payload = mcp.schema[tab] || mcp.schema.tools;
      try {
        schemaBody.textContent = JSON.stringify(payload, null, 2);
      } catch (e) {
        schemaBody.textContent = String(payload);
      }
      schemaTabs.forEach(function (btn) {
        var on = btn.getAttribute("data-mcp-tab") === tab;
        btn.classList.toggle("active", on);
        btn.setAttribute("aria-selected", on ? "true" : "false");
      });
    }
    schemaTabs.forEach(function (btn) {
      btn.addEventListener("click", function () {
        showMcpSchema(btn.getAttribute("data-mcp-tab") || "tools");
      });
    });
    showMcpSchema("tools");
  }

  /* ——— Workbook deliverables + rubric ——— */
  var wbGrid = document.getElementById("wb-grid");
  if (wbGrid && Content.workbookDeliverables) {
    wbGrid.innerHTML = "";
    Content.workbookDeliverables.forEach(function (d) {
      var c = document.createElement("div");
      c.className = "wb-card";
      c.innerHTML = "<h3>" + d.title + "</h3><p>" + d.desc + "</p>";
      wbGrid.appendChild(c);
    });
  }
  var rubricGrid = document.getElementById("rubric-grid");
  if (rubricGrid && Content.rubric) {
    rubricGrid.innerHTML = "";
    Content.rubric.forEach(function (r) {
      var item = document.createElement("div");
      item.className = "rubric-item";
      item.innerHTML =
        '<div class="rp">' +
        r.pct +
        "</div><h4>" +
        r.title +
        "</h4><p>" +
        r.desc +
        "</p>";
      rubricGrid.appendChild(item);
    });
  }

  /* ——— FAQ from content-data ——— */
  var faqList = document.getElementById("faq-list");
  if (faqList) {
    var faqs = Content.faq || [
      { q: "¿Cuánto tiempo necesito?", a: "~12–18 h por track · 2–3 semanas a 5–7 h/semana. Self-paced." },
      { q: "¿Necesito programar?", a: "No. Labs guiados en CLI/API/MCP. El centro es el juicio de desk." },
      { q: "¿Me cobran un plan al enviar el form?", a: "No. Waitlist de formación. Sin tarjeta. Producto después, solo si lo necesita." },
      { q: "¿Es el IPC?", a: "No. Góndola formal online. Enseñamos a no confundir las dos cosas." },
      { q: "¿Ambos tracks?", a: "Sí, en sprints separados." },
    ];
    faqList.innerHTML = "";
    faqs.forEach(function (f) {
      var d = document.createElement("details");
      d.className = "faq";
      d.innerHTML = "<summary>" + f.q + "</summary><p>" + f.a + "</p>";
      faqList.appendChild(d);
    });
  }

  /* ——— Nav scroll + active section ——— */
  var header = document.getElementById("site-header");
  var navLinks = document.querySelectorAll(".nav-links a[href^='#']");
  var sectionIds = [
    "para-usted",
    "lentes",
    "capabilities",
    "stack",
    "pipeline",
    "mcp",
    "tracks",
    "signal",
    "lab",
    "pedagogia",
    "how-it-works",
    "metrics",
    "moat",
    "semaforo",
    "capstone",
    "faq",
    "cta",
  ];

  function onScroll() {
    if (header) header.classList.toggle("is-scrolled", window.scrollY > 20);
    var y = window.scrollY + 120;
    var current = "";
    sectionIds.forEach(function (id) {
      var el = document.getElementById(id);
      if (el && el.offsetTop <= y) current = id;
    });
    navLinks.forEach(function (a) {
      var href = a.getAttribute("href") || "";
      a.classList.toggle("is-active", href === "#" + current);
    });
  }
  window.addEventListener("scroll", onScroll, { passive: true });
  onScroll();

  /* ——— Mobile menu ——— */
  var menuBtn = document.getElementById("menu-btn");
  var mobile = document.getElementById("mobile-menu");
  var iconMenu = document.getElementById("icon-menu");
  var iconClose = document.getElementById("icon-close");
  function setMenu(open) {
    if (!mobile) return;
    mobile.classList.toggle("open", open);
    if (iconMenu) iconMenu.style.display = open ? "none" : "block";
    if (iconClose) iconClose.style.display = open ? "block" : "none";
    document.body.style.overflow = open ? "hidden" : "";
  }
  if (menuBtn) {
    menuBtn.addEventListener("click", function () {
      setMenu(!mobile.classList.contains("open"));
    });
  }
  if (mobile) {
    mobile.querySelectorAll("[data-close]").forEach(function (a) {
      a.addEventListener("click", function () {
        setMenu(false);
      });
    });
  }

  /* ——— Tracks ——— */
  var trackSelect = document.getElementById("track");
  var rolSelect = document.getElementById("rol");
  var tabIntel = document.getElementById("tab-intel");
  var tabProcure = document.getElementById("tab-procure");
  var panelIntel = document.getElementById("panel-intel");
  var panelProcure = document.getElementById("panel-procure");

  function showTrackPanel(which) {
    var intel = which === "intel";
    if (panelIntel) panelIntel.classList.remove("active");
    if (panelProcure) panelProcure.classList.remove("active");
    var target = intel ? panelIntel : panelProcure;
    if (target) {
      void target.offsetWidth;
      target.classList.add("active");
    }
    if (tabIntel) tabIntel.classList.toggle("active", intel);
    if (tabProcure) tabProcure.classList.toggle("active", !intel);
  }
  if (tabIntel) {
    tabIntel.addEventListener("click", function () {
      showTrackPanel("intel");
    });
  }
  if (tabProcure) {
    tabProcure.addEventListener("click", function () {
      showTrackPanel("procure");
    });
  }

  function applyTrack(track, rol) {
    if (trackSelect && track) {
      if (track === "Ambos") trackSelect.value = "Ambos";
      else if (track === "Procure") trackSelect.value = "Procure";
      else trackSelect.value = "Intelligence";
    }
    if (rolSelect && rol) {
      for (var i = 0; i < rolSelect.options.length; i++) {
        if (rolSelect.options[i].value === rol || rolSelect.options[i].text === rol) {
          rolSelect.selectedIndex = i;
          break;
        }
      }
    }
    if (track === "Procure") showTrackPanel("procure");
    else if (track === "Intelligence") showTrackPanel("intel");
  }

  document.querySelectorAll("[data-track]").forEach(function (el) {
    el.addEventListener("click", function () {
      applyTrack(el.getAttribute("data-track"), el.getAttribute("data-rol") || "");
      var tracks = document.getElementById("tracks");
      if (tracks) tracks.scrollIntoView({ behavior: reduced ? "auto" : "smooth" });
      setTimeout(function () {
        var cta = document.getElementById("cta");
        if (cta && el.classList.contains("door")) {
          cta.scrollIntoView({ behavior: reduced ? "auto" : "smooth" });
        }
      }, 450);
    });
  });
  document.querySelectorAll("[data-prefill]").forEach(function (el) {
    el.addEventListener("click", function () {
      applyTrack(el.getAttribute("data-prefill"), "");
    });
  });

  /* ——— Quiz ——— */
  var quiz = document.getElementById("quiz");
  var openQuiz = document.getElementById("open-quiz");
  if (quiz && openQuiz) {
    quiz.innerHTML =
      "<h4>Diagnóstico rápido</h4>" +
      qBlock(1, "¿Su trabajo termina en una orden de compra?", [
        ["procure", "Sí, con frecuencia"],
        ["intel", "Casi nunca"],
        ["both", "A veces"],
      ]) +
      qBlock(2, "¿Qué le duele más esta semana?", [
        ["procure", "Cotizar y elegir proveedor"],
        ["intel", "No sé si el mercado se movió"],
        ["intel", "Defender un número en un comité"],
      ]) +
      qBlock(3, "¿Qué entregable le serviría mañana?", [
        ["procure", "Carrito / orden optimizada"],
        ["intel", "Brief de 1 página + riesgo"],
        ["both", "Los dos, en momentos distintos"],
      ]) +
      '<div class="quiz-result" id="quiz-result"></div>';

    function qBlock(id, title, opts) {
      var html =
        '<div class="quiz-q" data-q="' + id + '"><p>' + id + ". " + title + '</p><div class="quiz-opts">';
      opts.forEach(function (o) {
        html += '<button type="button" data-score="' + o[0] + '">' + o[1] + "</button>";
      });
      return html + "</div></div>";
    }

    openQuiz.addEventListener("click", function () {
      quiz.classList.add("open");
      quiz.scrollIntoView({ behavior: reduced ? "auto" : "smooth", block: "nearest" });
    });

    var scores = { procure: 0, intel: 0, both: 0 };
    var answered = {};
    quiz.querySelectorAll(".quiz-q").forEach(function (q) {
      var qid = q.getAttribute("data-q");
      q.querySelectorAll("button").forEach(function (btn) {
        btn.addEventListener("click", function () {
          q.querySelectorAll("button").forEach(function (b) {
            b.classList.remove("selected");
          });
          btn.classList.add("selected");
          if (answered[qid]) scores[answered[qid]]--;
          var sc = btn.getAttribute("data-score");
          answered[qid] = sc;
          scores[sc]++;
          if (Object.keys(answered).length >= 3) {
            var result = document.getElementById("quiz-result");
            var winner = "intel";
            var label = "Intelligence";
            if (scores.both >= scores.intel && scores.both >= scores.procure) {
              winner = "both";
              label = "Ambos (secuencial)";
            } else if (scores.procure > scores.intel) {
              winner = "procure";
              label = "Procure";
            }
            result.classList.add("show");
            result.innerHTML =
              "Recomendación: <strong>" +
              label +
              "</strong>. " +
              '<button type="button" id="quiz-apply" style="text-decoration:underline;font-weight:600;margin-left:0.35rem">Aplicar y ver syllabus</button>';
            document.getElementById("quiz-apply").addEventListener("click", function () {
              if (winner === "procure") applyTrack("Procure", "Abastecimiento / Compras");
              else if (winner === "both") applyTrack("Ambos", "");
              else applyTrack("Intelligence", "Pricing / Revenue");
              document.getElementById("tracks").scrollIntoView({
                behavior: reduced ? "auto" : "smooth",
              });
            });
          }
        });
      });
    });
  }

  /* ——— How it works (steps + code reveal + light syntax) ——— */
  var steps = [
    {
      roman: "I",
      title: "Diagnóstico",
      description: "Mapa de rol multi-lente y autoevaluación en el workbook.",
      file: "diagnostico.md",
      code:
        "# Parte 0 — workbook\n" +
        "rol: pricing | compras | research\n" +
        "pais: PE\n" +
        "track: Intelligence | Procure\n" +
        "meta: brief_semanal | compra_trimestre",
    },
    {
      roman: "II",
      title: "Módulos 00–08",
      description: "Problema → concepto → demo → práctica → reflexión.",
      file: "modulo-04.sh",
      code:
        "# Lab nowcast\n" +
        "market intel brief \\\n" +
        "  --country PE \\\n" +
        "  --line supermercados \\\n" +
        "  --days 7\n" +
        "# → headline · 7d vs 30d · calidad",
    },
    {
      roman: "III",
      title: "Labs reales",
      description: "CLI, API o MCP. Todo número sale de una tool call.",
      file: "lab-risk.sh",
      code:
        "market price risk --country PE --days 7\n" +
        "market trending --country PE --limit 10\n" +
        "market scores --country PE\n" +
        "# semáforo: usar | monitorear | no publicar",
    },
    {
      roman: "IV",
      title: "Capstone",
      description: "Pack con rúbrica. Claim falso de IPC = no aprueba.",
      file: "capstone.yaml",
      code:
        "pack:\n" +
        "  - desk_brief\n" +
        "  - risk_memo\n" +
        "  - category_one_pager\n" +
        "  - methods_quality\n" +
        "rubrica_min: 80\n" +
        "fallo_critico: inventar_ipc",
    },
    {
      roman: "V",
      title: "Ritual 90 días",
      description: "Brief, risk o compras según rol — hábito de desk.",
      file: "ritual-90d.md",
      code:
        "## Lunes 08:00\n" +
        "1. intel brief 7d\n" +
        "2. semáforo de calidad\n" +
        "3. 3 bullets por lente\n" +
        "4. archivar o publicar\n" +
        "# producto: solo si el rol lo pide",
    },
  ];

  var howSteps = document.getElementById("how-steps");
  var howCodeBody = document.getElementById("how-code-body");
  var howCodeName = document.getElementById("how-code-name");
  var activeStep = 0;
  var stepTimer = null;

  function tokenizeLine(line) {
    if (/^\s*#/.test(line) || /^\s*##/.test(line)) {
      return [{ t: "tok-comment", s: line }];
    }
    var tokens = [];
    var rest = line;
    // yaml-ish key:
    var keyMatch = rest.match(/^(\s*)([a-zA-Z_][\w]*:)(\s*)(.*)$/);
    if (keyMatch) {
      tokens.push({ t: "", s: keyMatch[1] });
      tokens.push({ t: "tok-key", s: keyMatch[2] });
      tokens.push({ t: "", s: keyMatch[3] });
      if (keyMatch[4]) tokens.push({ t: "tok-str", s: keyMatch[4] });
      return tokens;
    }
    // shell command start
    var parts = rest.split(/(\s+)/);
    var firstCmd = true;
    parts.forEach(function (p) {
      if (!p) return;
      if (/^\s+$/.test(p)) {
        tokens.push({ t: "", s: p });
        return;
      }
      if (p.charAt(0) === "-" && p.length > 1) {
        tokens.push({ t: "tok-flag", s: p });
        firstCmd = false;
      } else if (firstCmd && /^[a-zA-Z]/.test(p)) {
        tokens.push({ t: "tok-cmd", s: p });
        firstCmd = false;
      } else if (/^\d+$/.test(p) || /^[A-Z]{2}$/.test(p)) {
        tokens.push({ t: "tok-str", s: p });
      } else {
        tokens.push({ t: "", s: p });
      }
    });
    return tokens.length ? tokens : [{ t: "", s: line }];
  }

  function renderCode(step) {
    if (!howCodeBody) return;
    if (howCodeName) howCodeName.textContent = step.file;
    howCodeBody.innerHTML = "";
    var lines = step.code.split("\n");
    lines.forEach(function (line, lineIndex) {
      var row = document.createElement("div");
      row.className = "line";
      if (!reduced) row.style.animationDelay = lineIndex * 80 + "ms";
      var ln = document.createElement("span");
      ln.className = "ln";
      ln.textContent = String(lineIndex + 1);
      row.appendChild(ln);

      var tokens = tokenizeLine(line);
      var charIndex = 0;
      tokens.forEach(function (tok) {
        tok.s.split("").forEach(function (ch) {
          var c = document.createElement("span");
          c.className = "c" + (tok.t ? " " + tok.t : "");
          c.textContent = ch === " " ? "\u00A0" : ch;
          if (!reduced) {
            c.style.animationDelay = lineIndex * 80 + charIndex * 12 + "ms";
          }
          row.appendChild(c);
          charIndex++;
        });
      });
      if (line.length === 0) {
        var empty = document.createElement("span");
        empty.className = "c";
        empty.innerHTML = "&nbsp;";
        row.appendChild(empty);
      }
      howCodeBody.appendChild(row);
    });
  }

  function setActiveStep(index) {
    activeStep = index;
    if (!howSteps) return;
    howSteps.querySelectorAll(".how-step").forEach(function (el, i) {
      el.classList.toggle("active", i === index);
      var bar = el.querySelector(".how-progress > i");
      if (bar) {
        bar.style.animation = "none";
        void bar.offsetWidth;
        if (i === index && !reduced) {
          bar.style.animation = "progress 5s linear forwards";
        } else if (i === index && reduced) {
          bar.style.width = "100%";
        }
      }
    });
    renderCode(steps[index]);
  }

  if (howSteps) {
    steps.forEach(function (step, index) {
      var btn = document.createElement("button");
      btn.type = "button";
      btn.className = "how-step" + (index === 0 ? " active" : "");
      btn.innerHTML =
        '<div class="how-step-inner">' +
        '<span class="roman">' +
        step.roman +
        "</span>" +
        "<div><h3>" +
        step.title +
        "</h3>" +
        "<p>" +
        step.description +
        "</p>" +
        '<div class="how-progress"><i></i></div></div></div>';
      btn.addEventListener("click", function () {
        clearInterval(stepTimer);
        setActiveStep(index);
        startStepTimer();
      });
      howSteps.appendChild(btn);
    });
    setActiveStep(0);
    function startStepTimer() {
      clearInterval(stepTimer);
      if (reduced) return;
      stepTimer = setInterval(function () {
        setActiveStep((activeStep + 1) % steps.length);
      }, 5000);
    }
    startStepTimer();
  }

  /* ——— Metric counters ——— */
  var metricsEl = document.getElementById("metrics-big");
  var metricsDone = false;
  if (metricsEl && G && "IntersectionObserver" in window) {
    var mio = new IntersectionObserver(
      function (entries) {
        entries.forEach(function (en) {
          if (en.isIntersecting && !metricsDone) {
            metricsDone = true;
            metricsEl.querySelectorAll("[data-counter]").forEach(function (el) {
              var end = parseInt(el.getAttribute("data-end"), 10) || 0;
              var suffix = el.getAttribute("data-suffix") || "";
              var prefix = el.getAttribute("data-prefix") || "";
              G.animateCounter(el, end, 1800, suffix, prefix);
            });
          }
        });
      },
      { threshold: 0.35 }
    );
    mio.observe(metricsEl);
  } else if (metricsEl) {
    metricsEl.querySelectorAll("[data-counter]").forEach(function (el) {
      var end = parseInt(el.getAttribute("data-end"), 10) || 0;
      var suffix = el.getAttribute("data-suffix") || "";
      var prefix = el.getAttribute("data-prefix") || "";
      el.textContent = prefix + end.toLocaleString("es") + suffix;
    });
  }

  /* ——— CTA spotlight (Optimus) ——— */
  var ctaFrame = document.getElementById("cta-frame");
  var spotlight = document.getElementById("cta-spotlight");
  if (ctaFrame && spotlight && !reduced) {
    ctaFrame.addEventListener("mousemove", function (e) {
      var rect = ctaFrame.getBoundingClientRect();
      var x = ((e.clientX - rect.left) / rect.width) * 100;
      var y = ((e.clientY - rect.top) / rect.height) * 100;
      spotlight.style.background =
        "radial-gradient(600px circle at " +
        x +
        "% " +
        y +
        "%, rgba(20,18,15,0.14), transparent 40%)";
    });
  }

  /* ——— Form ——— */
  var ACADEMY_API_URL = "https://cli-market-api.fly.dev";
  var form = document.getElementById("waitlist-form");
  if (form) {
    form.addEventListener("submit", function (e) {
      e.preventDefault();
      var success = document.getElementById("form-success");
      var error = document.getElementById("form-error");
      var submitBtn = form.querySelector('button[type="submit"]');
      if (error) error.classList.remove("show");
      if (success) success.classList.remove("show");
      if (submitBtn) submitBtn.disabled = true;

      var body = {
        email: form.querySelector("#email").value,
        rol: form.querySelector("#rol").value,
        track: form.querySelector("#track").value,
        pais: form.querySelector("#pais").value,
        empresa: form.querySelector("#empresa").value,
      };

      fetch(ACADEMY_API_URL + "/v1/academy/waitlist", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body),
      })
        .then(function (res) {
          return res.json().then(function (data) {
            if (!res.ok) {
              throw new Error(
                (data && data.detail) || "No se pudo registrar su solicitud."
              );
            }
            return data;
          });
        })
        .then(function () {
          if (success) success.classList.add("show");
          form.reset();
        })
        .catch(function (err) {
          if (error) {
            error.textContent =
              (err && err.message) ||
              "No se pudo registrar su solicitud. Intente de nuevo.";
            error.classList.add("show");
          }
        })
        .finally(function () {
          if (submitBtn) submitBtn.disabled = false;
        });
    });
  }

  /* ——— Reveal on scroll (stagger siblings) ——— */
  var reveals = document.querySelectorAll(".reveal");
  if ("IntersectionObserver" in window && !reduced) {
    var io = new IntersectionObserver(
      function (entries) {
        entries.forEach(function (en) {
          if (en.isIntersecting) {
            en.target.classList.add("in");
            io.unobserve(en.target);
          }
        });
      },
      { threshold: 0.1, rootMargin: "0px 0px -40px 0px" }
    );
    reveals.forEach(function (el, idx) {
      if (!el.hasAttribute("data-delay")) {
        el.setAttribute("data-delay", String(Math.min(idx % 4, 3) || ""));
        if (!(idx % 4)) el.removeAttribute("data-delay");
      }
      io.observe(el);
    });
  } else {
    reveals.forEach(function (el) {
      el.classList.add("in");
    });
  }

  /* ——— Feature row stagger via CSS var ——— */
  document.querySelectorAll(".feature-row").forEach(function (row, i) {
    row.style.setProperty("--stagger", String(i));
    row.setAttribute("data-stagger", "");
  });

  /* ——— Multi-lente roles (AI Studio) ——— */
  var roleTabs = document.getElementById("role-tabs");
  var roles = Content.roles || [];
  var selectedRoleId = roles[0] ? roles[0].id : "pricing";

  function renderRole(id) {
    var role = null;
    for (var r = 0; r < roles.length; r++) {
      if (roles[r].id === id) {
        role = roles[r];
        break;
      }
    }
    if (!role) return;
    selectedRoleId = id;
    var badge = document.getElementById("role-badge");
    var title = document.getElementById("role-title");
    var desc = document.getElementById("role-desc");
    var tip = document.getElementById("role-tip");
    var ex = document.getElementById("role-example");
    if (badge) badge.textContent = role.badge || "";
    if (title) title.textContent = "¿Cómo aplica " + role.name + " los datos del moat?";
    if (desc) desc.textContent = role.description || "";
    if (tip) tip.textContent = role.tip || "";
    if (ex) ex.textContent = role.example || "";
    if (roleTabs) {
      roleTabs.querySelectorAll(".role-tab").forEach(function (btn) {
        var on = btn.getAttribute("data-role") === id;
        btn.classList.toggle("active", on);
        btn.setAttribute("aria-selected", on ? "true" : "false");
      });
    }
    // Prefill form track/rol without forcing scroll
    if (role.track === "Procure") {
      if (trackSelect) trackSelect.value = "Procure";
      showTrackPanel("procure");
    } else if (role.track === "Intelligence") {
      if (trackSelect) trackSelect.value = "Intelligence";
      showTrackPanel("intel");
    }
    if (rolSelect && role.name) {
      for (var ri = 0; ri < rolSelect.options.length; ri++) {
        if (
          rolSelect.options[ri].text.indexOf(role.name.split(" / ")[0]) !== -1 ||
          rolSelect.options[ri].text === role.name
        ) {
          rolSelect.selectedIndex = ri;
          break;
        }
      }
    }
  }

  if (roleTabs && roles.length) {
    roles.forEach(function (role, idx) {
      var btn = document.createElement("button");
      btn.type = "button";
      btn.className = "role-tab" + (idx === 0 ? " active" : "");
      btn.setAttribute("role", "tab");
      btn.setAttribute("data-role", role.id);
      btn.setAttribute("aria-selected", idx === 0 ? "true" : "false");
      btn.textContent = role.name;
      btn.addEventListener("click", function () {
        renderRole(role.id);
      });
      roleTabs.appendChild(btn);
    });
    // First paint without prefill-scroll
    var first = roles[0];
    selectedRoleId = first.id;
    var badge = document.getElementById("role-badge");
    var title = document.getElementById("role-title");
    var desc = document.getElementById("role-desc");
    var tip = document.getElementById("role-tip");
    var ex = document.getElementById("role-example");
    if (badge) badge.textContent = first.badge || "";
    if (title) title.textContent = "¿Cómo aplica " + first.name + " los datos del moat?";
    if (desc) desc.textContent = first.description || "";
    if (tip) tip.textContent = first.tip || "";
    if (ex) ex.textContent = first.example || "";
  }

  /* ——— Pedagogy cards (AI Studio) ——— */
  var pedGrid = document.getElementById("pedagogy-grid");
  var pedagogy = Content.pedagogy || [
    { n: "01", title: "El problema", text: "Caso de fallo o sesgo real de retail / compras / pricing en LATAM." },
    { n: "02", title: "El concepto", text: "Fundamentos DDM o SIRI para enmarcar el juicio." },
    { n: "03", title: "La demo", text: "Queries reales (o lab guiado) contra góndola formal." },
    { n: "04", title: "La práctica", text: "El alumno corre el lab y documenta en el workbook." },
    { n: "05", title: "La reflexión", text: "¿Qué claim puedo emitir — y cuál está prohibido?" },
  ];
  if (pedGrid) {
    pedGrid.innerHTML = "";
    pedagogy.forEach(function (p) {
      var card = document.createElement("article");
      card.className = "ped-card";
      card.innerHTML =
        '<div class="n">' +
        p.n +
        "</div><h3>" +
        p.title +
        "</h3><p>" +
        p.text +
        "</p>";
      pedGrid.appendChild(card);
    });
  }

  /* ——— Interactive lab terminal + semáforo (AI Studio) ——— */
  var labOutput = document.getElementById("lab-output");
  var labStatus = document.getElementById("lab-status");
  var labRunning = false;
  var labActiveCmd = "";
  var T = Content.terminal || {};

  var coverageSlider = document.getElementById("coverage-slider");
  var confidenceSlider = document.getElementById("confidence-slider");
  var informalToggle = document.getElementById("informal-toggle");
  var coverageVal = document.getElementById("coverage-val");
  var confidenceVal = document.getElementById("confidence-val");

  function coverage() {
    return coverageSlider ? parseInt(coverageSlider.value, 10) : 88;
  }
  function confidence() {
    return confidenceSlider ? parseInt(confidenceSlider.value, 10) : 92;
  }
  function informal() {
    return informalToggle ? informalToggle.checked : false;
  }

  function getSemStatus() {
    var sm = Content.semaforo || {};
    if (informal()) {
      return {
        level: "r",
        icon: "×",
        label: (sm.informal && sm.informal.label) || "Rechazado (claim inválido)",
        desc:
          (sm.informal && sm.informal.desc) ||
          "Prohibido extrapolar e-commerce formal a informal, ferias o inflación nacional sin ser el IPC.",
      };
    }
    var cov = coverage();
    var conf = confidence();
    if (cov >= 80 && conf >= 85) {
      return {
        level: "g",
        icon: "✓",
        label: (sm.green && sm.green.label) || "Semáforo verde (usar)",
        desc:
          (sm.green && sm.green.desc) ||
          "Cobertura y confianza altas. Publicación externa posible con disclaimer de canal formal y as_of.",
      };
    }
    if (cov >= 60 || conf >= 70) {
      return {
        level: "a",
        icon: "!",
        label: (sm.yellow && sm.yellow.label) || "Semáforo amarillo (monitorear)",
        desc:
          (sm.yellow && sm.yellow.desc) ||
          "Muestra parcial. Preferible uso interno o con advertencia explícita de cobertura.",
      };
    }
    return {
      level: "r",
      icon: "×",
      label: (sm.red && sm.red.label) || "Semáforo rojo (no publicar)",
      desc:
        (sm.red && sm.red.desc) ||
        "Confianza o cobertura insuficiente. No sostener claims externos con este corte.",
    };
  }

  function updateSemUI() {
    if (coverageVal) coverageVal.textContent = coverage() + "%";
    if (confidenceVal) confidenceVal.textContent = confidence() + "%";
    var st = getSemStatus();
    var box = document.getElementById("sem-status");
    var icon = document.getElementById("sem-icon");
    var label = document.getElementById("sem-label");
    var desc = document.getElementById("sem-desc");
    if (box) box.setAttribute("data-level", st.level);
    if (icon) icon.textContent = st.icon;
    if (label) label.textContent = st.label;
    if (desc) desc.textContent = st.desc;
  }

  function qualityOutput() {
    var cov = coverage();
    var conf = confidence();
    var inf = informal();
    var st = getSemStatus();
    var tag =
      st.level === "g"
        ? "[CORRECTO] VERDE (USAR)"
        : st.level === "a"
          ? "[ADVERTENCIA] AMARILLO (MONITOREAR)"
          : inf
            ? "[CRÍTICO] RECHAZADO"
            : "[BLOQUEADO] ROJO (NO PUBLICAR)";
    return (
      "$ quality-check --coverage " +
      cov +
      " --confidence " +
      conf +
      " --informal=" +
      (inf ? "true" : "false") +
      "\n\n" +
      "[EVAL] Validez metodológica (simulación didáctica — no API live)…\n\n" +
      "  " +
      tag +
      "\n" +
      "  " +
      st.desc +
      "\n\n" +
      "Umbrales orientativos Academy:\n" +
      "  Verde: ≥80% cobertura y ≥85% confidence\n" +
      "  Amarillo: ≥60% cobertura o ≥70% confidence\n" +
      "  Informal / IPC falso: siempre bloqueado\n\n" +
      "[ADVERTENCIA ACADEMY] Solo góndola formal online.\n" +
      "En el curso se reemplaza por el quality block del payload real."
    );
  }

  function cmdText(cmd) {
    if (cmd === "intel") return T.intel || "market intel brief — simulación no disponible";
    if (cmd === "procure") return T.procure || "procure cart — simulación no disponible";
    if (cmd === "quality") return qualityOutput();
    return "Comando no reconocido.";
  }

  function setLabText(text) {
    if (labOutput) labOutput.textContent = text;
  }

  function runLab(cmd, instant) {
    if (labRunning && !instant) return;
    labActiveCmd = cmd;
    document.querySelectorAll(".lab-cmd").forEach(function (b) {
      b.classList.toggle("active", b.getAttribute("data-cmd") === cmd);
    });
    if (instant || reduced) {
      setLabText(cmdText(cmd));
      if (labStatus) labStatus.hidden = true;
      labRunning = false;
      return;
    }
    labRunning = true;
    document.querySelectorAll(".lab-cmd").forEach(function (b) {
      b.disabled = true;
    });
    if (labStatus) labStatus.hidden = false;
    setLabText(
      "Procesando: " +
        (cmd === "intel" ? "market intel" : cmd === "procure" ? "procure cart" : "quality-check") +
        "\nConectando con sandbox didáctico (no live)…"
    );
    setTimeout(function () {
      setLabText(cmdText(cmd));
      if (labStatus) labStatus.hidden = true;
      labRunning = false;
      document.querySelectorAll(".lab-cmd").forEach(function (b) {
        b.disabled = false;
      });
    }, 900);
  }

  if (labOutput) {
    setLabText(
      T.intro ||
        "CLI Market Academy · sandbox didáctico\nSeleccione un comando para ver la estructura de salida de cada track.\nNúmeros = simulación; en el curso se usan tool calls reales."
    );
  }

  document.querySelectorAll(".lab-cmd").forEach(function (btn) {
    btn.addEventListener("click", function () {
      runLab(btn.getAttribute("data-cmd"), false);
    });
  });

  function onSemChange() {
    updateSemUI();
    if (labActiveCmd === "quality") runLab("quality", true);
  }
  if (coverageSlider) coverageSlider.addEventListener("input", onSemChange);
  if (confidenceSlider) confidenceSlider.addEventListener("input", onSemChange);
  if (informalToggle) informalToggle.addEventListener("change", onSemChange);
  updateSemUI();

  var syncBtn = document.getElementById("sem-sync-lab");
  if (syncBtn) {
    syncBtn.addEventListener("click", function () {
      runLab("quality", false);
      var lab = document.getElementById("lab");
      if (lab) lab.scrollIntoView({ behavior: reduced ? "auto" : "smooth", block: "center" });
    });
  }
})();
