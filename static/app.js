// static/app.js
// ---------------- FULL upgraded app.js ----------------
// State
let candidates = [];
let activeCity = "all";
let editingId = null;

// DOM nodes (must match your index.html)
const cardsWrap = document.getElementById("cardsWrap");
const modal = document.getElementById("modal");
const btnAdd = document.getElementById("btnAdd");
const chips = document.querySelectorAll(".chip");
const filterGender = document.getElementById("filterGender");
const filterPhoto = document.getElementById("filterPhoto");
const filterStatus = document.getElementById("filterStatus");
const searchText = document.getElementById("searchText");

// inputs in modal (if some id missing in your HTML — add them)
const cityInput = document.getElementById("cityInput");
const photoInput = document.getElementById("photoInput");
const nameInput = document.getElementById("nameInput");
const ageInput = document.getElementById("ageInput");
const genderInput = document.getElementById("genderInput"); // <-- add <select id="genderInput"> if not present
const experienceInput = document.getElementById("experienceInput");
const workingInput = document.getElementById("workingInput");
const workTimeInput = document.getElementById("workTimeInput");
const systemsInput = document.getElementById("systemsInput");
const startDateInput = document.getElementById("startDateInput"); // дата коли зацікавився
const phoneInput = document.getElementById("phoneInput");
const myNoteInput = document.getElementById("myNoteInput");
const statusInput = document.getElementById("statusInput");
const internPlaceInput = document.getElementById("internPlaceInput");
const internStartInput = document.getElementById("internStartInput");
const internDaysInput = document.getElementById("internDaysInput");
const callbackDateInput = document.getElementById("callbackDateInput");

// modal buttons / detail
const saveBtn = document.getElementById("saveBtn");
const cancelBtn = document.getElementById("cancelBtn");
const detailPanel = document.getElementById("detailPanel");
const detailContent = document.getElementById("detailContent");
const closePanel = document.getElementById("closePanel");

// notification button / dot / panel — add these elements to HTML header/topbar:
// <button id="notifBtn" class="notif-btn">✉ <span id="notifDot"></span></button>
// <div id="notifPanel" class="notif-panel hidden"></div>
const notifBtn = document.getElementById("notifBtn");
const notifDot = document.getElementById("notifDot");
const notifPanel = document.getElementById("notifPanel");

// Utility: load candidates from backend
async function loadCandidates() {
  try {
    const res = await fetch("/api/candidates");
    if (!res.ok) throw new Error("Failed to load");
    candidates = await res.json();
    // ensure created_at exists and is ISO string for each candidate
    candidates = candidates.map(c => {
      if (!c.created_at) c.created_at = new Date().toISOString();
      // ensure fields exist
      if (!c.status) c.status = "notCalled"; // default: not called yet
      if (!c.workTime) c.workTime = "permanent";
      if (!c.gender) c.gender = "unknown";
      return c;
    });
    render();
  } catch (e) {
    console.error("loadCandidates:", e);
    // show empty state
    candidates = [];
    render();
  }
}

function formatDateIso(d) {
  if (!d) return "-";
  try {
    const dt = new Date(d);
    return dt.toLocaleDateString();
  } catch (e) {
    return d;
  }
}

function getBadgeClass(status) {
  switch (status) {
    case "good": return "badge good";
    case "normal": return "badge normal";
    case "unclear": return "badge unclear";
    case "notCalled": return "badge gray";
    case "called": return "badge teal";
    case "interning": return "badge interning";
    case "hired": return "badge hired";
    case "rejected": return "badge rejected";
    default: return "badge normal";
  }
}

function statusLabel(status) {
  switch (status) {
    case "good": return "Хороший";
    case "normal": return "Норм";
    case "unclear": return "Непонятно";
    case "notCalled": return "Не обдзвонений";
    case "called": return "Обдзвонений";
    case "interning": return "Стажується";
    case "hired": return "Працевлаштований";
    case "rejected": return "Відмова";
    default: return status || "Норм";
  }
}

