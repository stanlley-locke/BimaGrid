async function postJson(path, payload) {
	const response = await fetch(path, {
		method: "POST",
		headers: {
			"Content-Type": "application/json",
			"X-CSRFToken": getCookie("csrftoken"),
		},
		credentials: "same-origin",
		body: JSON.stringify(payload),
	});
	const text = await response.text();
	try {
		return { status: response.status, body: JSON.parse(text) };
	} catch {
		return { status: response.status, body: text };
	}
}

function getCookie(name) {
	const match = document.cookie.match(new RegExp(`(?:^|; )${name}=([^;]*)`));
	return match ? decodeURIComponent(match[1]) : "";
}

function bindForm(formId, resultId, path, mapPayload) {
	const form = document.getElementById(formId);
	const result = document.getElementById(resultId);
	form.addEventListener("submit", async (event) => {
		event.preventDefault();
		result.textContent = "Loading...";
		const data = new FormData(form);
		const payload = mapPayload(data);
		const { status, body } = await postJson(path, payload);
		result.textContent = JSON.stringify({ status, body }, null, 2);
	});
}

bindForm("simulate-form", "simulate-result", "/api/admin/simulate-drought/", (data) => ({
	h3_index: data.get("h3_index"),
	rainfall_mm: parseFloat(data.get("rainfall_mm") || "15"),
	ndvi: parseFloat(data.get("ndvi") || "0.35"),
}));

bindForm("evaluate-form", "evaluate-result", "/api/admin/trigger-evaluation/", (data) => ({
	h3_index: data.get("h3_index"),
	simulate_drought: data.get("simulate_drought") === "on",
}));

bindForm("bypass-form", "bypass-result", "/api/admin/bypass-payment/", (data) => ({
	policy_id: data.get("policy_id"),
}));
