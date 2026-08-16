declare module "katex/contrib/auto-render" {
  type RenderOptions = {
    delimiters?: Array<{
      left: string;
      right: string;
      display: boolean;
    }>;

    ignoredTags?: string[];

    ignoredClasses?: string[];

    throwOnError?: boolean;

    strict?:
      | boolean
      | "warn"
      | "error"
      | "ignore";
  };

  function renderMathInElement(
    element: HTMLElement,
    options?: RenderOptions
  ): void;

  export default renderMathInElement;
}