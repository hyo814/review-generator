import { Eye, Trash2, RefreshCw, ChevronDown, Loader2 } from 'lucide-react';

function formatDate(iso) {
  const d = new Date(iso);
  const yyyy = d.getFullYear();
  const mm = String(d.getMonth() + 1).padStart(2, '0');
  const dd = String(d.getDate()).padStart(2, '0');
  const hh = String(d.getHours()).padStart(2, '0');
  const mi = String(d.getMinutes()).padStart(2, '0');
  return `${yyyy}.${mm}.${dd} ${hh}:${mi}`;
}

export function HistoryList({
  items,
  onLoad,
  onDelete,
  onRefresh,
  onLoadMore,
  loading,
  loadingMore,
  hasMore,
}) {
  return (
    <div className="panel history-panel">
      <div className="panel-title-row">
        <h2>③ 히스토리 <span className="history-count">({items.length}건{hasMore ? '+' : ''})</span></h2>
        <button onClick={onRefresh} className="btn-mini ghost" disabled={loading}>
          <RefreshCw size={12} className={loading ? 'spin' : ''} /> 새로고침
        </button>
      </div>

      {items.length === 0 ? (
        <div className="history-empty">아직 생성된 후기가 없어요.</div>
      ) : (
        <>
          <ul className="history-list">
            {items.map((item) => (
              <li key={item.id} className="history-item">
                <div className="history-item-info">
                  <span className="name">{item.store_name}</span>
                  <span className="meta">
                    {item.region} · {formatDate(item.created_at)}
                  </span>
                </div>
                <div className="history-actions">
                  <button onClick={() => onLoad(item.id)} className="btn-mini ghost">
                    <Eye size={12} /> 불러오기
                  </button>
                  <button
                    onClick={() => {
                      if (confirm(`'${item.store_name}' 후기를 삭제할까요?`)) {
                        onDelete(item.id);
                      }
                    }}
                    className="btn-mini ghost"
                    style={{ color: 'var(--color-error-text)' }}
                  >
                    <Trash2 size={12} />
                  </button>
                </div>
              </li>
            ))}
          </ul>

          {hasMore ? (
            <button
              onClick={onLoadMore}
              disabled={loadingMore}
              className="btn-load-more"
            >
              {loadingMore ? (
                <>
                  <Loader2 size={14} className="spin" /> 불러오는 중...
                </>
              ) : (
                <>
                  <ChevronDown size={14} /> 더 보기
                </>
              )}
            </button>
          ) : (
            items.length > 20 && (
              <div className="history-end">모든 히스토리를 불러왔어요.</div>
            )
          )}
        </>
      )}
    </div>
  );
}
