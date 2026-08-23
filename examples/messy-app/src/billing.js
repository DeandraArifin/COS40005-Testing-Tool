function calculateInvoiceTotal(items) {
  let total = 0;
  for (const item of items) {
    const line = item.price * item.qty;
    const tax = line * 0.1;
    const discount = line > 50 ? 5 : 0;
    total += line + tax - discount;
  }
  if (total > 1000) {
    total = total * 0.95;
  }
  return Math.round(total * 100) / 100;
}

function unusedHelper(value) {
  const doubled = value * 2;
  const labelled = "unused-" + doubled;
  return labelled;
}

module.exports = { calculateInvoiceTotal };
