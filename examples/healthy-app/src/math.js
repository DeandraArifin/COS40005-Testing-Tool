function add(left, right) {
  return left + right;
}

function formatCurrency(amount) {
  return `$${amount.toFixed(2)}`;
}

module.exports = { add, formatCurrency };
