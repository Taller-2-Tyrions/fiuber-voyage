// Import the functions you need from the SDKs you need
import { initializeApp } from "firebase/app";

/* Dont use now  */
//import { getAnalytics } from "firebase/analytics";


// TODO: Add SDKs for Firebase products that you want to use
// https://firebase.google.com/docs/web/setup#available-libraries

// Your web app's Firebase configuration
// For Firebase JS SDK v7.20.0 and later, measurementId is optional
const firebaseConfig = {
  apiKey: "AIzaSyD91WTkhydpLbHkBqTUvvnXXcybpjF7uL8",
  authDomain: "fiuber-363101.firebaseapp.com",
  projectId: "fiuber-363101",
  storageBucket: "fiuber-363101.appspot.com",
  messagingSenderId: "241358240016",
  appId: "1:241358240016:web:877f17f6fbe238f54f8d95",
  measurementId: "G-BKBJ28KEVW"
};

// Initialize Firebase
const app2 = initializeApp(firebaseConfig);
//const analytics = getAnalytics(app);

import { getStorage, ref, uploadString } from "firebase/storage";

//require('dotenv').config();
import * as dotenv from 'dotenv' // see https://github.com/motdotla/dotenv#how-do-i-use-dotenv-with-import
dotenv.config()

var PAYMENT_URI = process.env.PAYMENT_URI
var PAYMENT_HOST = process.env.PAYMENT_HOST
var PAYMENT_PORT = process.env.PAYMENT_PORT
var PAYMENT_PATH = process.env.PAYMENT_PATH
const SRV_PORT = process.env.SRV_PORT

const DATABASE_URL = process.env.PG_DATABASE_URL

//const express = require("express");
import express from 'express'
//const request = require("request");
import request from 'request'
//const http = require("http");
import http from 'http'
//const https = require("https");
import https from 'https'

const fetch = (...args) =>
  import("node-fetch").then(({ default: fetch }) => fetch(...args));
const app = express();

//app.use(cors())

const CONTENT_TYPE_JSON = {'Content-Type': 'application/json' }
const EMPTY_JSON = "{}"

const DATE_FORMAT = "YYYY-MM-DD HH:mm:ss"
const SELECT_TRAVELS_FOR_ID_USER = "SELECT * FROM public.travels WHERE user_id = $1 ORDER BY creation_date DESC"

import pgPromise from 'pg-promise';
const pgp = pgPromise({});
var db = pgp(DATABASE_URL);
console.log(pgp);

// var pgp = require("pg-promise")({
//    capSQL: true
// });//(/*options*/)
// import * as pgPromise from 'pg-promise';
// const pgp = pgPromise({});

//var db = pgp(DATABASE_URL);
app.post("/users/photo/:idUser", async (req, res) => {
  let idUser = req.params.idUser

  // Create a root reference
  const storage = getStorage()
  const storageRef = ref(storage, 'tyrion_'+idUser.toString())

  // Base64 formatted string = tyrion img
  const imgBase64 = '/9j/4AAQSkZJRgABAQAAAQABAAD/4QBqRXhpZgAASUkqAAgAAAADABIBAwABAAAAAQAAADEBAgARAAAAMgAAAGmHBAABAAAARAAAAAAAAABTaG90d2VsbCAwLjMwLjE0AAACAAKgCQABAAAAawAAAAOgCQABAAAAawAAAAAAAAD/4Qn0aHR0cDovL25zLmFkb2JlLmNvbS94YXAvMS4wLwA8P3hwYWNrZXQgYmVnaW49Iu+7vyIgaWQ9Ilc1TTBNcENlaGlIenJlU3pOVGN6a2M5ZCI/PiA8eDp4bXBtZXRhIHhtbG5zOng9ImFkb2JlOm5zOm1ldGEvIiB4OnhtcHRrPSJYTVAgQ29yZSA0LjQuMC1FeGl2MiI+IDxyZGY6UkRGIHhtbG5zOnJkZj0iaHR0cDovL3d3dy53My5vcmcvMTk5OS8wMi8yMi1yZGYtc3ludGF4LW5zIyI+IDxyZGY6RGVzY3JpcHRpb24gcmRmOmFib3V0PSIiIHhtbG5zOmV4aWY9Imh0dHA6Ly9ucy5hZG9iZS5jb20vZXhpZi8xLjAvIiB4bWxuczp0aWZmPSJodHRwOi8vbnMuYWRvYmUuY29tL3RpZmYvMS4wLyIgZXhpZjpQaXhlbFhEaW1lbnNpb249IjEwNyIgZXhpZjpQaXhlbFlEaW1lbnNpb249IjEwNyIgdGlmZjpJbWFnZVdpZHRoPSIxMDciIHRpZmY6SW1hZ2VIZWlnaHQ9IjEwNyIgdGlmZjpPcmllbnRhdGlvbj0iMSIvPiA8L3JkZjpSREY+IDwveDp4bXBtZXRhPiAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgIDw/eHBhY2tldCBlbmQ9InciPz7/2wBDAAMCAgMCAgMDAwMEAwMEBQgF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';
  uploadString(storageRef, imgBase64, 'base64').then((snapshot) => {
    console.log('Uploaded a base64 img!')
  });

  res.set(CONTENT_TYPE_JSON)
  res.send("")

})

app.get("/activity/:idUser/travels/:travelCount", async (req, res) =>{
  let travelCount = req.params.travelCount
  let idUser = req.params.idUser

  console.log("Retrieve activity content for user id: "+ idUser+",travelCount: ",travelCount)

  let resData = await db.one(SELECT_TRAVELS_FOR_ID_USER, idUser)
      .then(data => {
        console.log("Travels:", data)
        return JSON.stringify(data)
      })
      .catch(function (error) {
          console.log("Error: retrieve Travels ", error)
          return error
      })
  if(resData.code != undefined){ /* Response error */
    res.statusCode = 500
    res.set(CONTENT_TYPE_JSON)
    res.send(JSON.stringify({error_code: resData.code,error_msg: resData.message}))
  }

  res.set(CONTENT_TYPE_JSON)
  res.send(resData)

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

function _base64ToArrayBuffer(base64) {
    //var binary_string = window.atob(base64);
    var binary_string = Buffer.from(base64, 'base64').toString()
    var len = binary_string.length;
    var bytes = new Uint8Array(len);
    for (var i = 0; i < len; i++) {
        bytes[i] = binary_string.charCodeAt(i);
    }
    return bytes.buffer;
}