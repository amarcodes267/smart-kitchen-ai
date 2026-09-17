function createDemandChart(canvasId, labels, datasets) {
    const ctx = document.getElementById(canvasId);
    if (!ctx) return null;
    return new Chart(ctx, {
        type: "line",
        data: { labels, datasets },
        options: {
            responsive: true,
            plugins: {
                legend: { display: datasets.length > 1 },
            },
            scales: {
                y: { beginAtZero: true },
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
                    backgroundColor: ["#2563EB", "#78350F", "#111827", "#3B82F6", "#92400E"],
                },
            ],
        },
        options: {
            responsive: true,
            plugins: {
                legend: { position: "bottom" },
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
                    backgroundColor: "#2563EB",
                },
            ],
        },
        options: {
            responsive: true,
            plugins: {
                legend: { display: false },
            },
            scales: {
                y: { beginAtZero: true },
            },
        },
    });
}

function createHealthGauge(canvasId, score) {
    const ctx = document.getElementById(canvasId);
    if (!ctx) return null;
    return new Chart(ctx, {
        type: "doughnut",
        data: {
            labels: ["Score", "Remaining"],
            datasets: [
                {
                    data: [score, 100 - score],
                    backgroundColor: ["#2563EB", "#E5E7EB"],
                    borderWidth: 0,
                },
            ],
        },
        options: {
            responsive: true,
            cutout: "80%",
            plugins: {
                legend: { display: false },
                tooltip: { enabled: false },
            },
        },
    });
}
