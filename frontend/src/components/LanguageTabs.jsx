import { Languages, Loader2, Check } from 'lucide-react';

const LANGUAGES = {
  ko: { label: '한국어' },
  en: { label: 'English' },
  ja: { label: '日本語' },
  zh: { label: '中文' },
};

export function LanguageTabs({ active, translations, translating, onSelect }) {
  return (
    <div className="lang-tabs-wrap">
      <div className="lang-tabs-label">
        <Languages size={14} style={{ color: 'var(--color-accent)' }} />
        <span>번역 (탭을 클릭하면 해당 언어로 변환)</span>
      </div>
      <div className="lang-tabs">
        {Object.entries(LANGUAGES).map(([code, info]) => {
          const isActive = active === code;
          const isCached = !!translations[code];
          const isLoading = translating && isActive && !isCached;
          return (
            <button
              key={code}
              onClick={() => onSelect(code)}
              disabled={translating}
              className={`lang-tab ${isActive ? 'active' : ''}`}
            >
              {isLoading && <Loader2 size={11} className="spin" />}
              <span>{info.label}</span>
              {isCached && code !== 'ko' && !isActive && (
                <Check size={10} style={{ color: 'var(--color-success)', flexShrink: 0 }} />
              )}
            </button>
          );
        })}
      </div>
    </div>
  );
}

export { LANGUAGES };
