const app = require('express')();
const http = require('http').createServer(app);
const io = require('socket.io')(http);

app.get('/', (req, res) => {
    res.sendFile(__dirname + '/controller.html');
});

io.on('connection', socket => {
    console.log('something connected');
    // broadcast commands
    socket.on('command', cmd => io.emit('command', cmd));
    // stop on disconnect
    socket.on('disconnect', () => io.emit('command', 'stop'));
});

http.listen(3000, () => {
  console.log('listening on *:3000');
});