// RENDER list of cards
function render() {
  cardsWrap.innerHTML = "";

  let list = candidates.filter(c => {
    if (activeCity !== "all" && c.city !== activeCity) return false;
    if (filterGender && filterGender.value && filterGender.value !== "all" && c.gender !== filterGender.value) return false;
    if (filterPhoto && filterPhoto.value === "with" && !c.photo) return false;
    if (filterPhoto && filterPhoto.value === "no" && c.photo) return false;
    if (filterStatus && filterStatus.value !== "all" && c.status !== filterStatus.value) return false;
    const q = (searchText && searchText.value || "").trim().toLowerCase();
    if (q) {
      const hay = (c.name + " " + (c.phone || "") + " " + (c.myNote || "") + " " + (c.experience || "")).toLowerCase();
      if (!hay.includes(q)) return false;
    }
    return true;
  });

  // sort: temporary (workTime === 'temporary') go to the end, else by created_at desc
  list.sort((a, b) => {
    if (a.workTime === "temporary" && b.workTime !== "temporary") return 1;
    if (b.workTime === "temporary" && a.workTime !== "temporary") return -1;
    return new Date(b.created_at) - new Date(a.created_at);
  });

  if (list.length === 0) {
    cardsWrap.innerHTML = `<div class="empty">Поки немає кандидатів за поточними фільтрами.</div>`;
  } else {
    list.forEach(c => {
      const card = document.createElement("div");
      card.className = "card";
      // highlight temporary candidates with red border/pale background if desired in CSS via .card.temporary
      if (c.workTime === "temporary") card.classList.add("temporary");

      const name = c.name || "—";
      const ageLabel = c.age ? `${c.age} р.` : "";
      const genderLabel = c.gender && c.gender !== "unknown" ? ` • ${c.gender}` : "";
      const createdLabel = c.created_at ? ` • ${formatDateIso(c.created_at)}` : "";

      card.innerHTML = `
        <div class="photo">${c.photo ? `<img src="${c.photo}" alt="photo">` : `<div class="no-photo">No photo</div>`}</div>
        <div class="row">
          <div class="left">
            <div class="name">${name}</div>
            <div class="meta">${ageLabel}${genderLabel} • ${c.city || ""}${createdLabel}</div>
          </div>
          <div class="right"><span class="${getBadgeClass(c.status)}">${statusLabel(c.status)}</span></div>
        </div>
        <div class="meta">${c.experience ? c.experience : ""}</div>
        <div class="note">${c.myNote ? c.myNote : ""}</div>
        ${c.callbackDate ? `<div class="callback">🔔 ${formatDateIso(c.callbackDate)}</div>` : ""}
        <div class="actions">
          <button class="action-btn call" data-phone="${c.phone}">📞 Дзвонити</button>
          <button class="action-btn copy" data-phone="${c.phone}">📋 Копія</button>
          <button class="action-btn edit" data-id="${c.id}">✎ Редагувати</button>
        </div>
      `;
      // event delegation on buttons
      card.addEventListener("click", (e) => {
        const btn = e.target.closest(".action-btn");
        if (btn) {
          if (btn.classList.contains("call")) callNumber(btn.dataset.phone);
          else if (btn.classList.contains("copy")) copyNumber(btn.dataset.phone);
          else if (btn.classList.contains("edit")) openEdit(Number(btn.dataset.id));
        } else {
          openDetail(c.id);
        }
      });

      cardsWrap.appendChild(card);
    });
  }

  updateNotifications();
}

// Notifications (envelope icon + dot + panel)
function updateNotifications() {
  const today = new Date().toISOString().split("T")[0];
  const toCall = candidates.filter(c => (c.status === "notCalled") || (c.callbackDate && c.callbackDate === today));
  const interning = candidates.filter(c => c.status === "interning");

  // update dot
  if (!notifDot) return;
  if (toCall.length === 0) {
    notifDot.style.background = "green";
    notifDot.innerText = "✓";
    notifDot.title = "Усі обдзвонені";
  } else {
    notifDot.style.background = "red";
    notifDot.innerText = String(toCall.length);
    notifDot.title = `${toCall.length} потребують дзвінка`;
  }

  // fill panel
  if (!notifPanel) return;
  let html = "";
  if (toCall.length === 0) {
    html += `<div class="notif-empty">✅ Усі обдзвонені</div>`;
  } else {
    html += `<h4>📞 Потрібно подзвонити (${toCall.length}):</h4>`;
    toCall.forEach(c => {
      const isToday = c.callbackDate && c.callbackDate === today;
      html += `
        <div class="notif-item" onclick="openDetail(${c.id});" title="Відкрити анкету">
          <div class="ni-left"><b>${c.name || "-"}</b></div>
          <div class="ni-right">${c.phone || "-"} ${isToday ? `<span class="ni-today">🔔 сьогодні</span>` : ""}</div>
        </div>
      `;
    });
  }

  if (interning.length > 0) {
    html += `<h4>👷 На стажуванні (${interning.length}):</h4>`;
    interning.forEach(c => {
      html += `<div class="notif-item small" onclick="openDetail(${c.id});">${c.name} • ${c.city || ""}</div>`;
    });
  }

  notifPanel.innerHTML = html;
}

// No alert-based reminders — indicator only. (Removed alert spam)
// checkReminders kept minimal (can be used if you later want push-notifications)
function checkRemindersMinimal() {
  // noop for now (we rely on envelope indicator/panel)
}
setInterval(checkRemindersMinimal, 60 * 1000);

