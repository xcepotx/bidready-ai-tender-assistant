export default function LanguageSelector({ languageSetting, updateLanguageSetting, busy }) {
  const outputLanguage = languageSetting?.output_language || "en";
  const inputLanguage = languageSetting?.input_language || "auto";

  return (
    <div className="languageSelector">
      <span>Language</span>

      <div className="languageSelectorGrid">
        <label>
          Input
          <select
            value={inputLanguage}
            disabled={busy}
            onChange={(e) => updateLanguageSetting({ input_language: e.target.value })}
          >
            <option value="auto">Auto detect</option>
            <option value="en">English</option>
            <option value="id">Indonesia</option>
          </select>
        </label>

        <label>
          Output
          <select
            value={outputLanguage}
            disabled={busy}
            onChange={(e) => updateLanguageSetting({ output_language: e.target.value })}
          >
            <option value="en">English</option>
            <option value="id">Indonesia</option>
          </select>
        </label>
      </div>

      <small>
        {outputLanguage === "id"
          ? "Generated analysis will use Bahasa Indonesia after regeneration."
          : "Generated analysis will use English after regeneration."}
      </small>
    </div>
  );
}
