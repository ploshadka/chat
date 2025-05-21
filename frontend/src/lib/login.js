import {writable} from "svelte/store";
import {getDomain} from "./domain.js";

const isBrowser = typeof window !== 'undefined' && typeof localStorage !== 'undefined';

const storedToken = isBrowser ? localStorage.getItem("access_token") : null;
const storedUser = isBrowser && localStorage.getItem("user")
    ? JSON.parse(localStorage.getItem("user"))
    : null;

export const authStore = writable({
    token: storedToken,
    user: storedUser
});


export function setAuth(token, userData = {}) {
    try {
        const payload = JSON.parse(atob(token.split(".")[1]));

        const user = {
            id: payload.id,
            email: payload.sub,
            role: payload.role || "user",
            name: payload.name || userData?.name || "Пользователь"
        };

        if (isBrowser) {
            localStorage.setItem("access_token", token);
            localStorage.setItem("user", JSON.stringify(user));
        }

        authStore.set({token, user});

    } catch (e) {
        console.error("Ошибка при установке авторизации:", e);
        authStore.set({token: null, user: null});
    }
}

export async function refreshToken() {
    try {
        let response = await fetch(getDomain() + "refresh", {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            credentials: "include"  // Обязательно, чтобы куки отправлялись
        });

        if (!response.ok) {
            return false;  // Не удалось обновить токен
        }

        let data = await response.json();
        // setAuth(data.access_token, {email: data.email});
        setAuth(data.access_token);

        console.log("Токен обновлен");
        return true;
    } catch (err) {
        console.error("Ошибка при обновлении токена:", err);
        return false;
    }
}

export async function logout() {
    try {
        await fetch(getDomain() + "logout", {
            method: "POST",
            credentials: "include"  // 👈 Передаем куки для удаления refresh-токена
        });
    } catch (err) {
        console.error("Ошибка при выходе:", err);
    }

    // Очищаем локальное хранилище
    localStorage.removeItem("access_token");
    localStorage.removeItem("user");

    // Очищаем Svelte store
    authStore.set({token: null, user: null});

    // Перенаправляем на страницу логина
    window.location.href = "";
}