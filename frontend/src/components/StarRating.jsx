import { Star } from 'lucide-react';

export function StarRating({ value, onChange, label }) {
  return (
    <div className="rating-row">
      <span className="label">{label}</span>
      <div className="stars">
        {[1, 2, 3, 4, 5].map((n) => (
          <button
            key={n}
            type="button"
            onClick={() => onChange(n)}
            className="star-button"
            aria-label={`${label} ${n}점`}
          >
            <Star
              size={22}
              fill={n <= value ? 'var(--color-star)' : 'transparent'}
              stroke={n <= value ? 'var(--color-star)' : 'var(--color-star-empty)'}
              strokeWidth={1.5}
            />
          </button>
        ))}
      </div>
    </div>
  );
}
