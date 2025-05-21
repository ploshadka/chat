import {authStore, logout, refreshToken} from "./login.js";
import {getDomain} from "./domain.js";


// Получаем заголовки с access_token
function getAuthHeaders() {
    let token;
    authStore.subscribe(auth => {
        token = auth.token;
    })();
    return token ? {"Authorization": `Bearer ${token}`} : {};
}

// Универсальный обработчик 401 с auto-refresh
async function withAuthRetry(fetchFn) {
    let response = await fetchFn();

    if (response.status === 401) {
        console.warn("🔁 Попытка обновления токена...");
        const refreshed = await refreshToken();
        if (!refreshed) {
            await logout();
            throw new Error("Unauthorized");
        }

        response = await fetchFn();
    }

    return response;
}

export async function getFetch(url) {
    let headers = {...getAuthHeaders()};
    const response = await withAuthRetry(() =>
        fetch(getDomain() + url, {headers})
    );
    return response.json();
}


export async function postFetch(url, data, options = {}) {
    let headers = {"Content-Type": "application/json", ...getAuthHeaders()};
    if (options.headers) headers = {...headers, ...options.headers};

    const response = await withAuthRetry(() =>
        fetch(getDomain() + url, {
            method: "POST",
            headers,
            body: JSON.stringify(data)
        })
    );

    return response.json();
}