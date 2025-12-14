// API config for local testing
// const API_BASE = 'http://127.0.0.1:5000/api';
// const API_KEY  = 'raven-secret';

const API_BASE = 'https://e-commerce-sales-dashboard-backend.onrender.com/api';
const API_KEY  = 'raven-secret';


// store data in memory for selectors and forecasts
let currentMonthly = [];
let currentForecastMonthly = [];
let currentForecastTotals = {
  next_3_months: 0,
  next_6_months: 0,
  next_12_months: 0
};
let lastResultData = null;

// Load product list and theme when page opens
document.addEventListener('DOMContentLoaded', () => {
  initTheme();
  loadProductList();
});

// THEME
function initTheme() {
  const saved = localStorage.getItem('raven-theme');
  const body = document.body;
  const btn = document.getElementById('themeToggle');

  const theme = saved === 'light' ? 'theme-light' : 'theme-dark';
  body.classList.add(theme);
  if (btn) {
    btn.textContent = theme === 'theme-dark' ? '🌙 Dark' : '☀️ Light';
  }
}

function toggleTheme() {
  const body = document.body;
  const btn = document.getElementById('themeToggle');
  const isDark = body.classList.contains('theme-dark');

  body.classList.toggle('theme-dark', !isDark);
  body.classList.toggle('theme-light', isDark);
  localStorage.setItem('raven-theme', isDark ? 'light' : 'dark');

  if (btn) {
    btn.textContent = isDark ? '☀️ Light' : '🌙 Dark';
  }
}

// LOAD PRODUCT LIST
async function loadProductList() {
  const select = document.getElementById('productSelect');
  if (!select) return;

  try {
    const res = await fetch(API_BASE + '/products', {
      method: 'GET',
      headers: {
        'X-API-KEY': API_KEY
      }
    });
    if (!res.ok) {
      console.error('Failed to load products:', res.status);
      return;
    }
    const data = await res.json();
    const products = data.products || [];

    select.innerHTML = '<option value="">Select a product...</option>';
    products.forEach(name => {
      const opt = document.createElement('option');
      opt.value = name;
      opt.textContent = name;
      select.appendChild(opt);
    });
  } catch (err) {
    console.error('Error loading product list:', err);
  }
}

// MAIN SEARCH FUNCTION
async function searchSelectedProduct() {
  const select = document.getElementById('productSelect');
  const name = select.value;
  const loading = document.getElementById('loading');
  const results = document.getElementById('results');

  if (!name) {
    alert('Please select a product from the list.');
    return;
  }

  loading.classList.remove('hidden');
  results.classList.add('hidden');

  try {
    const response = await fetch(API_BASE + '/product-sales', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-API-KEY': API_KEY
      },
      body: JSON.stringify({ product_name: name })
    });

    if (!response.ok) {
      const text = await response.text();
      console.error('API error:', response.status, text);
      alert('API error: ' + response.status);
      loading.classList.add('hidden');
      return;
    }

    const data = await response.json();
    displayResults(data);
    loading.classList.add('hidden');
    results.classList.remove('hidden');
  } catch (err) {
    console.error('Fetch error:', err);
    alert('Error: ' + err.message);
    loading.classList.add('hidden');
  }
}

// TOGGLE SECTIONS WHEN METRIC CARDS ARE CLICKED
function toggleSection(sectionId) {
  const section = document.getElementById(sectionId);
  if (!section) return;

  document.querySelectorAll('.detail-section').forEach(sec => {
    if (sec.id === sectionId) {
      const willShow = sec.classList.contains('hidden');
      sec.classList.toggle('hidden');

      // Only when forecast section becomes visible, show 3/6/12 months totals
      if (sectionId === 'section-forecast' && willShow) {
        const t3  = Math.round(currentForecastTotals.next_3_months);
        const t6  = Math.round(currentForecastTotals.next_6_months);
        const t12 = Math.round(currentForecastTotals.next_12_months);

        document.getElementById('forecastSummary').textContent = t6.toString();

        const box = document.getElementById('forecastTotalDisplay');
        box.innerHTML = `
          <div>Next 3 months: <strong>${t3}</strong> units</div>
          <div>Next 6 months: <strong>${t6}</strong> units</div>
          <div>Next 12 months: <strong>${t12}</strong> units</div>
        `;
      }
    } else {
      sec.classList.add('hidden');
    }
  });
}

