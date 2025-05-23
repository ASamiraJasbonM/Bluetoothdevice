if ('serviceWorker' in navigator) {
    navigator.serviceWorker.register('/static/js/serviceworker.js')
    .then(function(reg) {
        console.log('✔️ Service Worker registrado', reg);

        // Solicita permiso para notificaciones push
        Notification.requestPermission().then(function(permission) {
        if (permission === 'granted') {
            console.log('🔔 Permiso de notificaciones concedido');
        } else {
            console.log('❌ Permiso de notificaciones denegado');
        }
        });
    })
    .catch(function(error) {
        console.error('❌ Error al registrar el Service Worker:', error);
    });
}