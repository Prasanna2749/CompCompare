/**
 * Circuit Lab: drag/drop strip, LED blink, LCD program panel.
 */
(function () {
  "use strict";

  const PART_NAMES = {
    battery: "Battery 9V",
    resistor: "Resistor 220Ω",
    led: "LED (forward)",
    led_rev: "LED (reversed)",
    lcd: "LCD display",
  };

  function ready(fn) {
    if (document.readyState === "loading") {
      document.addEventListener("DOMContentLoaded", fn);
    } else {
      fn();
    }
  }

  function initLab() {
    const root = document.querySelector("[data-lab]");
    if (!root) return;

    const board = root.querySelector("[data-lab-board]");
    const resultEl = root.querySelector("[data-lab-result]");
    const ledEl = root.querySelector("[data-lab-led]");
    const lcdTextEl = root.querySelector("[data-lab-lcd-text]");
    const lcdScreen = root.querySelector("[data-lab-lcd]");
    const lcdStatus = root.querySelector("[data-lab-lcd-status]");
    const programEl = root.querySelector("[data-lab-program]");
    const titleEl = root.querySelector("[data-lab-title]");
    const goalEl = root.querySelector("[data-lab-goal]");
    const hintEl = root.querySelector("[data-lab-hint]");
    const runBtn = root.querySelector("[data-lab-run]");
    const runProgramBtn = root.querySelector("[data-lab-run-program]");
    const clearBtn = root.querySelector("[data-lab-clear]");
    const sampleBtn = root.querySelector("[data-lab-load-sample]");

    let activeProblemId = root.getAttribute("data-active-problem") || "p1";
    let slotCount = Number(root.getAttribute("data-slots") || 3);
    let sampleProgram = (programEl && programEl.value) || 'lcd.print("Hello ECE")';
    let dragPartId = null;

    function setResult(ok, message) {
      if (!resultEl) return;
      resultEl.hidden = false;
      resultEl.className = `lab-result ${ok ? "ok" : "err"}`;
      resultEl.textContent = message;
    }

    function clearResult() {
      if (!resultEl) return;
      resultEl.hidden = true;
      resultEl.textContent = "";
      resultEl.className = "lab-result";
    }

    function setLcdStatus(message, kind) {
      if (!lcdStatus) return;
      lcdStatus.textContent =
        message || "Message appears here after a successful Run";
      lcdStatus.classList.remove("is-error", "is-ok");
      if (kind === "error") lcdStatus.classList.add("is-error");
      if (kind === "ok") lcdStatus.classList.add("is-ok");
    }

    function stopLed() {
      if (!ledEl) return;
      ledEl.classList.remove("is-blink", "is-on");
    }

    function blinkLed() {
      if (!ledEl) return;
      ledEl.classList.remove("is-blink", "is-on");
      void ledEl.offsetWidth;
      ledEl.classList.add("is-blink");
      window.setTimeout(() => {
        ledEl.classList.remove("is-blink");
        ledEl.classList.add("is-on");
      }, 2800);
    }

    function updateLcd(action, text) {
      if (!lcdTextEl || !lcdScreen) return;
      if (action === "clear") {
        lcdTextEl.textContent = "";
        lcdScreen.classList.remove("is-active");
        return;
      }
      if (action === "print") {
        lcdTextEl.textContent = String(text || "").toUpperCase();
        lcdScreen.classList.add("is-active");
        return;
      }
      lcdTextEl.textContent = "";
      lcdScreen.classList.remove("is-active");
    }

    function getSlots() {
      return Array.from(board.querySelectorAll("[data-slot]")).map(
        (slot) => slot.getAttribute("data-filled") || ""
      );
    }

    function fillSlot(slot, partId) {
      slot.setAttribute("data-filled", partId);
      slot.classList.add("filled");
      const name = PART_NAMES[partId] || partId;
      let iconClass = `lab-icon-${partId}`;
      if (partId === "led") iconClass = "lab-icon-led";
      if (partId === "led_rev") iconClass = "lab-icon-led is-rev";
      if (partId === "lcd") iconClass = "lab-icon-lcd";
      slot.innerHTML = `
        <span class="lab-slot-label">Filled</span>
        <span class="lab-part-icon ${iconClass}" aria-hidden="true"></span>
        <span class="lab-slot-part">${name}</span>`;
    }

    function emptySlot(slot, index) {
      slot.removeAttribute("data-filled");
      slot.classList.remove("filled", "drag-over");
      slot.innerHTML = `<span class="lab-slot-label">Slot ${index + 1}</span><span class="lab-slot-part">Drop here</span>`;
    }

    function renderBoard() {
      if (!board) return;
      board.innerHTML = "";
      for (let i = 0; i < slotCount; i += 1) {
        if (i > 0) {
          const wire = document.createElement("div");
          wire.className = "lab-wire";
          wire.setAttribute("aria-hidden", "true");
          board.appendChild(wire);
        }
        const slot = document.createElement("div");
        slot.className = "lab-slot";
        slot.setAttribute("data-slot", String(i));
        emptySlot(slot, i);

        slot.addEventListener("dragover", (event) => {
          event.preventDefault();
          slot.classList.add("drag-over");
        });
        slot.addEventListener("dragleave", () => slot.classList.remove("drag-over"));
        slot.addEventListener("drop", (event) => {
          event.preventDefault();
          slot.classList.remove("drag-over");
          const partId = event.dataTransfer.getData("text/plain") || dragPartId;
          if (!partId || !PART_NAMES[partId]) return;
          fillSlot(slot, partId);
          clearResult();
          stopLed();
        });
        slot.addEventListener("click", () => {
          if (!slot.getAttribute("data-filled")) return;
          emptySlot(slot, i);
          clearResult();
          stopLed();
        });

        board.appendChild(slot);
      }
    }

    function bindPalette() {
      root.querySelectorAll(".lab-part[data-part-id]").forEach((el) => {
        el.addEventListener("dragstart", (event) => {
          dragPartId = el.getAttribute("data-part-id");
          el.classList.add("dragging");
          if (event.dataTransfer) {
            event.dataTransfer.setData("text/plain", dragPartId);
            event.dataTransfer.effectAllowed = "copy";
          }
        });
        el.addEventListener("dragend", () => {
          el.classList.remove("dragging");
          dragPartId = null;
        });
      });
    }

    async function runLab() {
      const slots = getSlots();
      const program = programEl ? programEl.value : "";
      stopLed();
      try {
        const res = await fetch("/api/lab/run", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            problem_id: activeProblemId,
            slots,
            program,
          }),
        });
        const data = await res.json();
        setResult(Boolean(data.ok), data.message || "No response.");
        if (data.ok && data.blink) blinkLed();
        if (data.ok && data.lcd_action) {
          updateLcd(data.lcd_action, data.lcd_text || "");
          setLcdStatus(
            data.lcd_action === "clear"
              ? "LCD cleared."
              : `Showing: ${data.lcd_text || ""}`,
            "ok"
          );
        } else if (!data.ok) {
          updateLcd(null, "");
          setLcdStatus(data.message || "Run failed.", "error");
        }
      } catch (err) {
        setResult(false, "Could not reach the lab checker. Try again.");
        setLcdStatus("Could not reach the lab checker.", "error");
      }
    }

    function selectProblem(btn) {
      root.querySelectorAll(".lab-problem-btn").forEach((b) => b.classList.remove("active"));
      btn.classList.add("active");
      activeProblemId = btn.getAttribute("data-problem-id") || "p1";
      slotCount = Number(btn.getAttribute("data-slots") || 3);
      sampleProgram =
        btn.getAttribute("data-sample-program") || 'lcd.print("Hello ECE")';
      if (titleEl) titleEl.textContent = btn.getAttribute("data-title") || "";
      if (goalEl) goalEl.textContent = btn.getAttribute("data-goal") || "";
      if (hintEl) hintEl.textContent = btn.getAttribute("data-hint") || "";
      root.setAttribute("data-active-problem", activeProblemId);
      root.setAttribute("data-mode", btn.getAttribute("data-mode") || "led");
      if (programEl && (activeProblemId === "p5" || activeProblemId === "custom")) {
        programEl.value = sampleProgram;
      }
      clearResult();
      stopLed();
      updateLcd(null, "");
      setLcdStatus("Message appears here after a successful Run");
      renderBoard();
      window.history.replaceState({}, "", `/lab/${activeProblemId}`);
    }

    root.querySelectorAll(".lab-problem-btn").forEach((btn) => {
      btn.addEventListener("click", () => selectProblem(btn));
    });

    if (sampleBtn) {
      sampleBtn.addEventListener("click", () => {
        if (programEl) programEl.value = sampleProgram;
      });
    }

    if (clearBtn) {
      clearBtn.addEventListener("click", () => {
        renderBoard();
        clearResult();
        stopLed();
        updateLcd(null, "");
        setLcdStatus("Message appears here after a successful Run");
      });
    }

    if (runBtn) runBtn.addEventListener("click", runLab);
    if (runProgramBtn) runProgramBtn.addEventListener("click", runLab);

    bindPalette();
    renderBoard();
  }

  ready(initLab);
})();
