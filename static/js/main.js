/**
 * CompCompare front-end:
 * mobile nav, comparison tray, live search/filter/sort, compare picker
 */

(function () {
  "use strict";

  const MAX_COMPARE = 3;
  const STORAGE_KEY = "compcompare_selection";

  function ready(fn) {
    if (document.readyState === "loading") {
      document.addEventListener("DOMContentLoaded", fn);
    } else {
      fn();
    }
  }

  function getSelection() {
    try {
      const raw = localStorage.getItem(STORAGE_KEY);
      const parsed = raw ? JSON.parse(raw) : [];
      if (!Array.isArray(parsed)) return [];
      return parsed
        .filter((item) => item && Number.isInteger(item.id) && item.name)
        .slice(0, MAX_COMPARE);
    } catch (err) {
      return [];
    }
  }

  function saveSelection(items) {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(items.slice(0, MAX_COMPARE)));
  }

  function selectionIds() {
    return getSelection().map((item) => item.id);
  }

  function upsertSelection(id, name) {
    const items = getSelection().filter((item) => item.id !== id);
    items.push({ id, name });
    if (items.length > MAX_COMPARE) {
      return { ok: false, error: `You can compare at most ${MAX_COMPARE} components.` };
    }
    saveSelection(items);
    return { ok: true, items };
  }

  function removeSelection(id) {
    saveSelection(getSelection().filter((item) => item.id !== id));
  }

  function clearSelection() {
    saveSelection([]);
  }

  function syncCheckboxes() {
    const ids = new Set(selectionIds());
    document.querySelectorAll("[data-compare-toggle]").forEach((input) => {
      input.checked = ids.has(Number(input.value));
    });
  }

  function truncate(text, max) {
    return text.length > max ? `${text.slice(0, max - 1)}…` : text;
  }

  function escapeHtml(value) {
    return String(value)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;");
  }

  function escapeAttr(value) {
    return escapeHtml(value).replace(/'/g, "&#39;");
  }

  function renderTray() {
    const tray = document.querySelector("[data-compare-tray]");
    if (!tray) return;

    const items = getSelection();
    const countEl = tray.querySelector("[data-compare-count]");
    const chipsEl = tray.querySelector("[data-compare-chips]");
    const goBtn = tray.querySelector("[data-compare-go]");

    if (items.length === 0) {
      tray.hidden = true;
      return;
    }

    tray.hidden = false;
    if (countEl) countEl.textContent = `${items.length} selected`;
    if (chipsEl) {
      chipsEl.innerHTML = items
        .map(
          (item) =>
            `<span class="compare-chip" title="${escapeAttr(item.name)}">${escapeHtml(
              truncate(item.name, 28)
            )}</span>`
        )
        .join("");
    }
    if (goBtn) goBtn.disabled = items.length < 2;
  }

  function showToast(message, type) {
    let wrap = document.querySelector(".flash-wrap");
    if (!wrap) {
      wrap = document.createElement("div");
      wrap.className = "flash-wrap container";
      wrap.setAttribute("role", "status");
      const main = document.getElementById("main");
      if (main) main.parentNode.insertBefore(wrap, main);
      else document.body.prepend(wrap);
    }
    const el = document.createElement("div");
    el.className = `flash flash-${type || "warning"}`;
    el.textContent = message;
    wrap.appendChild(el);
    setTimeout(() => el.remove(), 3500);
  }

  function initNav() {
    const toggle = document.querySelector("[data-nav-toggle]");
    const nav = document.querySelector("[data-site-nav]");
    if (!toggle || !nav) return;
    toggle.addEventListener("click", () => {
      const open = nav.classList.toggle("open");
      toggle.setAttribute("aria-expanded", open ? "true" : "false");
    });
  }

  function initCompareToggles() {
    document.addEventListener("change", (event) => {
      const input = event.target;
      if (!(input instanceof HTMLInputElement)) return;
      if (!input.matches("[data-compare-toggle]")) return;

      const id = Number(input.value);
      const name = input.getAttribute("data-name") || `Component #${id}`;

      if (input.checked) {
        const result = upsertSelection(id, name);
        if (!result.ok) {
          input.checked = false;
          showToast(result.error, "warning");
          return;
        }
      } else {
        removeSelection(id);
      }
      renderTray();
      syncCheckboxes();
      syncPickerFromStorage();
    });
  }

  function initTrayActions() {
    const tray = document.querySelector("[data-compare-tray]");
    if (!tray) return;
    const clearBtn = tray.querySelector("[data-compare-clear]");
    const goBtn = tray.querySelector("[data-compare-go]");

    if (clearBtn) {
      clearBtn.addEventListener("click", () => {
        clearSelection();
        syncCheckboxes();
        renderTray();
        syncPickerFromStorage();
      });
    }

    if (goBtn) {
      goBtn.addEventListener("click", async () => {
        const ids = selectionIds();
        if (ids.length < 2) {
          showToast("Select at least 2 components to compare.", "warning");
          return;
        }
        try {
          const res = await fetch("/api/compare/validate", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ ids }),
          });
          const data = await res.json();
          if (!data.ok) {
            showToast(data.error || "Unable to compare selection.", "error");
            return;
          }
          window.location.href = data.url || `/compare?ids=${ids.join(",")}`;
        } catch (err) {
          window.location.href = `/compare?ids=${ids.join(",")}`;
        }
      });
    }
  }

  function debounce(fn, wait) {
    let timer = null;
    return function (...args) {
      clearTimeout(timer);
      timer = setTimeout(() => fn.apply(this, args), wait);
    };
  }

  function cardTemplate(c) {
    const specs = (c.key_spec_list || []).slice(0, 3)
      .map(
        (spec) =>
          `<li><span>${escapeHtml(spec.label)}</span> ${escapeHtml(spec.value)}</li>`
      )
      .join("");
    const image = c.image_file || `img/${c.image_slug || "ic"}.svg`;
    const src = `/static/${image}`.replace("/static//", "/static/");
    return `
      <article class="component-card" data-component-id="${c.id}">
        <div class="card-media">
          <img class="component-photo" src="${escapeAttr(src)}" alt="${escapeAttr(c.name)}" loading="eager" onerror="this.onerror=null;this.src='/static/img/ic.svg';">
        </div>
        <div class="card-top">
          <span class="badge">${escapeHtml(c.category)}</span>
          <label class="compare-check">
            <input type="checkbox" data-compare-toggle value="${c.id}" data-name="${escapeAttr(c.name)}">
            <span>Compare</span>
          </label>
        </div>
        <h3><a href="/component/${c.id}">${escapeHtml(c.name)}</a></h3>
        <p class="card-meta">${escapeHtml(c.part_number)} · ${escapeHtml(c.manufacturer)}</p>
        <ul class="mini-specs">${specs}</ul>
        <div class="card-actions">
          <a class="btn btn-small" href="/component/${c.id}">Details</a>
        </div>
      </article>`;
  }

  function initLiveFilter() {
    const form = document.querySelector("[data-filter-form]");
    const grid = document.querySelector("[data-component-grid]");
    const countEl = document.querySelector("[data-result-count]");
    if (!form || !grid) return;

    const searchInput = form.querySelector("[data-search-input]");
    const categorySelect = form.querySelector("[data-category-select]");
    const sortSelect = form.querySelector("[data-sort-select]");

    const run = async () => {
      const q = (searchInput && searchInput.value.trim()) || "";
      const category = (categorySelect && categorySelect.value) || "all";
      const sort = (sortSelect && sortSelect.value) || "category";
      const params = new URLSearchParams();
      if (q) params.set("q", q);
      if (category) params.set("category", category);
      if (sort) params.set("sort", sort);

      try {
        const res = await fetch(`/api/components?${params.toString()}`);
        const data = await res.json();
        if (!res.ok) {
          showToast(data.error || "Search failed.", "error");
          return;
        }

        const components = data.components || [];
        if (countEl) countEl.textContent = String(components.length);

        if (components.length === 0) {
          grid.innerHTML = `
            <div class="empty-state" data-empty-state>
              <h3>No components found</h3>
              <p>Try a different search term or clear the category filter.</p>
              <a class="btn btn-secondary" href="/components">Reset filters</a>
            </div>`;
        } else {
          grid.innerHTML = components.map(cardTemplate).join("");
        }
        syncCheckboxes();

        const url = new URL(window.location.href);
        if (q) url.searchParams.set("q", q);
        else url.searchParams.delete("q");
        if (category && category !== "all") url.searchParams.set("category", category);
        else url.searchParams.delete("category");
        if (sort && sort !== "category") url.searchParams.set("sort", sort);
        else url.searchParams.delete("sort");
        window.history.replaceState({}, "", url);
      } catch (err) {
        // Non-JS form submit still works.
      }
    };

    const debounced = debounce(run, 280);
    if (searchInput) searchInput.addEventListener("input", debounced);
    if (categorySelect) categorySelect.addEventListener("change", run);
    if (sortSelect) sortSelect.addEventListener("change", run);
  }

  function syncPickerFromStorage() {
    const picker = document.querySelector("[data-compare-picker]");
    if (!picker) return;
    const ids = new Set(selectionIds());
    picker.querySelectorAll('input[type="checkbox"][data-picker-id]').forEach((input) => {
      input.checked = ids.has(Number(input.getAttribute("data-picker-id")));
    });
    updatePickerHidden();
  }

  function updatePickerHidden() {
    const form = document.querySelector("[data-picker-form]");
    if (!form) return;
    const hidden = form.querySelector("[data-picker-ids]");
    const hint = form.querySelector("[data-picker-hint]");
    const checked = Array.from(
      form.querySelectorAll('input[type="checkbox"][data-picker-id]:checked')
    ).map((el) => Number(el.getAttribute("data-picker-id")));

    if (hidden) hidden.value = checked.join(",");
    if (hint) {
      if (checked.length < 2) {
        hint.textContent = "Select at least 2 components.";
        hint.classList.add("error");
      } else if (checked.length > MAX_COMPARE) {
        hint.textContent = `Select at most ${MAX_COMPARE} components.`;
        hint.classList.add("error");
      } else {
        hint.textContent = `${checked.length} selected — ready to compare.`;
        hint.classList.remove("error");
      }
    }
  }

  async function initComparePicker() {
    const grid = document.querySelector("[data-picker-grid]");
    const form = document.querySelector("[data-picker-form]");
    if (!grid || !form) return;

    try {
      const res = await fetch("/api/components");
      const data = await res.json();
      const components = data.components || [];
      const selected = new Set(selectionIds());

      grid.innerHTML = components
        .map((c) => {
          const checked = selected.has(c.id) ? "checked" : "";
          return `
            <label class="picker-item">
              <input type="checkbox" data-picker-id="${c.id}" value="${c.id}" ${checked}>
              <span>
                <strong>${escapeHtml(c.name)}</strong>
                <span>${escapeHtml(c.category)} · ${escapeHtml(c.part_number)}</span>
              </span>
            </label>`;
        })
        .join("");

      updatePickerHidden();

      form.addEventListener("change", (event) => {
        const input = event.target;
        if (!(input instanceof HTMLInputElement) || !input.matches("[data-picker-id]")) {
          return;
        }
        const id = Number(input.value);
        const label = input.closest("label");
        const name =
          (label && label.querySelector("strong") && label.querySelector("strong").textContent) ||
          `Component #${id}`;

        const checkedBoxes = form.querySelectorAll(
          'input[type="checkbox"][data-picker-id]:checked'
        );
        if (checkedBoxes.length > MAX_COMPARE) {
          input.checked = false;
          showToast(`You can compare at most ${MAX_COMPARE} components.`, "warning");
          updatePickerHidden();
          return;
        }

        if (input.checked) {
          const result = upsertSelection(id, name);
          if (!result.ok) {
            input.checked = false;
            showToast(result.error, "warning");
          }
        } else {
          removeSelection(id);
        }
        updatePickerHidden();
        syncCheckboxes();
        renderTray();
      });

      form.addEventListener("submit", (event) => {
        updatePickerHidden();
        const hidden = form.querySelector("[data-picker-ids]");
        const ids = (hidden && hidden.value ? hidden.value.split(",") : []).filter(Boolean);
        if (ids.length < 2 || ids.length > MAX_COMPARE) {
          event.preventDefault();
          showToast(`Select between 2 and ${MAX_COMPARE} components.`, "warning");
        }
      });
    } catch (err) {
      grid.innerHTML =
        '<p class="form-hint error">Could not load components for the picker. Use the catalog checkboxes instead.</p>';
    }
  }

  ready(() => {
    initNav();
    initCompareToggles();
    initTrayActions();
    initLiveFilter();
    initComparePicker();
    syncCheckboxes();
    renderTray();
  });
})();
