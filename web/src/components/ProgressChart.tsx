import type {
  ProgressPoint,
} from "../types/student";

type ProgressChartProps = {
  data: ProgressPoint[];
};

function valueFor(
  point: ProgressPoint
) {
  const raw =
    point.rating ??
    point.overall_rating ??
    0;

  const value = Number(raw);

  return Number.isFinite(value)
    ? value
    : 0;
}

export default function ProgressChart({
  data,
}: ProgressChartProps) {
  if (!data.length) {
    return (
      <section className="oi-section">
        <div className="oi-section-heading">
          <div>
            <span className="oi-eyebrow">
              PLAYER DEVELOPMENT
            </span>

            <h2>
              OVR Progression
            </h2>
          </div>
        </div>

        <div className="oi-chart-card oi-chart-empty">
          No progression data
          available.
        </div>
      </section>
    );
  }

  const points =
    data.map(valueFor);

  const min =
    Math.min(...points);

  const max =
    Math.max(...points);

  const range =
    Math.max(
      1,
      max - min
    );

  const width = 920;
  const height = 340;

  const padX = 48;
  const padY = 34;

  const coords =
    points.map(
      (
        value,
        index
      ) => {
        const x =
          padX +
          ((width -
            padX * 2) *
            index) /
            Math.max(
              1,
              points.length -
                1
            );

        const y =
          height -
          padY -
          ((value - min) /
            range) *
            (height -
              padY * 2);

        return {
          x,
          y,
          value,
        };
      }
    );

  const line =
    coords
      .map(
        (
          point,
          index
        ) =>
          `${
            index
              ? "L"
              : "M"
          } ${point.x} ${point.y}`
      )
      .join(" ");

  const area =
    `${line} L ${
      coords[
        coords.length - 1
      ].x
    } ${
      height - padY
    } L ${
      coords[0].x
    } ${
      height - padY
    } Z`;

  return (
    <section className="oi-section">
      <div className="oi-section-heading">
        <div>
          <span className="oi-eyebrow">
            PLAYER DEVELOPMENT
          </span>

          <h2>
            OVR Progression
          </h2>
        </div>

        <span className="oi-section-note">
          Historical performance
        </span>
      </div>

      <div className="oi-chart-card">
        <svg
          className="oi-chart"
          viewBox={`0 0 ${width} ${height}`}
          role="img"
          aria-label="Overall rating progression chart"
        >
          {[0, 1, 2, 3].map(
            (row) => {
              const y =
                padY +
                ((height -
                  padY * 2) *
                  row) /
                  3;

              return (
                <line
                  key={row}
                  x1={padX}
                  x2={
                    width -
                    padX
                  }
                  y1={y}
                  y2={y}
                  className="oi-chart-grid"
                />
              );
            }
          )}

          <path
            d={area}
            className="oi-chart-area"
          />

          <path
            d={line}
            className="oi-chart-line"
          />

          {coords.map(
            (
              point,
              index
            ) => (
              <g
                key={`${point.x}-${index}`}
              >
                <circle
                  cx={point.x}
                  cy={point.y}
                  r="6"
                  className="oi-chart-point"
                />

                <text
                  x={point.x}
                  y={point.y - 14}
                  textAnchor="middle"
                  className="oi-chart-value"
                >
                  {point.value}
                </text>

                <text
                  x={point.x}
                  y={height - 10}
                  textAnchor="middle"
                  className="oi-chart-label"
                >
                  {data[index]
                    ?.date ??
                    data[index]
                      ?.contest ??
                    `#${index + 1}`}
                </text>
              </g>
            )
          )}
        </svg>
      </div>
    </section>
  );
}