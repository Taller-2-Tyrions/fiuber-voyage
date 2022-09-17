require('dotenv').config();

var PAYMENT_URI = process.env.PAYMENT_URI
var PAYMENT_HOST = process.env.PAYMENT_HOST
var PAYMENT_PORT = process.env.PAYMENT_PORT
var PAYMENT_PATH = process.env.PAYMENT_PATH
const PAYMENT_PROTOCOL = process.env.PAYMENT_PROTOCOL
const SRV_PORT = process.env.SRV_PORT

const express = require("express");
const request = require("request");
const http = require("http");
//var cors = require('cors')

const fetch = (...args) =>
  import("node-fetch").then(({ default: fetch }) => fetch(...args));
const app = express();
//app.use(cors())

const CONTENT_TYPE_JSON = {'Content-Type': 'application/json' }
const EMPTY_JSON = "{}"

app.get("/contents/:idUser", async (req,res) => {
  var idUser  = req.params.idUser
  console.log("Retrieve utility content for user id: "+ idUser)

  var options = {
    protocol: PAYMENT_PROTOCOL,
    host: PAYMENT_HOST,
    port: PAYMENT_PORT,
    path: PAYMENT_PATH+'/3'
  };

  console.log("Request fiuber-payments uri: "+ options.host+":"+options.port+"/"+options.path)
  

  http.get(options, function(response) {
    console.log("Response status code: " + response.statusCode);

    response.on("data", function(chunk) {

      console.log("Body: " + chunk);
      //let utilityContent = {score: 5}
      res.set(CONTENT_TYPE_JSON)
      res.send(chunk)
      
    });
  }).on('error', function(e) {
    console.log("Error: " + e.message);
  });
})

app.get("/", (req, res) => {
  res.status(200).send("200 OK");
});

app.listen(process.env.PORT || SRV_PORT, () => {
  console.log("Escuchando en puerto =>", SRV_PORT);
});
