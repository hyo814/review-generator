import { Sparkles, Loader2 } from 'lucide-react';
import { StarRating } from './StarRating';

/**
 * 후기 정보 입력 폼.
 * App에서 폼 상태를 관리하고 props로 내려준다.
 */
export function ReviewForm({ form, setForm, onSubmit, loading, statusMsg }) {
  const update = (key) => (e) => setForm({ ...form, [key]: e.target.value });
  const setRating = (key) => (n) =>
    setForm({ ...form, ratings: { ...form.ratings, [key]: n } });

  return (
    <div className="panel">
      <h2 className="panel-title">① 정보 입력</h2>
      <div className="info-banner">
        예시 데이터가 미리 채워져 있어요. 그대로 <b>후기 생성하기</b>를 눌러봐도 되고, 가게에 맞게 자유롭게 수정해도 됩니다.
      </div>
      <div className="form-stack">
        <div>
          <label className="form-label">헤더 카테고리 태그 *</label>
          <input
            className="form-input"
            value={form.header_category}
            onChange={update('header_category')}
          />
        </div>

        <div className="form-row">
          <div>
            <label className="form-label">상호명 *</label>
            <input
              className="form-input"
              value={form.store_name}
              onChange={update('store_name')}
            />
          </div>
          <div>
            <label className="form-label">
              지역
              <span className="form-label-hint">(홍대·강남·부산 해운대·Tokyo Shibuya 등)</span>
            </label>
            <input
              className="form-input"
              value={form.region}
              onChange={update('region')}
              placeholder="예: 홍대, 부산 해운대, Tokyo Shibuya"
            />
          </div>
        </div>

        <div className="form-row">
          <div>
            <label className="form-label">
              시리즈명
            </label>
            <input
              className="form-input"
              value={form.series_name}
              onChange={update('series_name')}
              placeholder="예: 홍대투어"
            />
          </div>
          <div>
            <label className="form-label">회차 번호</label>
            <input
              className="form-input"
              value={form.episode_number}
              onChange={update('episode_number')}
            />
          </div>
        </div>

        <div>
          <label className="form-label">방문 메모 (자유롭게) *</label>
          <textarea
            className="form-textarea"
            rows={5}
            value={form.visit_memo}
            onChange={update('visit_memo')}
          />
        </div>

        <div>
          <label className="form-label">영업시간 (직접 복사 붙여넣기)</label>
          <textarea
            className="form-textarea"
            rows={3}
            value={form.business_hours}
            onChange={update('business_hours')}
          />
        </div>

        <div>
          <label className="form-label">
            주소
            <span className="form-label-hint">(번역에만 표시 · 한국어 그대로 노출)</span>
          </label>
          <input
            className="form-input"
            value={form.address}
            onChange={update('address')}
            placeholder="예: 서울 성동구 상원6가길 3 1층"
          />
        </div>

        <div>
          <label className="form-label">네이버 검색어 (리뷰 요약용)</label>
          <input
            className="form-input"
            value={form.search_query}
            onChange={update('search_query')}
          />
        </div>

        <div>
          <label className="form-label" style={{ marginTop: 8 }}>별점</label>
          <div className="rating-box">
            <StarRating label="맛" value={form.ratings.taste} onChange={setRating('taste')} />
            <StarRating label="서비스" value={form.ratings.service} onChange={setRating('service')} />
            <StarRating label="위치" value={form.ratings.location} onChange={setRating('location')} />
            <StarRating label="시설" value={form.ratings.facility} onChange={setRating('facility')} />
            <StarRating label="재방문의사" value={form.ratings.revisit} onChange={setRating('revisit')} />
          </div>
        </div>

        <button onClick={onSubmit} disabled={loading} className="btn-primary">
          {loading ? (
            <>
              <Loader2 size={18} className="spin" />
              {statusMsg || '생성 중...'}
            </>
          ) : (
            <>
              <Sparkles size={18} />
              후기 생성하기
            </>
          )}
        </button>
      </div>
    </div>
  );
}
