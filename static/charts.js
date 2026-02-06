document.addEventListener("DOMContentLoaded", () => {
    const canvas = document.getElementById("evidenceChart");
    if (!canvas) return;

    // Backend se status counts HTML data-attributes se uthayenge
    const data = JSON.parse(canvas.dataset.stats);

    new Chart(canvas, {
        type: "bar",
        data: {
            labels: ["Valid", "Tampered", "Minor Change", "Duplicate"],
            datasets: [{
                label: "Evidence Status Overview",
                data: [
                    data.VALID || 0,
                    data.TAMPERED || 0,
                    data.MINOR_CHANGE || 0,
                    data.DUPLICATE || 0
                ],
                backgroundColor: [
                    "#3fbf9b",
                    "#e57373",
                    "#f5c16c",
                    "#64b5f6"
                ],
                borderRadius: 6
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: { display: false },
                tooltip: {
                    backgroundColor: "#1c2f36",
                    titleColor: "#ffffff",
                    bodyColor: "#dfeff0"
                }
            },
            scales: {
                x: {
                    grid: { display: false },
                    ticks: { color: "#cfe6e6" }
                },
                y: {
                    grid: { color: "rgba(255,255,255,0.05)" },
                    ticks: { color: "#cfe6e6", stepSize: 1 }
                }
            }
        }
    });
});