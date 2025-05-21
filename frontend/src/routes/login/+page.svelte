<script>
    import {setAuth} from "$lib/login.js";
    import {postFetch} from "$lib/crud.js";
    import {getDomain} from "$lib/domain.js";

    let email = "";
    let name = "";
    let password = "";
    let error = "";
    let successMessage = "";
    let isRegistering = false;

    async function login() {
        error = "";
        try {
            const data = new URLSearchParams();
            data.append("username", email);
            data.append("password", password);
            data.append("name", name);

            const response = await fetch(getDomain() + "token", {
                method: "POST",
                body: data,
                headers: {"Content-Type": "application/x-www-form-urlencoded"}
            });

            if (!response.ok) {
                password = "";
                name = "";

                throw new Error("Ошибка авторизации");
            }

            const result = await response.json();
            setAuth(result.access_token, {name});

            window.location.href = "/chat";

        } catch (err) {
            error = err.message;
        }
    }

    async function register() {
        error = "";
        successMessage = "";


        try {
            const result = await postFetch("register", {email, password, name});

            if (!result || result.detail) {
                throw new Error(result?.detail || "Ошибка регистрации");
            }

            email = "";
            password = "";
            name = "";
            successMessage = "Регистрация успешна! Теперь войдите в систему.";
            isRegistering = false;

        } catch (err) {
            error = err.message;
        }
    }

    function handleSubmit(event) {
        event.preventDefault();
        if (isRegistering) {
            register();
        } else {
            login();
        }
    }

    function switchToRegister(event) {
        event.preventDefault();
        isRegistering = true;
        error = "";
        successMessage = "";

        email = "";
        password = "";
    }

    function switchToLogin(event) {
        event.preventDefault();
        isRegistering = false;
        error = "";
        successMessage = "";

        email = "";
        password = "";
    }
</script>

<form class="login-container" on:submit={handleSubmit}>
    <h2>{isRegistering ? "Регистрация" : "Вход"}</h2>

    {#if isRegistering}
        <button type="button" on:click={switchToLogin}>Уже есть аккаунт? Войти</button>
    {:else}
        <button type="button" on:click={switchToRegister}>Нет аккаунта? Зарегистрироваться</button>
    {/if}

    {#if isRegistering}
        <input type="name" placeholder="Имя" bind:value={name}/>
    {/if}

    <input type="email" placeholder="Email" bind:value={email} required autocomplete="email"/>
    <input type="password" placeholder="Пароль" bind:value={password} required autocomplete={isRegistering ? "new-password" : "current-password"}/>

    {#if successMessage}
        <p class="success">{successMessage}</p>
    {/if}

    {#if error}
        <p class="error">{error}</p>
    {/if}


    <button type="submit">{isRegistering ? "Зарегистрироваться" : "Войти"}</button>

</form>

<style>
    .login-container {
        max-width: 300px;
        margin: auto;
        text-align: center;
    }

    .error {
        color: red;
    }

    .success {
        color: green;
    }

    input {
        display: block;
        width: 100%;
        margin: 10px 0;
        padding: 8px;
    }

    button {
        margin: 10px 0;
        width: 100%;
        padding: 10px;
        background: blue;
        color: white;
        border: none;
        cursor: pointer;
    }

</style>