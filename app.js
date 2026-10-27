document.documentElement.classList.add("js");
const menu = document.querySelector(".menu");
const nav = document.querySelector("#main-nav");
function closeMenu() {
  nav?.classList.remove("open");
  menu?.setAttribute("aria-expanded", "false");
}
menu?.addEventListener("click", () => {
  const open = nav.classList.toggle("open");
  menu.setAttribute("aria-expanded", String(open));
});
document.addEventListener("keydown", (event) => {
  if (event.key === "Escape" && nav?.classList.contains("open")) {
    closeMenu();
    menu.focus();
  }
});
document.addEventListener("click", (event) => {
  if (!event.target.closest("header")) closeMenu();
});
nav?.addEventListener("click", (event) => {
  if (event.target.closest("a")) closeMenu();
});
window.matchMedia("(min-width: 741px)").addEventListener("change", closeMenu);
const crew = document.querySelector("#crew"),
  membership = document.querySelector("#membership"),
  tier = document.querySelector("#rate-tier");
function calculate() {
  const n = Number(crew.value),
    rate = Number(membership.value) - (tier?.value === "founder" ? 10 : 0);
  const valid = Number.isInteger(n) && n >= 1 && n <= 10000;
  crew.setCustomValidity(valid ? "" : "Enter a whole number from 1 to 10,000.");
  const money = new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: "USD",
    maximumFractionDigits: 0,
  });
  document.querySelector("#monthly").textContent = valid
    ? money.format(n * rate)
    : "—";
  document.querySelector("#annual").textContent = valid
    ? money.format(n * rate * 12)
    : "—";
}
crew?.addEventListener("input", calculate);
membership?.addEventListener("change", calculate);
tier?.addEventListener("change", calculate);
if (crew) calculate();
for (const form of document.querySelectorAll("form[data-inquiry]"))
  form.addEventListener("submit", async (event) => {
    event.preventDefault();
    if (form.dataset.submitting === "true") return;
    if (!form.reportValidity()) return;
    const status = form.parentElement.querySelector(".form-status");
    const button = form.querySelector('[type="submit"]');
    const label = button.textContent;
    const controller = new AbortController();
    const timeout = setTimeout(() => controller.abort(), 20000);
    form.dataset.submitting = "true";
    form.setAttribute("aria-busy", "true");
    button.disabled = true;
    button.textContent = "Sending…";
    status.classList.add("hidden");
    let submissionError = "";
    try {
      const response = await fetch(form.action, {
        method: "POST",
        headers: {
          Accept: "application/json",
          "Content-Type": "application/x-www-form-urlencoded",
        },
        body: new URLSearchParams(new FormData(form)).toString(),
        signal: controller.signal,
      });
      const result = await response.json();
      if (!response.ok || result.ok !== true) {
        submissionError = Array.isArray(result.errors)
          ? result.errors
              .map((error) => error.message)
              .filter((message) => typeof message === "string")
              .join(" ")
          : "";
        throw new Error("Submission failed");
      }
      window.location.assign(form.dataset.successUrl);
    } catch {
      status.textContent = submissionError
        ? `We couldn’t send your inquiry. ${submissionError} Your entries are still here.`
        : "We couldn’t confirm receipt of your inquiry. Please check your connection and try again. Your entries are still here. If you retry after a timeout, we may receive a duplicate.";
      status.classList.remove("hidden");
      status.focus();
    } finally {
      clearTimeout(timeout);
      form.dataset.submitting = "false";
      form.removeAttribute("aria-busy");
      button.disabled = false;
      button.textContent = label;
    }
  });
const state = document.querySelector("#state"),
  note = document.querySelector("#state-note");
state?.addEventListener("change", () =>
  note?.classList.toggle("hidden", state.value !== "Other"),
);
const referral = document.querySelector("#referralcode");
if (referral)
  referral.value = (
    new URLSearchParams(location.search).get("ref") || ""
  ).slice(0, 100);
const interest = document.querySelector("#interest");
const requestedInterest = new URLSearchParams(location.search).get("interest");
if (interest && ["founder-rate", "founding"].includes(requestedInterest)) {
  interest.value = requestedInterest;
}
