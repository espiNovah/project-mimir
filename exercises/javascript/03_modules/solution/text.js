export function slugify(title) {
  return title.toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/^-+|-+$/g, "");
}

export function truncate(text, max) {
  return text.length <= max ? text : text.slice(0, max - 1) + "…";
}

export default function wordCount(text) {
  return text.split(/\s+/).filter(Boolean).length;
}
