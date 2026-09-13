import { useState, useEffect, useCallback } from 'react';
import { Sparkles } from 'lucide-react';
import { ReviewForm } from './components/ReviewForm';
import { OutputPanel } from './components/OutputPanel';
import { HistoryList } from './components/HistoryList';
import { api } from './api/client';

// 폼 기본값은 frontend/.env 의 VITE_DEFAULT_* 에서 읽음 (빌드 시 주입, 없으면 빈 칸)
const env = import.meta.env;
const INITIAL_FORM = {
  header_category: env.VITE_DEFAULT_HEADER_CATEGORY || '',
  store_name: env.VITE_DEFAULT_STORE_NAME || '',
  region: env.VITE_DEFAULT_REGION || '',
  series_name: env.VITE_DEFAULT_SERIES_NAME || '',
  episode_number: env.VITE_DEFAULT_EPISODE_NUMBER || '1',
  visit_memo: env.VITE_DEFAULT_VISIT_MEMO || '',
  business_hours: env.VITE_DEFAULT_BUSINESS_HOURS || '',
  address: env.VITE_DEFAULT_ADDRESS || '',
  search_query: env.VITE_DEFAULT_SEARCH_QUERY || '',
  ratings: { taste: 4, service: 3, location: 3, facility: 3, revisit: 4 },
};