// Events
btnAdd && btnAdd.addEventListener("click", () => openModal());
chips.forEach(ch => {
  ch.addEventListener("click", () => {
    chips.forEach(x => x.classList.remove("active"));
    ch.classList.add("active");
    activeCity = ch.dataset.city;
    render();
  });
});
document.querySelector('.chip[data-city="all"]')?.classList.add('active');

filterGender && filterGender.addEventListener("change", render);
filterPhoto && filterPhoto.addEventListener("change", render);
filterStatus && filterStatus.addEventListener("change", render);
searchText && searchText.addEventListener("input", render);

cancelBtn && cancelBtn.addEventListener("click", () => modal.classList.add("hidden"));

notifBtn && notifBtn.addEventListener("click", () => {
  if (!notifPanel) return;
  notifPanel.classList.toggle("hidden");
});

// Modal open / edit
function openModal() {
  editingId = null;
  document.getElementById("modalTitle").innerText = "Додати кандидата";
  modal.classList.remove("hidden");

  // reset fields
  cityInput.value = cityInput.value || "Житомир";
  photoInput.value = "";
  nameInput.value = "";
  ageInput.value = "";
  if (genderInput) genderInput.value = "unknown";
  experienceInput.value = "";
  workingInput.value = "no";
  workTimeInput.value = "permanent";
  systemsInput.value = "no";
  startDateInput.value = (new Date()).toISOString().split('T')[0];
  phoneInput.value = "";
  myNoteInput.value = "";
  statusInput.value = "notCalled";
  internPlaceInput.value = "";
  internStartInput.value = "";
  internDaysInput.value = "";
  callbackDateInput.value = "";
}

function openEdit(id) {
  const c = candidates.find(x => x.id === id);
  if (!c) return;
  editingId = id;
  document.getElementById("modalTitle").innerText = "Редагувати кандидата";

  cityInput.value = c.city || "Житомир";
  // NOTE: do not set photoInput file — files are read-only; we keep photo displayed in UI
  nameInput.value = c.name || "";
  ageInput.value = c.age || "";
  if (genderInput) genderInput.value = c.gender || "unknown";
  experienceInput.value = c.experience || "";
  workingInput.value = c.working || "no";
  workTimeInput.value = c.workTime || "permanent";
  systemsInput.value = c.systems || "no";
  startDateInput.value = c.startDate || "";
  phoneInput.value = c.phone || "";
  myNoteInput.value = c.myNote || "";
  statusInput.value = c.status || "notCalled";
  internPlaceInput.value = (c.internship && c.internship.place) || "";
  internStartInput.value = (c.internship && c.internship.start) || "";
  internDaysInput.value = (c.internship && c.internship.days) || "";
  callbackDateInput.value = c.callbackDate || "";
  modal.classList.remove("hidden");
}

// Save (create/update)
saveBtn && saveBtn.addEventListener("click", async () => {
  const obj = {
    city: cityInput.value,
    name: nameInput.value,
    age: ageInput.value ? Number(ageInput.value) : null,
    gender: genderInput ? genderInput.value : "unknown",
    experience: experienceInput.value,
    working: workingInput.value,
    workTime: workTimeInput.value,
    systems: systemsInput.value,
    startDate: startDateInput.value || null, // date when they were interested
    phone: phoneInput.value,
    myNote: myNoteInput.value,
    status: statusInput.value || "notCalled",
    callbackDate: callbackDateInput.value || null
  };

  if (internPlaceInput.value || internStartInput.value || internDaysInput.value) {
    obj.internship = {
      place: internPlaceInput.value || "",
      start: internStartInput.value || "",
      days: internDaysInput.value ? Number(internDaysInput.value) : 0
    };
  } else {
    obj.internship = null;
  }

  // handle photo: if new file selected => to base64; if editing and no new file => preserve existing
  const file = photoInput.files && photoInput.files[0];
  if (file) {
    try {
      const b64 = await toBase64(file);
      obj.photo = b64;
    } catch (e) {
      console.error("photo toBase64:", e);
    }
  } else if (editingId) {
    // preserve previous photo of candidate when editing
    const orig = candidates.find(x => x.id === editingId);
    if (orig && orig.photo) obj.photo = orig.photo;
  }

  if (editingId) {
    obj.id = editingId;
    const orig = candidates.find(x => x.id === editingId);
    if (orig && orig.created_at) obj.created_at = orig.created_at;
  } else {
    obj.created_at = new Date().toISOString();
  }

  // POST to backend
  try {
    const res = await fetch("/api/candidates", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ candidate: obj })
    });
    if (!res.ok) throw new Error("Save failed");
  } catch (e) {
    console.error("Save candidate error:", e);
    alert("Помилка збереження. Подивіться консолі сервера.");
  }

  modal.classList.add("hidden");
  await loadCandidates();
});

