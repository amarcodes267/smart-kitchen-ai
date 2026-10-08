// charts.js - Modernized Chart.js configurations with Light SaaS styling

function createDemandChart(canvasId, labels, datasets) {
    const ctx = document.getElementById(canvasId);
    if (!ctx) return null;

    // Apply modern Light SaaS botanical/amber palette to datasets
    const modernColors = ['#059669', '#f59e0b', '#0d9488', '#8b5cf6', '#e11d48'];
    const styledDatasets = datasets.map((ds, idx) => {
        const color = modernColors[idx % modernColors.length];
        return {
            borderColor: color,
            backgroundColor: ds.backgroundColor || `${color}18`,
            borderWidth: ds.borderWidth || 2.5,
            tension: 0.35,
            pointBackgroundColor: color,
            pointBorderColor: '#ffffff',
            pointBorderWidth: 2,
            pointRadius: 4,
            pointHoverRadius: 6,
            ...ds
        };
    });

    return new Chart(ctx, {
        type: "line",
        data: { labels, datasets: styledDatasets },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: datasets.length > 1,
                    labels: { color: '#64748b', font: { family: 'Plus Jakarta Sans', size: 12 } }
                },
                tooltip: {
                    backgroundColor: '#0f172a',
                    titleColor: '#ffffff',
                    bodyColor: '#f1f5f9',
                    borderColor: '#334155',
                    borderWidth: 1,
                    padding: 10,
                    cornerRadius: 8
                }
            },
            scales: {
                x: {
                    grid: { color: 'rgba(0, 0, 0, 0.05)' },
                    ticks: { color: '#64748b', font: { family: 'Plus Jakarta Sans', size: 11 } }
                },
                y: {
                    beginAtZero: true,
                    grid: { color: 'rgba(0, 0, 0, 0.05)' },
                    ticks: { color: '#64748b', font: { family: 'Plus Jakarta Sans', size: 11 } }
                },
            },
        },
    });
}

function createWasteChart(canvasId, labels, data) {
    const ctx = document.getElementById(canvasId);
    if (!ctx) return null;
    return new Chart(ctx, {
        type: "doughnut",
        data: {
            labels,
            datasets: [
                {
                    data,
                    backgroundColor: [
                        "#059669",
                        "#f59e0b",
                        "#0d9488",
                        "#8b5cf6",
                        "#e11d48"
                    ],
                    borderColor: "#ffffff",
                    borderWidth: 2,
                },
            ],
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: "bottom",
                    labels: {
                        color: '#64748b',
                        font: { family: 'Plus Jakarta Sans', size: 12 },
                        padding: 14,
                        usePointStyle: true
                    }
                },
                tooltip: {
                    backgroundColor: '#0f172a',
                    titleColor: '#ffffff',
                    bodyColor: '#f1f5f9',
                    borderColor: '#334155',
                    borderWidth: 1,
                    padding: 10,
                    cornerRadius: 8
                }
            },
        },
    });
}

function createSalesChart(canvasId, labels, data) {
    const ctx = document.getElementById(canvasId);
    if (!ctx) return null;
    return new Chart(ctx, {
        type: "bar",
        data: {
            labels,
            datasets: [
                {
                    label: "Orders",
                    data,
                    backgroundColor: "rgba(5, 150, 105, 0.85)",
                    hoverBackgroundColor: "#059669",
                    borderRadius: 6,
                    borderSkipped: false
                },
            ],
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false },
                tooltip: {
                    backgroundColor: '#0f172a',
                    titleColor: '#ffffff',
                    bodyColor: '#f1f5f9',
                    borderColor: '#334155',
                    borderWidth: 1,
                    padding: 10,
                    cornerRadius: 8
                }
            },
            scales: {
                x: {
                    grid: { display: false },
                    ticks: { color: '#64748b', font: { family: 'Plus Jakarta Sans', size: 11 } }
                },
                y: {
                    beginAtZero: true,
                    grid: { color: 'rgba(0, 0, 0, 0.05)' },
                    ticks: { color: '#64748b', font: { family: 'Plus Jakarta Sans', size: 11 } }
                },
            },
        },
    });
}

function createHealthGauge(canvasId, score) {
    const ctx = document.getElementById(canvasId);
    if (!ctx) return null;
    const gaugeColor = score >= 70 ? "#059669" : score >= 50 ? "#f59e0b" : "#e11d48";
    return new Chart(ctx, {
        type: "doughnut",
        data: {
            labels: ["Score", "Remaining"],
            datasets: [
                {
                    data: [score, 100 - score],
                    backgroundColor: [gaugeColor, "#f1f5f9"],
                    borderWidth: 0,
                },
            ],
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            cutout: "80%",
            plugins: {
                legend: { display: false },
                tooltip: { enabled: false },
            },
        },
    });
}