export default function App() {
  const [form, setForm] = useState(INITIAL_FORM);

  // 출력 상태
  const [reviewId, setReviewId] = useState(null); // DB id (번역 호출에 사용)
  const [translations, setTranslations] = useState({ ko: '', en: '', ja: '', zh: '' });
  const [activeLanguage, setActiveLanguage] = useState('ko');
  const [loading, setLoading] = useState(false);
  const [translating, setTranslating] = useState(false);
  const [statusMsg, setStatusMsg] = useState('');
  const [error, setError] = useState(null);
  const [copied, setCopied] = useState(false);

  // 히스토리 (load-more 패턴: 처음 PAGE_SIZE건, "더 보기"로 다음 PAGE_SIZE건 누적)
  const PAGE_SIZE = 20;
  const [history, setHistory] = useState([]);
  const [historyLoading, setHistoryLoading] = useState(false);
  const [historyLoadingMore, setHistoryLoadingMore] = useState(false);
  const [historyHasMore, setHistoryHasMore] = useState(false);

  const refreshHistory = useCallback(async () => {
    setHistoryLoading(true);
    try {
      const items = await api.history(PAGE_SIZE, 0);
      setHistory(items);
      setHistoryHasMore(items.length === PAGE_SIZE);
    } catch (err) {
      console.error('히스토리 조회 실패:', err);
    } finally {
      setHistoryLoading(false);
    }
  }, []);

  const loadMoreHistory = useCallback(async () => {
    if (historyLoadingMore || !historyHasMore) return;
    setHistoryLoadingMore(true);
    try {
      const next = await api.history(PAGE_SIZE, history.length);
      setHistory((prev) => [...prev, ...next]);
      setHistoryHasMore(next.length === PAGE_SIZE);
    } catch (err) {
      console.error('히스토리 더 불러오기 실패:', err);
    } finally {
      setHistoryLoadingMore(false);
    }
  }, [history.length, historyHasMore, historyLoadingMore]);

  useEffect(() => {
    refreshHistory();
  }, [refreshHistory]);

  // ── 후기 생성 ──
  const handleGenerate = async () => {
    if (!form.store_name.trim() || !form.visit_memo.trim() || !form.header_category.trim()) {
      setError('헤더 카테고리, 상호명, 방문 메모는 필수예요.');
      return;
    }

    setLoading(true);
    setError(null);
    setTranslations({ ko: '', en: '', ja: '', zh: '' });
    setActiveLanguage('ko');
    setReviewId(null);
    setCopied(false);
    setStatusMsg('네이버/웹 검색 + 후기 작성 중... (15~30초 소요)');

    try {
      const res = await api.generate(form);
      setReviewId(res.id);
      setTranslations({ ko: res.korean, en: '', ja: '', zh: '' });
      setActiveLanguage('ko');
      // 히스토리 갱신
      refreshHistory();
    } catch (err) {
      setError(err.message || '알 수 없는 오류가 발생했어요.');
    } finally {
      setLoading(false);
      setStatusMsg('');
    }
  };

  // ── 번역 ──
  const handleLanguageSelect = async (lang) => {
    // 이미 캐시된 언어 또는 한국어 → 즉시 전환
    if (lang === 'ko' || translations[lang]) {
      setActiveLanguage(lang);
      setError(null);
      setCopied(false);
      return;
    }
    if (!reviewId || !translations.ko) return;

    setActiveLanguage(lang);
    setTranslating(true);
    setError(null);
    setCopied(false);

    try {
      const res = await api.translate(reviewId, lang);
      setTranslations((prev) => ({ ...prev, [lang]: res.translated }));
    } catch (err) {
      setError(err.message || '번역 실패');
      setActiveLanguage('ko');
    } finally {
      setTranslating(false);
    }
  };

  // ── 초기화 ──
  const handleReset = () => {
    setTranslations({ ko: '', en: '', ja: '', zh: '' });
    setActiveLanguage('ko');
    setReviewId(null);
    setError(null);
    setCopied(false);
  };

  // ── 히스토리에서 불러오기 ──
  const handleLoadFromHistory = async (id) => {
    setError(null);
    try {
      const r = await api.getReview(id);
      setReviewId(r.id);
      setTranslations({
        ko: r.korean_output || '',
        en: r.en_output || '',
        ja: r.ja_output || '',
        zh: r.zh_output || '',
      });
      setActiveLanguage('ko');
      // 폼도 같이 채워줌 → 같은 가게 다시 생성하기 편함
      setForm({
        header_category: r.header_category,
        store_name: r.store_name,
        region: r.region,
        series_name: r.series_name,
        episode_number: r.episode_number,
        visit_memo: r.visit_memo,
        business_hours: r.business_hours,
        address: r.address || '',
        search_query: r.search_query,
        ratings: r.ratings,
      });
      // 페이지 상단으로 스크롤
      window.scrollTo({ top: 0, behavior: 'smooth' });
    } catch (err) {
      setError(err.message || '불러오기 실패');
    }
  };

  // ── 히스토리 삭제 ──
  const handleDeleteFromHistory = async (id) => {
    try {
      await api.deleteReview(id);
      // 현재 보고 있던 후기를 삭제했다면 출력 패널도 초기화
      if (reviewId === id) handleReset();
      refreshHistory();
    } catch (err) {
      setError(err.message || '삭제 실패');
    }
  };

  return (
    <div className="app">
      <div className="container">
        <div className="app-header">
          <h1>
            <Sparkles size={26} style={{ color: 'var(--color-accent)' }} />
            SNS 후기 자동 생성기
          </h1>
          <p>폼을 채우면 네이버/웹 리뷰를 자동 분석해서 후기 글을 생성해줘요.</p>
        </div>

        <div className="grid-2col">
          <ReviewForm
            form={form}
            setForm={setForm}
            onSubmit={handleGenerate}
            loading={loading}
            statusMsg={statusMsg}
          />
          <OutputPanel
            translations={translations}
            activeLanguage={activeLanguage}
            loading={loading}
            translating={translating}
            error={error}
            copied={copied}
            setCopied={setCopied}
            setError={setError}
            onLanguageSelect={handleLanguageSelect}
            onReset={handleReset}
          />
        </div>

        <HistoryList
          items={history}
          loading={historyLoading}
          loadingMore={historyLoadingMore}
          hasMore={historyHasMore}
          onLoad={handleLoadFromHistory}
          onDelete={handleDeleteFromHistory}
          onRefresh={refreshHistory}
          onLoadMore={loadMoreHistory}
        />

        <div className="app-footer">
          Powered by Claude · 후기는 AI 생성물이므로 게시 전 사실관계 한 번 더 확인해주세요
        </div>
      </div>
    </div>
  );
}
