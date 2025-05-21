<script>
    import {authStore} from '$lib/login.js';

    let user = null;
    let name = '';

    $: authStore.subscribe(auth => {
        user = auth.user;
        name = user?.name || '';
    });

</script>

{#if user}
    <h1>Добро пожаловать, {name}!</h1>
    <p><a href="/chat">Перейти в чат</a></p>
{:else}
    <h1>Перед входом в чат нужно</h1>
    <p><a href="/login">Войти</a> или <a href="/login" on:click|preventDefault={() => window.location.href = '/login'}>зарегистрироваться</a></p>
{/if}