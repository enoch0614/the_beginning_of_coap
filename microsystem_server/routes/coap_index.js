var coap = require('coap');
var router = require('../lib/coap-router');
var mysql = require('mysql');

var route = new router();

var config = require('../config/db-config.json');

route.post('/devices/{device_id}', function(req, res) {
    console.log('----------------------------------------');
    console.log('add sensor datapoint to database');

    var device_id = req.params.device_id;
    console.log('device id: %s', device_id);

    var payload = JSON.parse(req.payload);
    var temp = payload.temp;
    var hum = payload.hum;
    var light = payload.light;
    console.log('temp %.1f, hum %.1f, light %.1f', temp, hum, light);

    var conn = mysql.createConnection(config);
    conn.connect();

    conn.query('INSERT INTO sensor_history SET device_id=?, temp=?, hum=?, light=?, time=NOW()',
        [device_id, temp, hum, light],
        function(err, rows) {
            if (err) {
                console.log("client error: " + err.message);
                res.code = 4.00;
                res.end();
            } else {
                res.code = '2.01';
                res.end();
            }
    });

    conn.end(function(err) {
        console.log('db close');
    });
});

// 测试目的路由，没有具体含义
route.get('/test-db', function(req, res) {
    var conn = mysql.createConnection(config);
    conn.connect();

    conn.query('SELECT 1+2 AS result',
        function(err, rows) {
            var result = rows[0].result;
            res.code = '2.05';
            res.setOption('Content-Format', 'application/json');
            res.end(JSON.stringify({result: result}));
    });

    conn.end();
});

// 测试目的路由，没有具体含义
route.get('/test', function(req, res) {
    res.code = '2.05';
    res.end(new Date().toLocaleString())
});


module.exports = route;