// AFTER SEARCH: PREPARE DATA & DROPDOWNS
function displayResults(data) {
  const monthly = data.monthly;
  const yearlyTotal = data.yearly_total;
  const forecastMonthly = data.forecast_monthly;
  const forecastTotals = data.forecast_totals;

  currentMonthly = monthly;
  currentForecastMonthly = forecastMonthly;
  currentForecastTotals = forecastTotals;
  lastResultData = data;

  document.getElementById('monthSummary').textContent = '-';
  document.getElementById('yearSummary').textContent = '-';
  document.getElementById('forecastSummary').textContent = '-';
  document.getElementById('forecastTotalDisplay').innerHTML = '-';

  fillMonthOptions(monthly);
  fillYearOptions(monthly);

  clearTablesAndForecastDisplay();

  document.querySelectorAll('.detail-section').forEach(sec => sec.classList.add('hidden'));

  window._storedYearlyTotal = yearlyTotal;
}

// BUILD MONTH SELECT OPTIONS
function fillMonthOptions(monthly) {
  const monthSelect = document.getElementById('monthSelect');
  const seen = new Set();

  monthSelect.innerHTML = '<option value="">Select month</option>';

  monthly.forEach(m => {
    const label = m.date;
    if (!seen.has(label)) {
      seen.add(label);
      const opt = document.createElement('option');
      opt.value = label;
      opt.textContent = label;
      monthSelect.appendChild(opt);
    }
  });
}

// BUILD YEAR SELECT OPTIONS
function fillYearOptions(monthly) {
  const yearSelect = document.getElementById('yearSelect');
  const seenYears = new Set();

  yearSelect.innerHTML = '<option value="">Select year</option>';

  monthly.forEach(m => {
    const year = m.date.split('-')[0];
    if (!seenYears.has(year)) {
      seenYears.add(year);
      const opt = document.createElement('option');
      opt.value = year;
      opt.textContent = year;
      yearSelect.appendChild(opt);
    }
  });
}

// CLEAR TABLES + FORECAST DISPLAY
function clearTablesAndForecastDisplay() {
  document.getElementById('monthTableBody').innerHTML = '';
  document.getElementById('yearTableBody').innerHTML = '';
  document.getElementById('forecastTotalDisplay').innerHTML = '-';
}

// WHEN MONTH IS CHOSEN → SHOW ONLY THAT MONTH & UPDATE CARD
function showSelectedMonth() {
  const select = document.getElementById('monthSelect');
  const value = select.value;
  const tbody = document.getElementById('monthTableBody');
  tbody.innerHTML = '';

  if (!value) {
    document.getElementById('monthSummary').textContent = '-';
    return;
  }

  const m = currentMonthly.find(row => row.date === value);
  if (!m) {
    document.getElementById('monthSummary').textContent = '-';
    return;
  }

  tbody.innerHTML = `
    <tr>
      <td>${m.date}</td>
      <td>${m.sold}</td>
    </tr>
  `;

  document.getElementById('monthSummary').textContent = m.sold.toString();
}

// WHEN YEAR IS CHOSEN → SHOW MONTHS FOR THAT YEAR & UPDATE CARD
function showSelectedYear() {
  const select = document.getElementById('yearSelect');
  const year = select.value;
  const tbody = document.getElementById('yearTableBody');
  tbody.innerHTML = '';

  if (!year) {
    document.getElementById('yearSummary').textContent = '-';
    return;
  }

  const rows = currentMonthly.filter(m => m.date.startsWith(year + '-'));
  if (!rows.length) {
    document.getElementById('yearSummary').textContent = '-';
    return;
  }

  tbody.innerHTML = rows
    .map(m => `<tr><td>${m.date}</td><td>${m.sold}</td></tr>`)
    .join('');

  const yearTotal = rows.reduce((sum, m) => sum + m.sold, 0);
  document.getElementById('yearSummary').textContent = yearTotal.toString();
}

// DOWNLOAD CURRENT DATA AS CSV
function downloadCurrentDataAsCsv() {
  if (!lastResultData) {
    alert('Search a product first to download its data.');
    return;
  }

  const rows = [];
  rows.push(['date', 'sold']);

  (lastResultData.monthly || []).forEach(m => {
    rows.push([m.date, m.sold]);
  });

  const csvLines = rows.map(r =>
    r.map(value => `"${String(value).replace(/"/g, '""')}"`).join(',')
  );
  const csvContent = csvLines.join('\n');

  const blob = new Blob([csvContent], { type: 'text/csv' });
  const url = window.URL.createObjectURL(blob);
  const a = document.createElement('a');
  const productName = (lastResultData.product && lastResultData.product.name) || 'product';
  a.href = url;
  a.download = `${productName}_sales.csv`;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  window.URL.revokeObjectURL(url);
}
