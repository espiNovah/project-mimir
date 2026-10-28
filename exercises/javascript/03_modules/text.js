// TODO: export slugify and truncate as named exports, and wordCount as the default export.

function slugify(title) {
  throw new Error("TODO: lower-case, replace runs of other characters with '-', trim '-'");
}

function truncate(text, max) {
  throw new Error("TODO: cut to exactly max characters, ending with '…'");
}

function wordCount(text) {
  return text.split(/\s+/).filter(Boolean).length;
}
