import katex from "katex";

import "katex/dist/katex.min.css";

type ProblemTextProps = {
  text: string;
};

type TextPart = {
  type: "text";
  value: string;
};

type MathPart = {
  type: "math";
  value: string;
  display: boolean;
};

type Part = TextPart | MathPart;


/**
 * Extracts mathematical expressions from a problem statement.
 *
 * Supported forms:
 *
 * $$ ... $$      display math
 * $ ... $        inline math
 * \( ... \)      inline math
 * \[ ... \]      display math
 *
 * The order matters:
 * $$ must be checked before $
 */
function tokenize(
  source: string
): Part[] {
  const parts: Part[] = [];

  let buffer = "";
  let index = 0;

  const flushText = () => {
    if (!buffer) {
      return;
    }

    parts.push({
      type: "text",
      value: buffer,
    });

    buffer = "";
  };

  while (index < source.length) {
    /*
     * --------------------------------------------------------
     * DISPLAY: $$ ... $$
     * --------------------------------------------------------
     */

    if (source.startsWith("$$", index)) {
      const end = source.indexOf(
        "$$",
        index + 2
      );

      if (end !== -1) {
        const expression =
          source
            .slice(
              index + 2,
              end
            )
            .trim();

        if (expression) {
          flushText();

          parts.push({
            type: "math",
            value: expression,
            display: true,
          });

          index = end + 2;
          continue;
        }
      }
    }

    /*
     * --------------------------------------------------------
     * DISPLAY: \[ ... \]
     * --------------------------------------------------------
     */

    if (source.startsWith("\\[", index)) {
      const end = source.indexOf(
        "\\]",
        index + 2
      );

      if (end !== -1) {
        const expression =
          source
            .slice(
              index + 2,
              end
            )
            .trim();

        if (expression) {
          flushText();

          parts.push({
            type: "math",
            value: expression,
            display: true,
          });

          index = end + 2;
          continue;
        }
      }
    }

    /*
     * --------------------------------------------------------
     * INLINE: \( ... \)
     * --------------------------------------------------------
     */

    if (source.startsWith("\\(", index)) {
      const end = source.indexOf(
        "\\)",
        index + 2
      );

      if (end !== -1) {
        const expression =
          source
            .slice(
              index + 2,
              end
            )
            .trim();

        if (expression) {
          flushText();

          parts.push({
            type: "math",
            value: expression,
            display: false,
          });

          index = end + 2;
          continue;
        }
      }
    }

    /*
     * --------------------------------------------------------
     * INLINE: $ ... $
     * --------------------------------------------------------
     *
     * Do not treat $$ as inline math.
     */

    if (
      source[index] === "$" &&
      source[index + 1] !== "$" &&
      source[index - 1] !== "\\"
    ) {
      const end = source.indexOf(
        "$",
        index + 1
      );

      if (end !== -1) {
        const expression =
          source
            .slice(
              index + 1,
              end
            )
            .trim();

        /*
         * Reject multiline dollar blocks.
         * Those should normally use $$.
         */
        if (
          expression &&
          !expression.includes("\n")
        ) {
          flushText();

          parts.push({
            type: "math",
            value: expression,
            display: false,
          });

          index = end + 1;
          continue;
        }
      }
    }

    /*
     * --------------------------------------------------------
     * NORMAL TEXT
     * --------------------------------------------------------
     */

    buffer += source[index];
    index += 1;
  }

  flushText();

  return parts;
}


/**
 * Render a LaTeX expression directly to HTML.
 *
 * We deliberately render synchronously instead of:
 * - manipulating DOM after render
 * - searching text nodes
 * - running another React effect
 *
 * This makes the result deterministic.
 */
function renderMath(
  expression: string,
  display: boolean
): string {
  try {
    return katex.renderToString(
      expression,
      {
        displayMode: display,
        throwOnError: false,
        strict: false,
        trust: false,
        output: "htmlAndMathml",
      }
    );
  } catch (error) {
    console.error(
      "KaTeX rendering failed:",
      expression,
      error
    );

    return `
      <span class="oi-math-error">
        ${escapeHtml(expression)}
      </span>
    `;
  }
}


/**
 * Escape normal text used inside the very rare
 * math-error fallback.
 */
function escapeHtml(
  value: string
): string {
  return value
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll(
      "'",
      "&#039;"
    );
}


/**
 * Convert ordinary problem text into React-safe
 * line-separated text.
 */
function renderPlainText(
  value: string
): React.ReactNode {
  const lines =
    value.split("\n");

  return lines.map(
    (
      line,
      index
    ) => (
      <span
        key={index}
        className="oi-problem-text-line"
      >
        {line}

        {index <
          lines.length - 1 && (
          <br />
        )}
      </span>
    )
  );
}


export default function ProblemText({
  text,
}: ProblemTextProps) {
  const normalized =
    text
      .replace(/\r\n/g, "\n")
      .replace(/\r/g, "\n");

  const parts =
    tokenize(normalized);

  return (
    <div className="oi-rendered-problem">
      {parts.map(
        (
          part,
          index
        ) => {
          /*
           * ------------------------------------------------------
           * NORMAL TEXT
           * ------------------------------------------------------
           */

          if (
            part.type ===
            "text"
          ) {
            return (
              <span
                key={index}
                className="oi-problem-text-content"
              >
                {renderPlainText(
                  part.value
                )}
              </span>
            );
          }

          /*
           * ------------------------------------------------------
           * MATH
           * ------------------------------------------------------
           */

          return (
            <span
              key={index}
              className={
                part.display
                  ? "oi-math-display"
                  : "oi-math-inline"
              }
              dangerouslySetInnerHTML={{
                __html:
                  renderMath(
                    part.value,
                    part.display
                  ),
              }}
            />
          );
        }
      )}
    </div>
  );
}