// Surligne dans le texte brut la portion correspondant à span {start, end}.
// Chaque chiffre affiche sa phrase source surlignée dans le texte d'origine
// (dev-brief §3.2).
export default function QuoteHighlight({
  text,
  span,
}: {
  text: string;
  span?: { start: number; end: number } | null;
}) {
  if (!span || span.start == null || span.end == null) {
    return <p className="whitespace-pre-wrap text-sm leading-6">{text}</p>;
  }
  const before = text.slice(0, span.start);
  const highlighted = text.slice(span.start, span.end);
  const after = text.slice(span.end);
  return (
    <p className="whitespace-pre-wrap text-sm leading-6">
      {before}
      <mark>{highlighted}</mark>
      {after}
    </p>
  );
}
