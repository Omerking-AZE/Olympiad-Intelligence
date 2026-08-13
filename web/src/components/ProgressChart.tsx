import type { ProgressPoint } from "../types/student";

type Props = {
  data: ProgressPoint[];
};

export default function ProgressChart({
  data,
}: Props) {
  if (data.length === 0) {
    return (
      <div className="chart-empty">
        Not enough progression data yet.
      </div>
    );
  }

  const width = 1200;
  const height = 340;

  const paddingLeft = 58;
  const paddingRight = 28;
  const paddingTop = 28;
  const paddingBottom = 52;

  const chartWidth =
    width - paddingLeft - paddingRight;

  const chartHeight =
    height - paddingTop - paddingBottom;

  const minOvr = 50;
  const maxOvr = 100;

  const getX = (index: number) => {
    if (data.length === 1) {
      return (
        paddingLeft +
        chartWidth / 2
      );
    }

    return (
      paddingLeft +
      (index / (data.length - 1)) *
        chartWidth
    );
  };

  const getY = (ovr: number) => {
    return (
      paddingTop +
      ((maxOvr - ovr) /
        (maxOvr - minOvr)) *
        chartHeight
    );
  };

  const points = data
    .map(
      (point, index) =>
        `${getX(index)},${getY(
          point.overall_rating
        )}`
    )
    .join(" ");

  const levels = [
    50,
    60,
    70,
    80,
    90,
    100,
  ];

  return (
    <div className="progress-chart">
      <svg
        viewBox={`0 0 ${width} ${height}`}
        className="progress-svg"
        role="img"
        aria-label="Student OVR progression"
      >
        {levels.map((level) => {
          const y = getY(level);

          return (
            <g key={level}>
              <line
                x1={paddingLeft}
                y1={y}
                x2={width - paddingRight}
                y2={y}
                className="chart-grid-line"
              />

              <text
                x={18}
                y={y + 4}
                className="chart-axis-label"
              >
                {level}
              </text>
            </g>
          );
        })}

        <polyline
          points={points}
          fill="none"
          className="chart-line"
          strokeWidth="5"
          strokeLinecap="round"
          strokeLinejoin="round"
        />

        {data.map((point, index) => {
          const x = getX(index);
          const y = getY(
            point.overall_rating
          );

          return (
            <g
              key={`${point.attempts}-${index}`}
            >
              <circle
                cx={x}
                cy={y}
                r="7"
                className="chart-point"
              />

              <text
                x={x}
                y={y - 15}
                textAnchor="middle"
                className="chart-value-label"
              >
                {point.overall_rating}
              </text>

              <text
                x={x}
                y={height - 16}
                textAnchor="middle"
                className="chart-axis-label"
              >
                {point.attempts}P
              </text>
            </g>
          );
        })}
      </svg>
    </div>
  );
}