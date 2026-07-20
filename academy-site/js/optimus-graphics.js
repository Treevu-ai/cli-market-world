/**
 * Graphics & animations ported from Optimus template
 * (AnimatedSphere, AnimatedTetrahedron, AnimatedWave + helpers)
 * + pause when off-screen, prefers-reduced-motion, DPR-aware resize
 */
(function (global) {
  "use strict";

  var prefersReduced =
    typeof window.matchMedia === "function" &&
    window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  function setupCanvas(canvas) {
    var ctx = canvas.getContext("2d");
    if (!ctx) return null;
    var dpr = Math.min(window.devicePixelRatio || 1, 2);
    var rect = canvas.getBoundingClientRect();
    var w = Math.max(1, Math.floor(rect.width));
    var h = Math.max(1, Math.floor(rect.height));
    var need =
      canvas.width !== Math.floor(w * dpr) ||
      canvas.height !== Math.floor(h * dpr);
    if (need) {
      canvas.width = Math.floor(w * dpr);
      canvas.height = Math.floor(h * dpr);
    }
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    return { ctx: ctx, w: w, h: h };
  }

  function watchVisibility(canvas, onVisible, onHidden) {
    if (!("IntersectionObserver" in window)) {
      onVisible();
      return function () {};
    }
    var io = new IntersectionObserver(
      function (entries) {
        entries.forEach(function (en) {
          if (en.isIntersecting) onVisible();
          else onHidden();
        });
      },
      { rootMargin: "80px", threshold: 0.01 }
    );
    io.observe(canvas);
    return function () {
      io.disconnect();
    };
  }

  function AnimatedSphere(canvas) {
    var frame = 0;
    var time = 0;
    var chars = "░▒▓█▀▄▌▐│─┤├┴┬╭╮╰╯";
    var running = false;
    var wantRun = true;
    var parallaxX = 0;
    var parallaxY = 0;
    var targetPX = 0;
    var targetPY = 0;

    function resize() {
      setupCanvas(canvas);
    }
    resize();
    window.addEventListener("resize", resize);

    function onMove(e) {
      var rect = canvas.getBoundingClientRect();
      if (!rect.width || !rect.height) return;
      var cx = rect.left + rect.width / 2;
      var cy = rect.top + rect.height / 2;
      targetPX = ((e.clientX - cx) / rect.width) * 0.35;
      targetPY = ((e.clientY - cy) / rect.height) * 0.25;
    }
    if (!prefersReduced) {
      window.addEventListener("pointermove", onMove, { passive: true });
    }

    function drawFrame(advance) {
      var s = setupCanvas(canvas);
      if (!s) return;
      var ctx = s.ctx;
      var w = s.w;
      var h = s.h;
      ctx.clearRect(0, 0, w, h);

      parallaxX += (targetPX - parallaxX) * 0.06;
      parallaxY += (targetPY - parallaxY) * 0.06;

      var centerX = w / 2 + parallaxX * 40;
      var centerY = h / 2 + parallaxY * 30;
      var radius = Math.min(w, h) * 0.525;
      ctx.font = "12px 'JetBrains Mono', monospace";
      ctx.textAlign = "center";
      ctx.textBaseline = "middle";

      var points = [];
      var step = prefersReduced ? 0.22 : 0.15;
      for (var phi = 0; phi < Math.PI * 2; phi += step) {
        for (var theta = 0; theta < Math.PI; theta += step) {
          var x = Math.sin(theta) * Math.cos(phi + time * 0.5);
          var y = Math.sin(theta) * Math.sin(phi + time * 0.5);
          var z = Math.cos(theta);

          var rotY = time * 0.3 + parallaxX * 0.4;
          var newX = x * Math.cos(rotY) - z * Math.sin(rotY);
          var newZ = x * Math.sin(rotY) + z * Math.cos(rotY);

          var rotX = time * 0.2 + parallaxY * 0.3;
          var newY = y * Math.cos(rotX) - newZ * Math.sin(rotX);
          var finalZ = y * Math.sin(rotX) + newZ * Math.cos(rotX);

          var depth = (finalZ + 1) / 2;
          var charIndex = Math.floor(depth * (chars.length - 1));
          points.push({
            x: centerX + newX * radius,
            y: centerY + newY * radius,
            z: finalZ,
            char: chars[Math.min(charIndex, chars.length - 1)],
          });
        }
      }
      points.sort(function (a, b) {
        return a.z - b.z;
      });
      points.forEach(function (p) {
        var alpha = 0.2 + (p.z + 1) * 0.4;
        ctx.fillStyle = "rgba(20, 18, 15, " + Math.min(alpha, 0.95) + ")";
        ctx.fillText(p.char, p.x, p.y);
      });

      if (advance) time += prefersReduced ? 0 : 0.02;
    }

    function render() {
      if (!running) return;
      drawFrame(true);
      if (prefersReduced) {
        running = false;
        return;
      }
      frame = requestAnimationFrame(render);
    }

    function start() {
      if (running || !wantRun) return;
      running = true;
      if (prefersReduced) {
        drawFrame(false);
        running = false;
      } else {
        render();
      }
    }
    function pause() {
      running = false;
      cancelAnimationFrame(frame);
    }

    var unwatch = watchVisibility(canvas, start, pause);
    start();

    return function stop() {
      wantRun = false;
      pause();
      unwatch();
      window.removeEventListener("resize", resize);
      window.removeEventListener("pointermove", onMove);
    };
  }

  function AnimatedTetrahedron(canvas) {
    var frame = 0;
    var time = 0;
    var chars = "░▒▓█▀▄▌▐│─┤├┴┬╭╮╰╯";
    var running = false;
    var wantRun = true;
    var vertices = [
      { x: 0, y: 1, z: 0 },
      { x: -0.943, y: -0.333, z: -0.5 },
      { x: 0.943, y: -0.333, z: -0.5 },
      { x: 0, y: -0.333, z: 1 },
    ];
    var edges = [
      [0, 1],
      [0, 2],
      [0, 3],
      [1, 2],
      [2, 3],
      [3, 1],
    ];
    var faces = [
      [0, 1, 2],
      [0, 2, 3],
      [0, 3, 1],
      [1, 3, 2],
    ];

    function rotY(p, a) {
      return {
        x: p.x * Math.cos(a) - p.z * Math.sin(a),
        y: p.y,
        z: p.x * Math.sin(a) + p.z * Math.cos(a),
      };
    }
    function rotX(p, a) {
      return {
        x: p.x,
        y: p.y * Math.cos(a) - p.z * Math.sin(a),
        z: p.y * Math.sin(a) + p.z * Math.cos(a),
      };
    }
    function rotZ(p, a) {
      return {
        x: p.x * Math.cos(a) - p.y * Math.sin(a),
        y: p.x * Math.sin(a) + p.y * Math.cos(a),
        z: p.z,
      };
    }

    function resize() {
      setupCanvas(canvas);
    }
    resize();
    window.addEventListener("resize", resize);

    function drawFrame(advance) {
      var s = setupCanvas(canvas);
      if (!s) return;
      var ctx = s.ctx;
      var w = s.w;
      var h = s.h;
      ctx.clearRect(0, 0, w, h);
      var centerX = w / 2;
      var centerY = h / 2;
      var scale = Math.min(w, h) * 0.7;
      ctx.font = "16px 'JetBrains Mono', monospace";
      ctx.textAlign = "center";
      ctx.textBaseline = "middle";

      var points = [];
      var edgeStep = prefersReduced ? 0.08 : 0.05;
      var faceStep = prefersReduced ? 0.18 : 0.12;
      edges.forEach(function (e) {
        var v1 = vertices[e[0]];
        var v2 = vertices[e[1]];
        for (var t = 0; t <= 1; t += edgeStep) {
          var point = {
            x: v1.x + (v2.x - v1.x) * t,
            y: v1.y + (v2.y - v1.y) * t,
            z: v1.z + (v2.z - v1.z) * t,
          };
          point = rotY(point, time * 0.4);
          point = rotX(point, time * 0.3);
          point = rotZ(point, time * 0.2);
          var depth = (point.z + 1.5) / 3;
          var charIndex = Math.floor(depth * (chars.length - 1));
          points.push({
            x: centerX + point.x * scale,
            y: centerY - point.y * scale,
            z: point.z,
            char: chars[Math.min(charIndex, chars.length - 1)],
          });
        }
      });
      faces.forEach(function (f) {
        var v1 = vertices[f[0]];
        var v2 = vertices[f[1]];
        var v3 = vertices[f[2]];
        for (var u = 0; u <= 1; u += faceStep) {
          for (var v = 0; v <= 1 - u; v += faceStep) {
            var ww = 1 - u - v;
            var point = {
              x: v1.x * u + v2.x * v + v3.x * ww,
              y: v1.y * u + v2.y * v + v3.y * ww,
              z: v1.z * u + v2.z * v + v3.z * ww,
            };
            point = rotY(point, time * 0.4);
            point = rotX(point, time * 0.3);
            point = rotZ(point, time * 0.2);
            var depth = (point.z + 1.5) / 3;
            var charIndex = Math.floor(depth * (chars.length - 1));
            points.push({
              x: centerX + point.x * scale,
              y: centerY - point.y * scale,
              z: point.z,
              char: chars[Math.min(charIndex, chars.length - 1)],
            });
          }
        }
      });
      points.sort(function (a, b) {
        return a.z - b.z;
      });
      points.forEach(function (p) {
        var alpha = 0.15 + (p.z + 1.5) * 0.25;
        ctx.fillStyle = "rgba(20, 18, 15, " + Math.min(alpha, 0.9) + ")";
        ctx.fillText(p.char, p.x, p.y);
      });
      if (advance) time += prefersReduced ? 0 : 0.015;
    }

    function render() {
      if (!running) return;
      drawFrame(true);
      if (prefersReduced) {
        running = false;
        return;
      }
      frame = requestAnimationFrame(render);
    }

    function start() {
      if (running || !wantRun) return;
      running = true;
      if (prefersReduced) {
        drawFrame(false);
        running = false;
      } else {
        render();
      }
    }
    function pause() {
      running = false;
      cancelAnimationFrame(frame);
    }

    var unwatch = watchVisibility(canvas, start, pause);
    start();

    return function stop() {
      wantRun = false;
      pause();
      unwatch();
      window.removeEventListener("resize", resize);
    };
  }

  function AnimatedWave(canvas, inverted) {
    var frame = 0;
    var time = 0;
    var chars = "·∘○◯◌●◉";
    var running = false;
    var wantRun = true;

    function resize() {
      setupCanvas(canvas);
    }
    resize();
    window.addEventListener("resize", resize);

    function drawFrame(advance) {
      var s = setupCanvas(canvas);
      if (!s) return;
      var ctx = s.ctx;
      var w = s.w;
      var h = s.h;
      ctx.clearRect(0, 0, w, h);
      ctx.font = "14px 'JetBrains Mono', monospace";
      ctx.textAlign = "center";
      ctx.textBaseline = "middle";
      var cell = prefersReduced ? 28 : 20;
      var cols = Math.floor(w / cell);
      var rows = Math.floor(h / cell);
      for (var y = 0; y < rows; y++) {
        for (var x = 0; x < cols; x++) {
          var px = (x + 0.5) * (w / cols);
          var py = (y + 0.5) * (h / rows);
          var wave1 = Math.sin(x * 0.2 + time * 2) * Math.cos(y * 0.15 + time);
          var wave2 = Math.sin((x + y) * 0.1 + time * 1.5);
          var wave3 = Math.cos(x * 0.1 - y * 0.1 + time * 0.8);
          var combined = (wave1 + wave2 + wave3) / 3;
          var normalized = (combined + 1) / 2;
          var charIndex = Math.floor(normalized * (chars.length - 1));
          var alpha = 0.12 + normalized * 0.45;
          if (inverted) {
            ctx.fillStyle = "rgba(250, 249, 247, " + alpha + ")";
          } else {
            ctx.fillStyle = "rgba(20, 18, 15, " + alpha + ")";
          }
          ctx.fillText(chars[charIndex], px, py);
        }
      }
      if (advance) time += prefersReduced ? 0 : 0.03;
    }

    function render() {
      if (!running) return;
      drawFrame(true);
      if (prefersReduced) {
        running = false;
        return;
      }
      frame = requestAnimationFrame(render);
    }

    function start() {
      if (running || !wantRun) return;
      running = true;
      if (prefersReduced) {
        drawFrame(false);
        running = false;
      } else {
        render();
      }
    }
    function pause() {
      running = false;
      cancelAnimationFrame(frame);
    }

    var unwatch = watchVisibility(canvas, start, pause);
    start();

    return function stop() {
      wantRun = false;
      pause();
      unwatch();
      window.removeEventListener("resize", resize);
    };
  }

  /**
   * Mid-page lattice: wireframe cube + scanning shelf plane.
   * Same ASCII depth language as Sphere / Tetra / Wave.
   */
  function AnimatedLattice(canvas) {
    var frame = 0;
    var time = 0;
    var edgeChars = "·∘○◌●◉";
    var faceChars = "░▒▓█▀▄▌▐";
    var running = false;
    var wantRun = true;

    // Unit cube corners
    var corners = [
      { x: -1, y: -1, z: -1 },
      { x: 1, y: -1, z: -1 },
      { x: 1, y: 1, z: -1 },
      { x: -1, y: 1, z: -1 },
      { x: -1, y: -1, z: 1 },
      { x: 1, y: -1, z: 1 },
      { x: 1, y: 1, z: 1 },
      { x: -1, y: 1, z: 1 },
    ];
    var edges = [
      [0, 1], [1, 2], [2, 3], [3, 0],
      [4, 5], [5, 6], [6, 7], [7, 4],
      [0, 4], [1, 5], [2, 6], [3, 7],
    ];

    function rotY(p, a) {
      return {
        x: p.x * Math.cos(a) - p.z * Math.sin(a),
        y: p.y,
        z: p.x * Math.sin(a) + p.z * Math.cos(a),
      };
    }
    function rotX(p, a) {
      return {
        x: p.x,
        y: p.y * Math.cos(a) - p.z * Math.sin(a),
        z: p.y * Math.sin(a) + p.z * Math.cos(a),
      };
    }
    function rotZ(p, a) {
      return {
        x: p.x * Math.cos(a) - p.y * Math.sin(a),
        y: p.x * Math.sin(a) + p.y * Math.cos(a),
        z: p.z,
      };
    }
    function project(p, timeVal) {
      var q = rotY(p, timeVal * 0.45);
      q = rotX(q, timeVal * 0.22 + 0.35);
      q = rotZ(q, timeVal * 0.08);
      return q;
    }

    function resize() {
      setupCanvas(canvas);
    }
    resize();
    window.addEventListener("resize", resize);

    function drawFrame(advance) {
      var s = setupCanvas(canvas);
      if (!s) return;
      var ctx = s.ctx;
      var w = s.w;
      var h = s.h;
      ctx.clearRect(0, 0, w, h);
      var centerX = w / 2;
      var centerY = h / 2;
      var scale = Math.min(w, h) * 0.32;
      ctx.font = "13px 'JetBrains Mono', monospace";
      ctx.textAlign = "center";
      ctx.textBaseline = "middle";

      var points = [];
      var edgeStep = prefersReduced ? 0.1 : 0.06;

      // Cube edges
      edges.forEach(function (e) {
        var v1 = corners[e[0]];
        var v2 = corners[e[1]];
        for (var t = 0; t <= 1; t += edgeStep) {
          var raw = {
            x: v1.x + (v2.x - v1.x) * t,
            y: v1.y + (v2.y - v1.y) * t,
            z: v1.z + (v2.z - v1.z) * t,
          };
          var p = project(raw, time);
          var depth = (p.z + 2) / 4;
          var ci = Math.floor(depth * (edgeChars.length - 1));
          points.push({
            x: centerX + p.x * scale,
            y: centerY - p.y * scale,
            z: p.z,
            char: edgeChars[Math.min(ci, edgeChars.length - 1)],
            kind: "edge",
          });
        }
      });

      // Scanning horizontal plane (shelf slice moving through the cube)
      var scanY = Math.sin(time * 1.1) * 0.85;
      var planeStep = prefersReduced ? 0.22 : 0.14;
      for (var px = -1; px <= 1; px += planeStep) {
        for (var pz = -1; pz <= 1; pz += planeStep) {
          var rawP = { x: px, y: scanY, z: pz };
          var p2 = project(rawP, time);
          // Soft ripple on plane
          var ripple = Math.sin(px * 3 + pz * 2 + time * 2) * 0.5 + 0.5;
          var depth2 = (p2.z + 2) / 4;
          var ci2 = Math.floor(
            (depth2 * 0.55 + ripple * 0.45) * (faceChars.length - 1)
          );
          points.push({
            x: centerX + p2.x * scale,
            y: centerY - p2.y * scale,
            z: p2.z + 0.01,
            char: faceChars[Math.min(ci2, faceChars.length - 1)],
            kind: "plane",
            alphaBoost: 0.08 + ripple * 0.2,
          });
        }
      }

      // Vertical "signal" pillars inside (4 sample retailers metaphor — visual only)
      var pillars = [
        { x: -0.45, z: -0.45 },
        { x: 0.45, z: -0.45 },
        { x: -0.45, z: 0.45 },
        { x: 0.45, z: 0.45 },
      ];
      pillars.forEach(function (col, idx) {
        var hMax = 0.35 + 0.45 * (0.5 + 0.5 * Math.sin(time * 1.4 + idx * 1.1));
        for (var py = -1; py <= -1 + 2 * hMax; py += prefersReduced ? 0.18 : 0.1) {
          var rawC = { x: col.x, y: py, z: col.z };
          var p3 = project(rawC, time);
          var depth3 = (p3.z + 2) / 4;
          var ci3 = Math.floor(depth3 * (faceChars.length - 1));
          points.push({
            x: centerX + p3.x * scale,
            y: centerY - p3.y * scale,
            z: p3.z,
            char: faceChars[Math.min(ci3, faceChars.length - 1)],
            kind: "pillar",
            alphaBoost: 0.12,
          });
        }
      });

      points.sort(function (a, b) {
        return a.z - b.z;
      });
      points.forEach(function (p) {
        var base = 0.14 + (p.z + 2) * 0.18;
        if (p.kind === "plane") base += p.alphaBoost || 0;
        if (p.kind === "pillar") base += p.alphaBoost || 0;
        ctx.fillStyle = "rgba(20, 18, 15, " + Math.min(base, 0.92) + ")";
        ctx.fillText(p.char, p.x, p.y);
      });

      if (advance) time += prefersReduced ? 0 : 0.016;
    }

    function render() {
      if (!running) return;
      drawFrame(true);
      if (prefersReduced) {
        running = false;
        return;
      }
      frame = requestAnimationFrame(render);
    }

    function start() {
      if (running || !wantRun) return;
      running = true;
      if (prefersReduced) {
        drawFrame(false);
        running = false;
      } else {
        render();
      }
    }
    function pause() {
      running = false;
      cancelAnimationFrame(frame);
    }

    var unwatch = watchVisibility(canvas, start, pause);
    start();

    return function stop() {
      wantRun = false;
      pause();
      unwatch();
      window.removeEventListener("resize", resize);
    };
  }

  function animateCounter(el, end, duration, suffix, prefix) {
    var start = 0;
    var startTime = null;
    suffix = suffix || "";
    prefix = prefix || "";
    if (prefersReduced) {
      el.textContent = prefix + end.toLocaleString("es") + suffix;
      return;
    }
    function step(ts) {
      if (!startTime) startTime = ts;
      var p = Math.min((ts - startTime) / duration, 1);
      var eased = 1 - Math.pow(1 - p, 3);
      var val = Math.floor(eased * end);
      el.textContent = prefix + val.toLocaleString("es") + suffix;
      if (p < 1) requestAnimationFrame(step);
    }
    requestAnimationFrame(step);
  }

  global.OptimusGraphics = {
    AnimatedSphere: AnimatedSphere,
    AnimatedTetrahedron: AnimatedTetrahedron,
    AnimatedLattice: AnimatedLattice,
    AnimatedWave: AnimatedWave,
    animateCounter: animateCounter,
    prefersReducedMotion: prefersReduced,
  };
})(window);
