const express = require('express');
const app = express();
const http = require('http').createServer(app);
const io = require('socket.io')(http);

app.get('/', (req, res) => {
  res.sendFile(__dirname + '/static/controller.html');
});

app.use('/', express.static('static'));

io.on('connection', socket => {
    console.log('something connected');
    // broadcast commands
    socket.on('command', cmd => socket.broadcast.binary(false).volatile.emit('command', cmd));
    socket.on('video', frame => socket.broadcast.binary(true).volatile.emit('video', frame));
    // stop on disconnect
    socket.on('disconnect', () => socket.broadcast.binary(false).volatile.emit('command', 'stop'));
});

http.listen(3000, () => {
  console.log('listening on *:3000');
});