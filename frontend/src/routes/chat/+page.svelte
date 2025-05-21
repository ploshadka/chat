<script>
    import {onMount} from 'svelte';
    import {connectWS, sendWSMessage, subscribeWS} from '$lib/wsClient';
    import {getDomain} from "$lib/domain.js";
    import {authStore, logout} from "$lib/login.js";

    let user = null;
    let userId = null;
    let users = [];
    let groups = [];
    let messages = [];
    let selectedChat = null;
    let input = '';
    let currentUserName = '';
    let unsubscribe = null;

    $: authStore.subscribe((auth) => {
        user = auth.user;
    });

    onMount(async () => {
        const unsubscribe = authStore.subscribe(async (auth) => {
            if (!auth?.user) {
                window.location.href = '/';
                return;
            }

            user = auth.user;
            userId = user.id;
            currentUserName = auth.user.email;

            await loadUsersAndGroups();

            const lastChatRaw = localStorage.getItem("last_chat");
            let lastChat;
            try {
                lastChat = JSON.parse(lastChatRaw);
            } catch {
            }

            if (lastChat?.isPrivate) {
                const target = users.find(u => u.id === lastChat.targetUserId);
                if (target) {
                    await startPrivateChat(target);
                }
            } else if (lastChat?.id) {
                const found = groups.find(g => g.id === lastChat.id);
                if (found) {
                    await selectChat(found);
                } else if (groups.length > 0) {
                    await selectChat(groups[0]);
                }
            }

            unsubscribe();
        });
    });


    async function loadUsersAndGroups() {
        const [usersRes, groupsRes] = await Promise.all([
            fetch(getDomain() + 'users'),
            fetch(getDomain() + 'groups/by_user/' + userId)
        ]);

        users = (await usersRes.json()).filter((u) => u.email !== user?.email);

        groups = await groupsRes.json();
    }

    async function selectChat(chat) {
        if (unsubscribe) {
            // Отключаем предыдущего слушателя
            unsubscribe();
        }

        selectedChat = {
            ...chat,
            member_ids: chat.member_ids || []
        };

        messages = [];

        if (!chat.isPrivate) {
            localStorage.setItem("last_chat", JSON.stringify({
                id: chat.id,
                isPrivate: false
            }));
        }

        const res = await fetch(getDomain() + 'history/' + chat.id);
        messages = await res.json();

        await connectWS(chat.id, userId);


        // После загрузки истории — пометить все входящие как прочитанные
        for (const msg of messages) {
            if (
                msg.sender_id !== userId &&
                Array.isArray(msg.read_by) &&
                !msg.read_by.includes(userId)
            ) {
                sendWSMessage({
                    type: "mark_as_read",
                    message_id: msg.id
                });
            }
        }

        unsubscribe = subscribeWS(async (msg) => {
            console.log("📤 msg", msg);


            if (msg.type === "read_receipt") {
                const index = messages.findIndex((m) => m.id === msg.message_id);
                if (index !== -1) {
                    const already = messages[index].read_by || [];
                    if (!already.includes(msg.reader_id)) {
                        messages[index] = {
                            ...messages[index],
                            read_by: [...already, msg.reader_id]
                        };
                    }
                }

             } else if (!msg.type) {
    if (!messages.find((m) => m.client_id === msg.client_id)) {
        messages = [...messages, msg];

        const readBy = msg.read_by || [];

        if (msg.sender_id !== userId && !readBy.includes(userId)) {
            sendWSMessage({
                type: "mark_as_read",
                message_id: msg.id
            });
        }
    }
}
            // } else if (msg.type === "new_message") {
            //     console.log("📩 Получено новое сообщение", msg);
            //
            //     if (!messages.find((m) => m.client_id === msg.client_id)) {
            //         msg.read_by = Array.isArray(msg.read_by) ? msg.read_by : [];
            //         messages.push(msg);
            //         messages = messages;
            //
            //         if (msg.sender_id !== userId && !msg.read_by.includes(userId)) {
            //             console.log("📤 Отправка mark_as_read", msg.id);
            //
            //             await sendWSMessage({
            //                 type: "mark_as_read",
            //                 message_id: msg.id
            //             });
            //         }
            //     }
            // }


        });
    }

    function send() {
        if (input.trim()) {
            sendWSMessage({
                type: 'new_message',
                text: input,
                client_id: crypto.randomUUID()
            });
            input = '';
        }
    }

    let newGroupTitle = '';
    let selectedMembers = new Set();

    async function createGroup() {
        if (!newGroupTitle) {
            alert("Введите название группы");
            return;
        }
        if (selectedMembers.size === 0) {
            alert("Нужно выбрать хотя бы одного участника");
            return;
        }

        const payload = {
            title: newGroupTitle,
            creator_id: userId,
            member_ids: Array.from(selectedMembers)
        };
        const res = await fetch(getDomain() + 'groups', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(payload)
        });

        if (!res.ok) {
            console.error("Ошибка при создании группы");
            return;
        }

        const newGroup = await res.json();
        await loadUsersAndGroups();

        newGroupTitle = '';
        selectedMembers.clear();

        // Найдём только что созданную группу
        const justCreated = groups.find(g => g.id === newGroup.id);
        if (justCreated) {
            selectChat(justCreated);
        }
    }

    async function startPrivateChat(targetUser) {
        const sorted = [user.id, targetUser.id].sort((a, b) => a - b);

        const res = await fetch(getDomain() + 'chats/private', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                user1_id: sorted[0],
                user2_id: sorted[1]
            })
        });

        if (!res.ok) {
            console.error("Ошибка при создании/поиске приватного чата");
            return;
        }

        const chat = await res.json();

        localStorage.setItem("last_chat", JSON.stringify({
            id: chat.id,
            isPrivate: true,
            targetUserId: targetUser.id
        }));

        selectedChat = {
            id: chat.id,
            title: `Диалог с ${targetUser.name}`,
            isPrivate: true,
            member_ids: [user.id, targetUser.id]
        };

        if (unsubscribe) unsubscribe();

        connectWS(chat.id, user.id);
        const historyRes = await fetch(getDomain() + 'history/' + chat.id);
        messages = await historyRes.json();

        unsubscribe = subscribeWS((msg) => {
            messages = [...messages, msg];
        });
    }

    function getUserNameById(id) {
        if (id === user?.id) return "Вы";
        const found = users.find(u => u.id === id);
        return found ? found.name : `Пользователь ${id}`;
    }

    async function handleDeleteGroup(groupId) {
        if (!confirm("Вы уверены, что хотите удалить эту группу?")) return;

        const res = await fetch(getDomain() + `groups/${groupId}`, {
            method: "DELETE"
        });

        if (res.ok) {
            // Удалим из списка и сбросим selectedChat, если удалили текущий
            groups = groups.filter(g => g.id !== groupId);
            if (selectedChat?.id === groupId) {
                selectedChat = null;
                messages = [];
            }
        } else {
            alert("Не удалось удалить группу");
        }
    }

