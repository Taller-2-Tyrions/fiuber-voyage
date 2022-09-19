require('dotenv').config();

var PAYMENT_URI = process.env.PAYMENT_URI
var PAYMENT_HOST = process.env.PAYMENT_HOST
var PAYMENT_PORT = process.env.PAYMENT_PORT
var PAYMENT_PATH = process.env.PAYMENT_PATH
const SRV_PORT = process.env.SRV_PORT

const DATABASE_URL = process.env.PG_DATABASE_URL

const express = require("express");
const request = require("request");
const http = require("http");
const https = require("https");

const fetch = (...args) =>
  import("node-fetch").then(({ default: fetch }) => fetch(...args));
const app = express();
//app.use(cors())

const CONTENT_TYPE_JSON = {'Content-Type': 'application/json' }
const EMPTY_JSON = "{}"

const DATE_FORMAT = "YYYY-MM-DD HH:mm:ss"
const SELECT_TRAVELS_FOR_ID_USER = "SELECT * FROM public.travels WHERE user_id = $1 ORDER BY creation_date DESC"

var pgp = require("pg-promise")({
   capSQL: true
});//(/*options*/)
var db = pgp(DATABASE_URL);

app.get("/activity/:idUser/travels/:travelCount", async (req, res) =>{
  let travelCount = req.params.travelCount
  let idUser = req.params.idUser

  console.log("Retrieve activity content for user id: "+ idUser+",travelCount: ",travelCount)

  let res_data = await db.one(SELECT_TRAVELS_FOR_ID_USER, idUser)
      .then(data => {
        console.log("Travels:", data)
        return JSON.stringify(data)
      })
      .catch(function (error) {
          console.log("Error: retrieve Travels ", error)
          return EMPTY_JSON
      })
  res.set(CONTENT_TYPE_JSON)
  res.send(res_data)

})

app.get("/contents/:idUser", async (req,res) => {
  var idUser  = req.params.idUser
  console.log("Retrieve utility content for user id: "+ idUser)

  var options = {
    host: PAYMENT_HOST,
    path: PAYMENT_PATH
  };

  console.log("Request fiuber-payments uri: "+ options.host+":"+options.port+"/"+options.path)
  

  https.get(options, function(response) {
    console.log("Response status code: " + response.statusCode);

    response.on("data", function(chunk) {

      console.log("Body: " + chunk);

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
