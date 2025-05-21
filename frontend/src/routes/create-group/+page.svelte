<script>
    import {onMount} from 'svelte';
    import {createGroup} from '$lib/wsClient';
    import {getDomain} from '$lib/domain.js';

    let title = '';
    let selectedUserIds = [];
    let users = [];
    let message = '';
    let currentUser = null;

    authStore.subscribe((auth) => {
        currentUser = auth.user; // ← сохраняем текущего пользователя
    });

    onMount(async () => {
        const res = await fetch(getDomain() + 'users');
        users = await res.json();
    });

    async function handleCreate() {
        if (!title || selectedUserIds.length === 0) {
            message = 'Введите название и выберите участников';
            return;
        }

        try {
            await createGroup({
                title,
                member_ids: selectedUserIds,
                creator_id: currentUser.id
            });
            message = 'Группа успешно создана!';
            title = '';
            selectedUserIds = [];
        } catch (err) {
            message = err.message;
        }
    }
</script>

<h1>Создание группы</h1>

<input bind:value={title} placeholder="Название группы"/>

<h3>Участники:</h3>
{#each users as user}
    <label>
        <input type="checkbox" bind:group={selectedUserIds} value={user.id}/>
        {user.name}
    </label><br>
{/each}

<br>
<button on:click={handleCreate}>Создать группу</button>

<p>{message}</p>