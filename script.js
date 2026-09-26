document.addEventListener("DOMContentLoaded", () => {
    const analyzeBtn = document.getElementById("analyze-btn");
    const passwordInput = document.getElementById("password-input");
    const resultsContainer = document.getElementById("results-container");

    passwordInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') analyzeBtn.click();
    });

    analyzeBtn.addEventListener("click", async () => {
        const password = passwordInput.value;
        if (!password) return;

        analyzeBtn.textContent = "...";
        analyzeBtn.disabled = true;

        try {
            const res = await fetch("http://localhost:5001/analyze", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ password })
            });
            const data = await res.json();

            if (res.ok) {
                updateUI(data);
                resultsContainer.classList.remove("hidden");
                // Trigger a reflow for transition
                void resultsContainer.offsetWidth;
                resultsContainer.style.opacity = 1;
                resultsContainer.style.transform = 'translateY(0)';
            } else {
                alert(data.error);
            }
        } catch (err) {
            console.error(err);
            alert("Error connecting to server. Is app.py running?");
        } finally {
            analyzeBtn.textContent = "Analyze";
            analyzeBtn.disabled = false;
        }
    });

    function updateUI(data) {
        const scoreCircle = document.getElementById("score-circle");
        const scoreValue = document.getElementById("score-value");
        const strengthLabel = document.getElementById("strength-label");

        scoreValue.textContent = data.score;
        strengthLabel.textContent = data.strength_level;

        let color = "var(--border)";
        if (data.strength_level === "Weak") color = "var(--c-weak)";
        if (data.strength_level === "Moderate") color = "var(--c-mod)";
        if (data.strength_level === "Strong") color = "var(--c-strong)";
        if (data.strength_level === "Very Strong") color = "var(--c-very)";

        scoreCircle.style.borderColor = color;
        strengthLabel.style.color = color;

        document.getElementById("crack-time").textContent = formatTime(data.estimated_crack_time_seconds);
        document.getElementById("pass-length").textContent = data.password_length;
        document.getElementById("pass-combinations").textContent = formatNumber(data.total_combinations);
        document.getElementById("pass-charset").textContent = data.character_set_size;

        const vulnList = document.getElementById("vuln-list");
        vulnList.innerHTML = "";

        data.vulnerability_types.forEach(vuln => {
            const li = document.createElement("li");
            li.textContent = vuln;
            if (vuln === "No specific attack vulnerabilities detected") {
                li.className = "ok";
            }
            vulnList.appendChild(li);
        });
    }

    function formatTime(seconds) {
        if (seconds < 1) return "< 1s";
        const minutes = seconds / 60;
        if (minutes < 1) return `${Math.round(seconds)}s`;
        const hours = minutes / 60;
        if (hours < 1) return `${Math.round(minutes)}m`;
        const days = hours / 24;
        if (days < 1) return `${Math.round(hours)}h`;
        const years = days / 365.25;
        if (years < 1) return `${Math.round(days)}d`;
        if (years < 1000) return `${Math.round(years)}y`;
        return "> 1000y";
    }

    function formatNumber(num) {
        if (num >= 1e18) return (num / 1e18).toFixed(1) + 'Q+';
        if (num >= 1e15) return (num / 1e15).toFixed(1) + 'q+';
        if (num >= 1e12) return (num / 1e12).toFixed(1) + 'T+';
        if (num >= 1e9) return (num / 1e9).toFixed(1) + 'B+';
        if (num >= 1e6) return (num / 1e6).toFixed(1) + 'M+';
        return num.toLocaleString();
    }
});
