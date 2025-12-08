// 22 Scheduled Indian Languages
const LANGUAGES = [
  { code: "as", name: "Assamese" },
  { code: "bn", name: "Bengali" },
  { code: "bho", name: "Bodo" }, // used "bho" as placeholder
  { code: "dog", name: "Dogri" },
  { code: "gu", name: "Gujarati" },
  { code: "hi", name: "Hindi" },
  { code: "kn", name: "Kannada" },
  { code: "ks", name: "Kashmiri" },
  { code: "kok", name: "Konkani" },
  { code: "mai", name: "Maithili" },
  { code: "ml", name: "Malayalam" },
  { code: "mni", name: "Manipuri (Meitei)" },
  { code: "mr", name: "Marathi" },
  { code: "ne", name: "Nepali" },
  { code: "or", name: "Odia" },
  { code: "pa", name: "Punjabi" },
  { code: "sa", name: "Sanskrit" },
  { code: "sat", name: "Santhali" },
  { code: "sd", name: "Sindhi" },
  { code: "ta", name: "Tamil" },
  { code: "te", name: "Telugu" },
  { code: "ur", name: "Urdu" }
];

document.addEventListener("DOMContentLoaded", () => {
  const uiLanguageSelect = document.getElementById("uiLanguageSelect");
  const videoLanguageSelect = document.getElementById("videoLanguageSelect");
  const transcriptLanguageSelect = document.getElementById("transcriptLanguageSelect");
  const captionLanguageSelect = document.getElementById("captionLanguageSelect");

  const videoLangLabel = document.getElementById("videoLangLabel");
  const transcriptLangLabel = document.getElementById("transcriptLangLabel");
  const captionLangLabel = document.getElementById("captionLangLabel");

  const descriptionText = document.getElementById("descriptionText");
  const descriptionLangChip = document.getElementById("descriptionLangChip");
  const transcriptText = document.getElementById("transcriptText");
  const transcriptLangChip = document.getElementById("transcriptLangChip");

  const applyLocalizationBtn = document.getElementById("applyLocalizationBtn");

  const tabButtons = document.querySelectorAll(".tab-button");
  const tabPanels = document.querySelectorAll(".tab-panel");

  // Helper: create options for a select
  function populateLanguageSelect(selectEl, includePlaceholder = true) {
    if (includePlaceholder) {
      const ph = document.createElement("option");
      ph.value = "";
      ph.textContent = "Select language";
      selectEl.appendChild(ph);
    }

    LANGUAGES.forEach(lang => {
      const opt = document.createElement("option");
      opt.value = lang.code;
      opt.textContent = lang.name;
      selectEl.appendChild(opt);
    });
  }

  // Populate selects for UI, video, transcript, captions
  populateLanguageSelect(uiLanguageSelect, false);
  populateLanguageSelect(videoLanguageSelect);
  populateLanguageSelect(transcriptLanguageSelect);
  populateLanguageSelect(captionLanguageSelect);

  // Set some sensible defaults
  uiLanguageSelect.value = "en"; // we will add this manually
  const uiExtraOption = document.createElement("option");
  uiExtraOption.value = "en";
  uiExtraOption.textContent = "English (Default)";
  uiLanguageSelect.insertBefore(uiExtraOption, uiLanguageSelect.firstChild);

  videoLanguageSelect.value = "hi";
  transcriptLanguageSelect.value = "hi";
  captionLanguageSelect.value = "hi";

  // Update label helpers
  function getLanguageName(code) {
    if (code === "en") return "English (Default)";
    const match = LANGUAGES.find(l => l.code === code);
    return match ? match.name : "-";
  }

  function updateInlineLabels() {
    videoLangLabel.textContent = getLanguageName(videoLanguageSelect.value);
    transcriptLangLabel.textContent = getLanguageName(transcriptLanguageSelect.value);
    captionLangLabel.textContent = getLanguageName(captionLanguageSelect.value);
  }

  updateInlineLabels();

  // When Apply Localization is clicked, update text areas to reflect choices
  applyLocalizationBtn.addEventListener("click", () => {
    const uiLang = uiLanguageSelect.value || "en";
    const videoLang = videoLanguageSelect.value;
    const transcriptLang = transcriptLanguageSelect.value;
    const captionLang = captionLanguageSelect.value;

    // Update chips / labels
    updateInlineLabels();
    descriptionLangChip.textContent = getLanguageName(uiLang);
    transcriptLangChip.textContent = getLanguageName(transcriptLang);

    // Generate sample localized messages (demo only)
    descriptionText.textContent =
      "You are viewing this lesson with the interface language set to " +
      getLanguageName(uiLang) +
      ". In a real LMS, this description, buttons, and labels would be fully localized.";

    transcriptText.textContent =
      "Sample transcript note: The transcript language is set to " +
      getLanguageName(transcriptLang) +
      ". Here you would see the full lesson transcript in the selected language. " +
      "Captions during video playback would appear in " +
      getLanguageName(captionLang) +
      ".";

    // Small visual feedback
    applyLocalizationBtn.classList.add("pulse-once");
    setTimeout(() => {
      applyLocalizationBtn.classList.remove("pulse-once");
    }, 300);

    console.log("Localization applied:", {
      uiLang,
      videoLang,
      transcriptLang,
      captionLang
    });
  });

  // Simple tab switching
  tabButtons.forEach(btn => {
    btn.addEventListener("click", () => {
      const target = btn.getAttribute("data-tab");

      tabButtons.forEach(b => b.classList.remove("active"));
      btn.classList.add("active");
      
      tabPanels.forEach(panel => {
        if (panel.id === "tab-" + target) {
          panel.classList.add("active");
        } else {
          panel.classList.remove("active");
        }
      });
    });
  });
});
