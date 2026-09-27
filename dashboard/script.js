
let chart = null;
const countrySelect = document.getElementById('countrySelect');
const indicatorSelect = document.getElementById('indicatorSelect');

async function showCountries() {
    try {
        const response = await fetch('countries');
        if (!response.ok) throw new Error(`HTTP ${response.status}`);
        const data = await response.json();
        countrySelect.innerHTML = `<option>Choose a country ...</option>`
        data.forEach(country => {
            const option = document.createElement('option')
            option.value = country.code
            option.textContent = country.name
            countrySelect.appendChild(option)
        });
    } catch (error) {
        console.error('Erreur :', error);
        document.body.innerHTML = '<p style="color:red;">Error loading ...</p>';
    }
} showCountries();

async function loadGDP(code, indicator) {
    const response = await fetch(`/gdp/${code}?indicator=${indicator}`)
    const country = await response.json()
    const labels = country.map(row => row.year)
    const values = country.map(row => row.value)

    return {indicator, labels, values}
}

function renderChart({indicator, labels, values}) {
    const canvas = document.getElementById('gdp-chart');
    if (chart) {
        chart.destroy();
    }
    chart = new Chart(canvas, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [{
                label: indicator,
                data: values,
                borderColor: '#1B7A8C',
                backgroundColor: 'rgba(27, 122, 140, 0.1)',
                tension: 0.25,
                fill: true
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false
        }
    })
}

function refreshChart() {
    const code = countrySelect.value;
    const indic = indicatorSelect.value;
    loadGDP(code, indic).then(({indicator, labels, values}) => {
        renderChart({indicator, labels, values});
    });

}

countrySelect.addEventListener('change', refreshChart);
indicatorSelect.addEventListener('change', refreshChart);