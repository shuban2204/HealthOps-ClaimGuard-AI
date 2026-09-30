export function formatPercent(value: number, digits = 0) {
  return `${(value * 100).toFixed(digits)}%`;
}

export function formatCurrency(value: number) {
  return new Intl.NumberFormat("en-US", { style: "currency", currency: "USD", maximumFractionDigits: 0 }).format(value);
}

export function humanizeFeature(feature: string) {
  return feature.replaceAll("_", " ").replace(/\b\w/g, (letter) => letter.toUpperCase());
}

