let socket;
let listeners = [];

export function connectWS(chatId, userId) {
    // Закрываем старое соединение, если оно было
    if (socket) {
        socket.close();
    }

    // Очищаем старых слушателей — важно!
    listeners = [];

    socket = new WebSocket(`ws://localhost:8000/ws/chat/${chatId}/${userId}`);

    socket.onopen = () => {
        console.log("WebSocket connected");
    };

    socket.onclose = () => {
        console.log("WebSocket disconnected");
    };

    socket.onmessage = (event) => {
        const data = JSON.parse(event.data);
        for (const cb of listeners) cb(data);
    };
}

export function sendWSMessage(payload) {
    if (socket && socket.readyState === WebSocket.OPEN) {
        socket.send(JSON.stringify(payload));
    }
}

export function subscribeWS(callback) {
    listeners.push(callback);
    return () => {
        listeners = listeners.filter((cb) => cb !== callback);
    };
}

export async function createGroup(data) {
    console.log(data);

    const res = await fetch('http://localhost:8000/groups', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify(data)
    });

    if (!res.ok) {
        const err = await res.json();
        throw new Error(err.detail || 'Ошибка при создании группы');
    }

    return res.json();
}
