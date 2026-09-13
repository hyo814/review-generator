import { Copy, Check, RotateCcw, AlertCircle, Loader2, Sparkles } from 'lucide-react';
import { LanguageTabs, LANGUAGES } from './LanguageTabs';

/**
 * 출력 패널.
 * - 생성된 후기 표시
 * - 언어 탭으로 번역본 전환
 * - 복사 / 초기화 버튼
 *
 * 복사 폴백 패턴: navigator.clipboard 실패 시 execCommand로 자동 재시도.
 * iOS Safari·iframe 환경에서도 동작하도록 함.
 */

function fallbackCopy(text) {
  const textarea = document.createElement('textarea');
  textarea.value = text;
  textarea.setAttribute('readonly', '');
  textarea.style.position = 'fixed';
  textarea.style.left = '-9999px';
  textarea.style.opacity = '0';
  document.body.appendChild(textarea);

  const isIOS = /ipad|iphone|ipod/i.test(navigator.userAgent);
  if (isIOS) {
    const range = document.createRange();
    range.selectNodeContents(textarea);
    const sel = window.getSelection();
    sel.removeAllRanges();
    sel.addRange(range);
    textarea.setSelectionRange(0, 999999);
  } else {
    textarea.focus();
    textarea.select();
  }

  let success = false;
  try {
    success = document.execCommand('copy');
  } catch {
    success = false;
  }
  document.body.removeChild(textarea);
  return success;
}

export function OutputPanel({
  translations,
  activeLanguage,
  loading,
  translating,
  error,
  copied,
  setCopied,
  setError,
  onLanguageSelect,
  onReset,
}) {
  const currentText = translations[activeLanguage] || '';
  const hasOutput = !!translations.ko;

  const handleCopy = async () => {
    // 1차: 모던 Clipboard API
    if (navigator.clipboard?.writeText) {
      try {
        await navigator.clipboard.writeText(currentText);
        setCopied(true);
        setTimeout(() => setCopied(false), 2000);
        return;
      } catch {
        // 폴백으로 진행
      }
    }
    // 2차: execCommand 폴백
    if (fallbackCopy(currentText)) {
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
      return;
    }
    // 3차: 둘 다 실패
    setError('복사가 차단된 환경이에요. 출력 텍스트를 길게 눌러 직접 선택·복사해주세요.');
  };

  return (
    <div className="panel">
      <div className="panel-title-row">
        <h2>② 생성된 후기</h2>
        {hasOutput && (
          <div style={{ display: 'flex', gap: 8 }}>
            <button onClick={onReset} className="btn-mini ghost">
              <RotateCcw size={12} /> 초기화
            </button>
            <button
              onClick={handleCopy}
              className={`btn-mini ${copied ? 'success' : 'dark'}`}
            >
              {copied ? (
                <>
                  <Check size={12} /> 복사됨
                </>
              ) : (
                <>
                  <Copy size={12} /> 복사
                </>
              )}
            </button>
          </div>
        )}
      </div>

      {hasOutput && (
        <>
          <LanguageTabs
            active={activeLanguage}
            translations={translations}
            translating={translating}
            onSelect={onLanguageSelect}
          />
          <div className="cost-notice">
            번역은 호출당 <b>약 $0.05~0.10</b> 비용이 발생해요. 한 번 누른 언어는 자동 캐싱되어 다시 눌러도 추가 비용이 없으니, 필요한 언어만 골라서 눌러주세요.
          </div>
        </>
      )}

      {error && (
        <div className="error-box">
          <AlertCircle size={16} />
          <span>{error}</span>
        </div>
      )}

      {/* 최초 생성 로딩 */}
      {loading && !hasOutput && (
        <div className="skeleton-stack">
          {[100, 92, 78, 88, 65].map((w, i) => (
            <div key={i} className="skeleton-bar" style={{ width: `${w}%` }} />
          ))}
        </div>
      )}

      {/* 번역 중 */}
      {translating && !currentText && (
        <div className="translating-indicator">
          <Loader2 size={16} className="spin" />
          <span>{LANGUAGES[activeLanguage]?.label}로 번역 중...</span>
        </div>
      )}

      {/* 출력 */}
      {currentText && !loading && <pre className="output">{currentText}</pre>}

      {/* 빈 상태 */}
      {!hasOutput && !loading && !error && (
        <div className="empty-state">
          <div className="icon-circle">
            <Sparkles size={20} style={{ color: 'var(--color-accent)' }} />
          </div>
          <p>왼쪽 폼을 채우고 생성 버튼을 눌러주세요</p>
          <p className="sub">네이버/웹 검색 후 후기 자동 작성됨</p>
        </div>
      )}
    </div>
  );
}
