document.addEventListener('DOMContentLoaded', () => {
    const buttons = document.getElementsByClassName('comando');
    Array.from(buttons).forEach((btn) => {
        btn.addEventListener('mousedown', () => {
            console.log('Mouse up:', btn.value);
            let velocita = document.getElementById('velocita').value;
            fetch('invia.php', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded'
                },
                body: `Comando=${btn.value}&Velocita=${velocita}`
            })
            .catch(error => {
                console.error('Errore durante il fetch (mousedown):', error);
            });
        });

        btn.addEventListener('mouseup', () => {
            console.log('Mouse up:', 0);
            fetch('invia.php', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded'
                },
                body: `Comando=0&Velocita=0` 
            })
            .catch(error => {
                console.error('Errore durante il fetch (mouseup):', error);
            });
        });
    });
    
});