// file -> base64
function toBase64(file) {
  return new Promise((res, rej) => {
    const reader = new FileReader();
    reader.onload = () => res(reader.result);
    reader.onerror = (e) => rej(e);
    reader.readAsDataURL(file);
  });
}

// call / copy utils
function callNumber(num) {
  if (!num) { alert("Номер відсутній"); return; }
  // open dialer on mobile / desktop uses tel: handler
  window.location.href = `tel:${num}`;
}
function copyNumber(num) {
  if (!num) { alert("Номер відсутній"); return; }
  navigator.clipboard.writeText(num).then(() => {
    // subtle toast - here simplest:
    const prev = document.querySelector(".toast-copy");
    if (prev) prev.remove();
    const t = document.createElement("div");
    t.className = "toast-copy";
    t.innerText = "Номер скопійовано";
    document.body.appendChild(t);
    setTimeout(() => t.remove(), 1200);
  });
}

// Detail panel
function openDetail(id) {
  const c = candidates.find(x => x.id === id);
  if (!c) return;
  detailContent.innerHTML = `
    <div class="detail-row">
      <div class="detail-photo">
        ${c.photo ? `<img src="${c.photo}" alt="photo">` : `<div class="no-photo large">No photo</div>`}
      </div>
      <div class="detail-main">
        <h2>${c.name || "-"}</h2>
        <div class="meta">${c.age ? c.age + " р." : ""} ${c.gender && c.gender !== "unknown" ? "• " + c.gender : ""} • ${c.city || ""}</div>
        <p class="experience">${c.experience || ""}</p>
        <p class="note"><b>Мій коментар:</b> ${c.myNote || "-"}</p>
        <p class="status"><b>Статус:</b> <span class="${getBadgeClass(c.status)}">${statusLabel(c.status)}</span></p>
        <p><b>Системи/парите:</b> ${c.systems || "-"}</p>
        <p><b>Період:</b> ${c.workTime === "temporary" ? "Тимчасово" : "Постійно"}</p>
        ${c.callbackDate ? `<p class="callback">🔔 Нагадування: ${formatDateIso(c.callbackDate)}</p>` : ""}
        <div class="detail-actions">
          <button class="btn primary" onclick='callNumber("${c.phone}")'>📞 Дзвонити</button>
          <button class="btn ghost" onclick='copyNumber("${c.phone}")'>📋 Копіювати</button>
          <button class="btn ghost" onclick='markCalled(${c.id})'>✔ Обдзвонений</button>
          <button class="btn ghost" onclick='markInterning(${c.id})'>👷 Стажується</button>
          <button class="btn ghost" onclick='markHired(${c.id})'>🏁 Прийнятий</button>
          <button class="btn ghost" onclick='markRejected(${c.id})'>✖ Відмова</button>
          <button class="btn ghost" onclick='deleteCandidate(${c.id})' style="background:rgba(255,60,60,0.12)">🗑 Видалити</button>
        </div>
        <div class="detail-meta">Додав: ${formatDateIso(c.created_at)}</div>
        ${c.internship ? `<div class="detail-intern">Інтерн: ${c.internship.place || "-"} • Початок: ${c.internship.start || "-"} • Днів: ${c.internship.days || 0}</div>` : ""}
      </div>
    </div>
  `;
  detailPanel.classList.remove("hidden");
}
closePanel && closePanel.addEventListener("click", () => detailPanel.classList.add("hidden"));

// MARK actions (PATCH)
async function markCalled(id) {
  await patchStatus(id, { status: "called" });
}
async function markInterning(id) {
  await patchStatus(id, { status: "interning" });
}
async function markHired(id) {
  await patchStatus(id, { status: "hired" });
}
async function markRejected(id) {
  await patchStatus(id, { status: "rejected" });
}
async function patchStatus(id, payload) {
  try {
    const res = await fetch(`/api/candidates/${id}/patch`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    });
    if (!res.ok) throw new Error("Patch failed");
  } catch (e) {
    console.error("patchStatus:", e);
  }
  await loadCandidates();
}
async function deleteCandidate(id) {
  if (!confirm("Видалити кандидата?")) return;
  try {
    const res = await fetch(`/api/candidates/${id}`, { method: "DELETE" });
    if (!res.ok) throw new Error("Delete failed");
  } catch (e) {
    console.error("deleteCandidate:", e);
  }
  await loadCandidates();
}

// INIT
loadCandidates();

// --------------------------- End of app.js ---------------------------
