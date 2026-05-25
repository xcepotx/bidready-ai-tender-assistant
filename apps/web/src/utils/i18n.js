export function getUiLanguage() {
  return window.localStorage.getItem("bidreadyUiLanguage") || "en";
}

export function L(en, id) {
  return getUiLanguage() === "id" ? (id || en || "") : (en || id || "");
}

export function translateRequirementTextForUi(text, uiLanguage = "en") {
  if (!String(uiLanguage || "").toLowerCase().startsWith("id")) {
    return text || "";
  }

  let output = String(text || "");

  const direct = [
    ["Vendor shall provide application maintenance and support for existing enterprise", "Vendor harus menyediakan maintenance dan support aplikasi untuk enterprise yang sudah berjalan"],
    ["Vendor shall provide cloud infrastructure operation for production and non-", "Vendor harus menyediakan operasi infrastruktur cloud untuk production dan non-production"],
    ["Cloud engineers should hold relevant cloud certifications.", "Cloud engineer sebaiknya memiliki sertifikasi cloud yang relevan."],
    ["Payment shall be milestone-based.", "Pembayaran harus berbasis milestone."],
    ["Proposal must include executive summary, solution approach, delivery model, and", "Proposal harus mencakup ringkasan eksekutif, pendekatan solusi, model delivery, dan"],
    ["Data must be encrypted in transit and at rest.", "Data harus dienkripsi saat transit dan saat tersimpan."],
    ["Production data must remain within approved data", "Data production harus tetap berada dalam data center/lokasi yang disetujui"],
    ["Vendor must submit the proposal by 30 June 2026 at 15:00 local time.", "Vendor harus mengirimkan proposal paling lambat 30 Juni 2026 pukul 15:00 waktu setempat."],
    ["Vendor must provide at least 3 similar enterprise references.", "Vendor harus menyediakan minimal 3 referensi enterprise serupa."],
    ["Proposal validity period must be at least 90 days.", "Masa berlaku proposal harus minimal 90 hari."],
    ["Support must be available 24x7 for severity 1 incidents.", "Support harus tersedia 24x7 untuk insiden severity 1."],
    ["Vendor must provide monthly service reports.", "Vendor harus menyediakan laporan layanan bulanan."],
    ["Vendor must comply with ISO 27001 or equivalent standard.", "Vendor harus mematuhi ISO 27001 atau standar yang setara."],
    ["Vendor must provide project transition plan.", "Vendor harus menyediakan rencana transisi proyek."],
    ["Vendor must provide disaster recovery and backup procedure.", "Vendor harus menyediakan prosedur disaster recovery dan backup."],
    ["Vendor must ensure data privacy and confidentiality.", "Vendor harus memastikan privasi dan kerahasiaan data."],
  ];

  for (const [en, id] of direct) {
    output = output.replace(en, id);
  }

  const phrases = [
    ["Vendor shall", "Vendor harus"],
    ["Vendor must", "Vendor harus"],
    ["Vendor should", "Vendor sebaiknya"],
    ["must provide", "harus menyediakan"],
    ["shall provide", "harus menyediakan"],
    ["should provide", "sebaiknya menyediakan"],
    ["must include", "harus mencakup"],
    ["should hold", "sebaiknya memiliki"],
    ["must comply with", "harus mematuhi"],
    ["must ensure", "harus memastikan"],
    ["must submit", "harus mengirimkan"],
    ["application maintenance and support", "maintenance dan support aplikasi"],
    ["cloud infrastructure operation", "operasi infrastruktur cloud"],
    ["existing enterprise", "enterprise yang sudah berjalan"],
    ["production and non-production", "production dan non-production"],
    ["relevant cloud certifications", "sertifikasi cloud yang relevan"],
    ["milestone-based", "berbasis milestone"],
    ["executive summary", "ringkasan eksekutif"],
    ["solution approach", "pendekatan solusi"],
    ["delivery model", "model delivery"],
    ["encrypted in transit and at rest", "dienkripsi saat transit dan saat tersimpan"],
    ["similar enterprise references", "referensi enterprise serupa"],
    ["proposal validity period", "masa berlaku proposal"],
    ["local time", "waktu setempat"],
    ["monthly service reports", "laporan layanan bulanan"],
    ["project transition plan", "rencana transisi proyek"],
    ["disaster recovery", "disaster recovery"],
    ["backup procedure", "prosedur backup"],
    ["data privacy and confidentiality", "privasi dan kerahasiaan data"],
  ];

  for (const [en, id] of phrases) {
    output = output.replaceAll(en, id);
  }

  return output;
}