</script>


<main>
    <div class="sidebar">
        <div>
            <h2>Чат</h2>
            <div class="chat-select">
                <h4>Пользователи</h4>

                {#each users as u}
                    <div
                            class:selected={selectedChat?.isPrivate && selectedChat?.member_ids?.includes(u.id)}
                            style="cursor: pointer;"
                            on:click={() => startPrivateChat(u)}
                    >
                        💬 {u.name}
                    </div>
                {/each}

                <h4 style="margin-top: 2rem;">Группы</h4>

                {#each groups as g}
                    <div class:selected={selectedChat?.id === g.id} style="margin-bottom: 0.5rem;">
                        <span on:click={() => selectChat(g)} style="cursor:pointer; color:#0077cc;">
                            {g.title}
                        </span>
                        <button class="del" on:click={() => handleDeleteGroup(g.id)} style="margin-left: 0.5rem; color: crimson;">✖</button>
                    </div>
                {/each}
            </div>

            <div class="group-form">
                <h4>Создать группу</h4>
                <input placeholder="Название" bind:value={newGroupTitle}/>

                <!-- Переместить чекбоксы сюда -->
                <div style="margin-top: 0.5rem;">
                    {#each users as u}
                        <label>
                            <input type="checkbox" on:change={(e) => e.target.checked ? selectedMembers.add(u.id) : selectedMembers.delete(u.id)}/>
                            {u.name}
                        </label><br>
                    {/each}
                </div>

                <button on:click={createGroup}>Создать</button>
            </div>
        </div>


        <div>
            {#if currentUserName}
                <p style="font-size: 0.9em; color: #555;">
                    Вы: {currentUserName} | {user?.name}
                </p>
            {/if}

            <a href="/" class="link" on:click={() => logout()} style="color: crimson">
                <i class="fas fa-sign-out-alt"></i> Выйти
            </a>
        </div>
    </div>


    {#if selectedChat}
        <div class="chat">
            <div class="header">
                {selectedChat.title}
                {#if selectedChat?.member_ids}
                    <div class="chat-members">
                        Участники: {selectedChat.member_ids.map(id => getUserNameById(id)).join(', ')}
                    </div>
                {/if}
            </div>

            <div class="messages">
                {#each messages as msg}
                    <div class="message">
                        <div>
                            <strong>{getUserNameById(msg.sender_id)}</strong>
                            {#if msg.sender_id === userId}
                                <span class="status">
                                    {#if Array.isArray(msg.read_by) && selectedChat?.member_ids.every(id => msg.read_by.includes(id))}
                                        <span class="status read">✔</span>
                                    {:else}
                                        <span class="status sent">✔</span>
                                    {/if}
                                </span>
                            {/if}
                        </div>
                        <div class="time">{new Date(msg.timestamp).toLocaleTimeString()}</div>
                        <div class="text">{msg.text}</div>
                    </div>
                {/each}
            </div>
            <div class="input">
                <input type="text" bind:value={input} placeholder="Сообщение..." on:keydown={(e) => e.key === 'Enter' && send()}/>
                <button on:click={send}>Отправить</button>
            </div>
        </div>
    {:else}
        <div class="chat" style="display: flex; justify-content: center; align-items: center;">
            <p style="color: #aaa;">Выберите группу или человека слева, чтобы начать чат</p>
        </div>
    {/if}
</main>


<style>
    main {
        display: flex;
        height: 100vh;
        font-family: sans-serif;
    }

    .sidebar {
        width: 300px;
        background: #f4f4f4;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        padding: 1rem;
        border-right: 1px solid #ddd;
    }

    .chat {
        flex: 1;
        display: flex;
        flex-direction: column;
    }

    .header {
        padding: 1rem;
        border-bottom: 1px solid #ddd;
        font-weight: 500;
    }

    .messages {
        flex: 1;
        padding: 1rem;
        overflow-y: auto;
        background: #fff;
    }

    .message {
        margin-bottom: 0.5rem;
    }

    .input {
        display: flex;
        padding: 1rem;
        border-top: 1px solid #ddd;
    }

    input[type="text"] {
        flex: 1;
        padding: 0.5rem;
    }

    button {
        margin-left: 0.5rem;
        padding: 0.5rem 1rem;
    }

    .del {
        padding: 0;
        margin: 0;
        cursor: pointer;
        border: none;
    }

    .chat-select, .group-form {
        margin-bottom: 1rem;
    }

    .chat-members {
        padding: 0 1rem;
        font-size: 0.85em;
        color: #555;
        margin-bottom: 0.5rem;
    }

    .message {
        margin-bottom: 2rem;
    }

    .message strong {
        display: block;
        margin-bottom: 0;
        font-weight: 600;
    }

    .message .time {
        font-size: 0.85em;
        color: #888;
        margin-bottom: 0.2rem;
    }

    .message .text {
        line-height: 1.2;
    }

    .chat-select h4:nth-of-type(2) {
        border-top: 1px solid #ccc;
        padding: 2rem 0 0;
    }

    .group-form button {
        background-color: #0077cc;
        color: white;
        border: none;
        border-radius: 4px;
        margin-top: 0.8rem;
        padding: 0.5rem 1.2rem;
        cursor: pointer;
    }

    .group-form button:hover {
        background-color: #005fa3;
    }

    .selected {
        background-color: #ddeeff;
        padding: 0.2rem;
        border-radius: 4px;
    }

    .status {
        font-size: 0.85em;
        margin-left: 0.5rem;
    }

    .sent {
        color: #888;
    }

    .read {
        color: #0077cc;
    }
</style>