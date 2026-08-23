const test = require("node:test");
const assert = require("node:assert/strict");
const { add, formatCurrency } = require("./math");

test("adds two numbers", () => {
  assert.equal(add(2, 3), 5);
});

test("formats currency", () => {
  assert.equal(formatCurrency(10), "$10.00");
});
