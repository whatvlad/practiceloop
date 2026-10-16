interface StatTileProps {
  label: string;
  value: number;
  /** Shown as "/ n" after the value. */
  of?: number;
  /** 0–100 fill for the monochrome bar. */
  fill?: number;
  caption?: string;
}

export function StatTile({ label, value, of, fill, caption }: StatTileProps) {
  return (
    <div className="pl-stat">
      <span className="pl-label">{label}</span>
      <div className="v">
        {value}
        {of !== undefined && <small>/ {of}</small>}
      </div>
      {caption && <span className="pl-small pl-muted">{caption}</span>}
      {fill !== undefined && (
        <div className="pl-bar" aria-hidden="true">
          <i style={{ width: `${Math.max(0, Math.min(100, fill))}%` }} />
        </div>
      )}
    </div>
  );
}
